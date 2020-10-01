# -*- coding: utf-8 -*-
###########################################################################
# Copyright (c), The AiiDA team. All rights reserved.                     #
# This file is part of the AiiDA code.                                    #
#                                                                         #
# The code is hosted on GitHub at https://github.com/aiidateam/aiida-core #
# For further information on the license, see the LICENSE.txt file        #
# For further information please visit http://www.aiida.net               #
###########################################################################
# pylint: disable=invalid-name,too-few-public-methods
"""Migrate the file repository to the new disk object store based implementation."""
# pylint: disable=no-name-in-module,import-error
from django.core.exceptions import ObjectDoesNotExist
from django.db import migrations

from aiida.backends.djsite.db.migrations import upgrade_schema_version
from aiida.backends.general.migrations import utils
from aiida.cmdline.utils import echo

REVISION = '1.0.47'
DOWN_REVISION = '1.0.46'


def migrate_repository(apps, _):
    """Migrate the repository."""
    DbNode = apps.get_model('db', 'DbNode')

    mapping_node_repository_metadata = utils.migrate_legacy_repository()

    if mapping_node_repository_metadata is None:
        return

    for node_uuid, repository_metadata in mapping_node_repository_metadata.items():
        try:
            node = DbNode.objects.get(uuid=node_uuid)
        except ObjectDoesNotExist:
            echo.echo_warning(f'repo contained folder for Node<{node_uuid}>, but the node does not exist, skipping.')
        else:
            node.repository_metadata = repository_metadata
            node.save()


class Migration(migrations.Migration):
    """Migrate the file repository to the new disk object store based implementation."""

    dependencies = [
        ('db', '0046_add_node_repository_metadata'),
    ]

    operations = [
        migrations.RunPython(migrate_repository, reverse_code=migrations.RunPython.noop),
        upgrade_schema_version(REVISION, DOWN_REVISION),
    ]
