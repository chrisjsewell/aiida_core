# -*- coding: utf-8 -*-
# pylint: disable=invalid-name,no-member
"""Migrate the file repository to the new disk object store based implementation.

Revision ID: 1feaea71bd5a
Revises: 7536a82b2cc4
Create Date: 2020-10-01 15:05:49.271958

"""
from alembic import op
from sqlalchemy import Integer, cast
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import table, column

from aiida.backends.general.migrations import utils

# revision identifiers, used by Alembic.
revision = '1feaea71bd5a'
down_revision = '7536a82b2cc4'
branch_labels = None
depends_on = None


def upgrade():
    """Migrations for the upgrade."""
    connection = op.get_bind()

    DbNode = table(
        'db_dbnode',
        column('id', Integer),
        column('uuid', UUID),
        column('repository_metadata', JSONB),
    )

    mapping_node_repository_metadata = utils.migrate_legacy_repository()

    if mapping_node_repository_metadata is None:
        return

    for node_uuid, repository_metadata in mapping_node_repository_metadata.items():
        value = cast(repository_metadata, JSONB)
        connection.execute(DbNode.update().where(DbNode.c.uuid == node_uuid).values(repository_metadata=value))


def downgrade():
    """Migrations for the downgrade."""
