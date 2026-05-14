"""add media_id to automations

Revision ID: bc7cd6a3411d
Revises: 001
Create Date: 2026-05-13 16:46:37.773959

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'bc7cd6a3411d'
down_revision: Union[str, None] = '001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('automations', sa.Column('media_id', sa.String(length=255), nullable=True))
    op.add_column('automations', sa.Column('media_url', sa.String(length=1000), nullable=True))


def downgrade() -> None:
    op.drop_column('automations', 'media_url')
    op.drop_column('automations', 'media_id')
