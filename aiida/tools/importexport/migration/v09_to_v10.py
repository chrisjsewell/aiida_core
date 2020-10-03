# -*- coding: utf-8 -*-
###########################################################################
# Copyright (c), The AiiDA team. All rights reserved.                     #
# This file is part of the AiiDA code.                                    #
#                                                                         #
# The code is hosted on GitHub at https://github.com/aiidateam/aiida-core #
# For further information on the license, see the LICENSE.txt file        #
# For further information please visit http://www.aiida.net               #
###########################################################################
"""Migration from v0.9 to v0.10, used by `verdi export migrate` command.

This migration deals with the file repository. In the old version, the
"""
import os
import shutil

from aiida.tools.importexport.migration.utils import verify_metadata_version, update_metadata


def migrate_repository(metadata, data, folder):
    """Migrate the file repository to a disk object store container."""
    from disk_objectstore import Container
    from aiida.repository import Repository
    from aiida.repository.backend import DiskObjectStoreRepositoryBackend

    container = Container(os.path.join(folder.abspath, 'container'))
    container.init_container()
    backend = DiskObjectStoreRepositoryBackend(container=container)
    repository = Repository(backend=backend)

    for values in data.get('export_data', {}).get('Node', {}).values():
        uuid = values['uuid']
        dirpath_calc = os.path.join(folder.abspath, 'nodes', uuid[:2], uuid[2:4], uuid[4:], 'raw_input')
        dirpath_data = os.path.join(folder.abspath, 'nodes', uuid[:2], uuid[2:4], uuid[4:], 'path')

        if os.path.isdir(dirpath_calc):
            dirpath = dirpath_calc
        elif os.path.isdir(dirpath_data):
            dirpath = dirpath_data
        else:
            raise AssertionError('node repository contains neither `raw_input` nor `path` subfolder.')

        if not os.listdir(dirpath):
            continue

        repository.put_object_from_tree(dirpath)
        values['repository_metadata'] = repository.serialize()
        # Reset the repository's virtual hierarchy to be empty
        repository.reset()

    container.pack_all_loose(compress=False)
    shutil.rmtree(os.path.join(folder.abspath, 'nodes'))

    metadata['all_fields_info']['Node']['repository_metadata'] = {}


def migrate_v9_to_v10(metadata, data, folder):  # pylint: disable=unused-argument
    """Migration of export files from v0.8 to v0.9."""
    old_version = '0.9'
    new_version = '0.10'

    verify_metadata_version(metadata, old_version)
    update_metadata(metadata, new_version)

    # Apply migrations
    migrate_repository(metadata, data, folder)
