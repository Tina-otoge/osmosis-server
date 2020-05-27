"""Fill accuracy where null

Revision ID: c96246e06259
Revises: daecf5a4da73
Create Date: 2020-05-27 03:31:24.649784

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c96246e06259'
down_revision = 'daecf5a4da73'
branch_labels = None
depends_on = None


def upgrade():
    op.execute('UPDATE score SET accuracy = 0 WHERE accuracy IS NULL')


def downgrade():
    pass
