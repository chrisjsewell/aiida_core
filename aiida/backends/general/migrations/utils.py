# -*- coding: utf-8 -*-
###########################################################################
# Copyright (c), The AiiDA team. All rights reserved.                     #
# This file is part of the AiiDA code.                                    #
#                                                                         #
# The code is hosted on GitHub at https://github.com/aiidateam/aiida-core #
# For further information on the license, see the LICENSE.txt file        #
# For further information please visit http://www.aiida.net               #
###########################################################################
# pylint: disable=invalid-name
"""Various utils that should be used during migrations and migrations tests because the AiiDA ORM cannot be used."""
import datetime
import functools
import io
import os
import pathlib
import re
import typing

import numpy
from disk_objectstore import Container
from disk_objectstore.utils import LazyOpener

from aiida.cmdline.utils import echo
from aiida.common import json
from aiida.repository.backend import AbstractRepositoryBackend
from aiida.repository.common import File, FileType
from aiida.repository.repository import Repository

ISOFORMAT_DATETIME_REGEX = re.compile(r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d+(\+\d{2}:\d{2})?$')
REGEX_SHARD_SUB_LEVEL = re.compile(r'^[0-9a-f]{2}$')
REGEX_SHARD_FINAL_LEVEL = re.compile(r'^[0-9a-f-]{32}$')


class LazyFile(File):
    """Subclass of `File` where `key` also allows `LazyOpener` in addition to a string."""

    def __init__(
        self,
        name: str = '',
        file_type: FileType = FileType.DIRECTORY,
        key: typing.Union[str, None, LazyOpener] = None,
        objects: typing.Dict[str, 'File'] = None
    ):
        # pylint: disable=super-init-not-called
        if not isinstance(name, str):
            raise TypeError('name should be a string.')

        if not isinstance(file_type, FileType):
            raise TypeError('file_type should be an instance of `FileType`.')

        if key is not None and not isinstance(key, (str, LazyOpener)):
            raise TypeError('key should be `None` or a string.')

        if objects is not None and any([not isinstance(obj, self.__class__) for obj in objects.values()]):
            raise TypeError('objects should be `None` or a dictionary of `File` instances.')

        if file_type == FileType.DIRECTORY and key is not None:
            raise ValueError('an object of type `FileType.DIRECTORY` cannot define a key.')

        if file_type == FileType.FILE and objects is not None:
            raise ValueError('an object of type `FileType.FILE` cannot define any objects.')

        self._name = name
        self._file_type = file_type
        self._key = key
        self._objects = objects or {}


class MigrationRepository(Repository):
    """Subclass of `Repository` that uses `LazyFile` instead of `File` as its file class."""

    _file_cls = LazyFile


class NoopRepositoryBackend(AbstractRepositoryBackend):
    """Implementation of the ``AbstractRepositoryBackend`` where all write operations are no-ops."""

    def put_object_from_filelike(self, handle: io.BufferedIOBase) -> str:
        """Store the byte contents of a file in the repository.

        :param handle: filelike object with the byte content to be stored.
        :return: the generated fully qualified identifier for the object within the repository.
        :raises TypeError: if the handle is not a byte stream.
        """
        return LazyOpener(handle.name)

    def has_object(self, key: str) -> bool:
        """Return whether the repository has an object with the given key.

        :param key: fully qualified identifier for the object within the repository.
        :return: True if the object exists, False otherwise.
        """
        raise NotImplementedError()


def migrate_legacy_repository():
    """Migrate the legacy file repository to the new disk object store and return mapping of repository metadata.

    The format of the return value will be a dictionary where the keys are the UUIDs of the nodes whose repository
    folder has contents have been migrated to the disk object store. The values are the repository metadata that contain
    the keys for the generated files with which the files in the disk object store can be retrieved. The format of the
    repository metadata follows exactly that of what is generated normally by the ORM.

    :return: mapping of node UUIDs onto the new repository metadata.
    """
    # pylint: disable=too-many-locals
    from aiida.manage.configuration import get_profile

    profile = get_profile()
    backend = NoopRepositoryBackend()
    container = profile.get_repository_container()
    repository = MigrationRepository(backend=backend)

    # Initialize the new container: don't go through the profile, because that will not check if it already exists
    filepath = pathlib.Path(profile.repository_path) / 'container'
    container = Container(filepath)

    if not container.is_initialised:
        raise RuntimeError(f'the container {filepath} already exists.')

    basepath = pathlib.Path(profile.repository_path) / 'repository' / 'node'

    if not basepath.is_dir():
        echo.echo_warning(f'could not find the repository basepath {basepath}: nothing to migrate')
        return

    node_repository_dirpaths = get_node_repository_dirpaths(basepath)

    filepaths = []
    streams = []
    mapping_metadata = {}

    for node_uuid, node_dirpath in node_repository_dirpaths.items():
        repository.put_object_from_tree(node_dirpath)
        metadata = serialize_repository(repository)
        mapping_metadata[node_uuid] = metadata
        for root, _, filenames in repository.walk():
            for filename in filenames:
                parts = list(pathlib.Path(root / filename).parts)
                filepaths.append((node_uuid, parts))
                streams.append(functools.reduce(lambda objects, part: objects['o'].get(part), parts, metadata)['k'])

        # Reset the repository to a clean node repository, which removes the internal virtual file hierarchy
        repository.reset()

    hashkeys = container.add_streamed_objects_to_pack(streams, compress=True, open_streams=True)

    # Regroup by node UUID
    for hashkey, (node_uuid, parts) in zip(hashkeys, filepaths):
        repository_metadata = mapping_metadata[node_uuid]
        filename = parts.pop()
        file_object = repository_metadata['o']
        for part in parts:
            file_object = file_object[part]['o']
        file_object[filename]['k'] = hashkey

    return mapping_metadata


def get_node_repository_dirpaths(basepath):
    """Return a mapping of node UUIDs onto the path to their current repository folder in the old repository.

    :return: dictionary of node UUID onto absolute filepath
    """
    mapping = {}

    for shard_one in basepath.iterdir():

        if not REGEX_SHARD_SUB_LEVEL.match(shard_one.name):
            continue

        for shard_two in shard_one.iterdir():

            if not REGEX_SHARD_SUB_LEVEL.match(shard_two.name):
                continue

            for shard_three in shard_two.iterdir():

                if not REGEX_SHARD_FINAL_LEVEL.match(shard_three.name):
                    continue

                uuid = shard_one.name + shard_two.name + shard_three.name
                dirpath = basepath / shard_one / shard_two / shard_three
                subdirs = [path.name for path in dirpath.iterdir()]

                if 'path' in subdirs:
                    path = dirpath / 'path'
                elif 'raw_input' in subdirs:
                    path = dirpath / 'raw_input'
                else:
                    echo.echo_warning(
                        f'skipping node repository folder {dirpath} as it does not contain `path` nor `raw_input`'
                    )

                mapping[uuid] = path

    return mapping


def serialize_repository(repository: Repository) -> dict:
    """Serialize the metadata into a JSON-serializable format.

    .. note:: the serialization format is optimized to reduce the size in bytes.

    :return: dictionary with the content metadata.
    """
    file_object = repository._directory  # pylint: disable=protected-access
    if file_object.file_type == FileType.DIRECTORY:
        if file_object.objects:
            return {'o': {key: obj.serialize() for key, obj in file_object.objects.items()}}
        return {}
    return {'k': file_object.key}


def ensure_repository_folder_created(uuid):
    """Make sure that the repository sub folder for the node with the given UUID exists or create it.

    :param uuid: UUID of the node
    """
    dirpath = get_node_repository_sub_folder(uuid)
    os.makedirs(dirpath, exist_ok=True)


def put_object_from_string(uuid, name, content):
    """Write a file with the given content in the repository sub folder of the given node.

    :param uuid: UUID of the node
    :param name: name to use for the file
    :param content: the content to write to the file
    """
    ensure_repository_folder_created(uuid)
    basepath = get_node_repository_sub_folder(uuid)
    dirname = os.path.dirname(name)

    if dirname:
        os.makedirs(os.path.join(basepath, dirname), exist_ok=True)

    filepath = os.path.join(basepath, name)

    with open(filepath, 'w', encoding='utf-8') as handle:
        handle.write(content)


def get_object_from_repository(uuid, name):
    """Return the content of a file with the given name in the repository sub folder of the given node.

    :param uuid: UUID of the node
    :param name: name to use for the file
    """
    filepath = os.path.join(get_node_repository_sub_folder(uuid), name)

    with open(filepath) as handle:
        return handle.read()


def get_node_repository_sub_folder(uuid):
    """Return the absolute path to the sub folder `path` within the repository of the node with the given UUID.

    :param uuid: UUID of the node
    :return: absolute path to node repository folder, i.e `/some/path/repository/node/12/ab/c123134-a123/path`
    """
    from aiida.manage.configuration import get_profile

    uuid = str(uuid)

    repo_dirpath = os.path.join(get_profile().repository_path, 'repository')
    node_dirpath = os.path.join(repo_dirpath, 'node', uuid[:2], uuid[2:4], uuid[4:], 'path')

    return node_dirpath


def get_numpy_array_absolute_path(uuid, name):
    """Return the absolute path of a numpy array with the given name in the repository of the node with the given uuid.

    :param uuid: the UUID of the node
    :param name: the name of the numpy array
    :return: the absolute path of the numpy array file
    """
    return os.path.join(get_node_repository_sub_folder(uuid), f'{name}.npy')


def store_numpy_array_in_repository(uuid, name, array):
    """Store a numpy array in the repository folder of a node.

    :param uuid: the node UUID
    :param name: the name under which to store the array
    :param array: the numpy array to store
    """
    ensure_repository_folder_created(uuid)
    filepath = get_numpy_array_absolute_path(uuid, name)

    with open(filepath, 'wb') as handle:
        numpy.save(handle, array)


def delete_numpy_array_from_repository(uuid, name):
    """Delete the numpy array with a given name from the repository corresponding to a node with a given uuid.

    :param uuid: the UUID of the node
    :param name: the name of the numpy array
    """
    filepath = get_numpy_array_absolute_path(uuid, name)

    try:
        os.remove(filepath)
    except (IOError, OSError):
        pass


def load_numpy_array_from_repository(uuid, name):
    """Load and return a numpy array from the repository folder of a node.

    :param uuid: the node UUID
    :param name: the name under which to store the array
    :return: the numpy array
    """
    filepath = get_numpy_array_absolute_path(uuid, name)
    return numpy.load(filepath)


def recursive_datetime_to_isoformat(value):
    """Convert all datetime objects in the given value to string representations in ISO format.

    :param value: a mapping, sequence or single value optionally containing datetime objects
    """
    if isinstance(value, list):
        return [recursive_datetime_to_isoformat(_) for _ in value]

    if isinstance(value, dict):
        return dict((key, recursive_datetime_to_isoformat(val)) for key, val in value.items())

    if isinstance(value, datetime.datetime):
        return value.isoformat()

    return value


def dumps_json(dictionary):
    """Transforms all datetime object into isoformat and then returns the JSON."""
    return json.dumps(recursive_datetime_to_isoformat(dictionary))


def get_duplicate_uuids(table):
    """Retrieve rows with duplicate UUIDS.

    :param table: database table with uuid column, e.g. 'db_dbnode'
    :return: list of tuples of (id, uuid) of rows with duplicate UUIDs
    """
    from aiida.manage.manager import get_manager
    backend = get_manager().get_backend()
    return backend.query_manager.get_duplicate_uuids(table=table)


def verify_uuid_uniqueness(table):
    """Check whether database table contains rows with duplicate UUIDS.

    :param table: Database table with uuid column, e.g. 'db_dbnode'
    :type str:

    :raises: IntegrityError if table contains rows with duplicate UUIDS.
    """
    from aiida.common import exceptions
    duplicates = get_duplicate_uuids(table=table)

    if duplicates:
        raise exceptions.IntegrityError(
            'Table {table:} contains rows with duplicate UUIDS: run '
            '`verdi database integrity detect-duplicate-uuid -t {table:}` to address the problem'.format(table=table)
        )


def apply_new_uuid_mapping(table, mapping):
    """Take a mapping of pks to UUIDs and apply it to the given table.

    :param table: database table with uuid column, e.g. 'db_dbnode'
    :param mapping: dictionary of UUIDs mapped onto a pk
    """
    from aiida.manage.manager import get_manager
    backend = get_manager().get_backend()
    backend.query_manager.apply_new_uuid_mapping(table, mapping)


def deduplicate_uuids(table=None):
    """Detect and solve entities with duplicate UUIDs in a given database table.

    Before aiida-core v1.0.0, there was no uniqueness constraint on the UUID column of the node table in the database
    and a few other tables as well. This made it possible to store multiple entities with identical UUIDs in the same
    table without the database complaining. This bug was fixed in aiida-core=1.0.0 by putting an explicit uniqueness
    constraint on UUIDs on the database level. However, this would leave databases created before this patch with
    duplicate UUIDs in an inconsistent state. This command will run an analysis to detect duplicate UUIDs in a given
    table and solve it by generating new UUIDs. Note that it will not delete or merge any rows.

    :return: list of strings denoting the performed operations
    :raises ValueError: if the specified table is invalid
    """
    import distutils.dir_util
    from collections import defaultdict

    from aiida.common.utils import get_new_uuid

    mapping = defaultdict(list)

    for pk, uuid in get_duplicate_uuids(table=table):
        mapping[uuid].append(int(pk))

    messages = []
    mapping_new_uuid = {}

    for uuid, rows in mapping.items():

        uuid_ref = None

        for pk in rows:

            # We don't have to change all rows that have the same UUID, the first one can keep the original
            if uuid_ref is None:
                uuid_ref = uuid
                continue

            uuid_new = str(get_new_uuid())
            mapping_new_uuid[pk] = uuid_new

            messages.append(f'updated UUID of {table} row<{pk}> from {uuid_ref} to {uuid_new}')
            dirpath_repo_ref = get_node_repository_sub_folder(uuid_ref)
            dirpath_repo_new = get_node_repository_sub_folder(uuid_new)

            # First make sure the new repository exists, then copy the contents of the ref into the new. We use the
            # somewhat unknown `distuitils.dir_util` method since that does just contents as we want.
            os.makedirs(dirpath_repo_new, exist_ok=True)
            distutils.dir_util.copy_tree(dirpath_repo_ref, dirpath_repo_new)

    apply_new_uuid_mapping(table, mapping_new_uuid)

    if not messages:
        messages = ['no duplicate UUIDs found']

    return messages
