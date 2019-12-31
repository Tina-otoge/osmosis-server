"""remove accuracy column

Revision ID: d49fa3ae3344
Revises: 2d303aab17e2
Create Date: 2019-12-30 16:01:57.704680

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd49fa3ae3344'
down_revision = '2d303aab17e2'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('score', schema=None) as batch_op:
        batch_op.drop_column('accuracy')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('score', schema=None) as batch_op:
        batch_op.add_column(sa.Column('accuracy', sa.FLOAT(), nullable=True))

    # ### end Alembic commands ###