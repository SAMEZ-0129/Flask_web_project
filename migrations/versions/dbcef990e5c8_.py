"""empty message

Revision ID: dbcef990e5c8
Revises: ba7fd41b9072
Create Date: 2024-12-04 17:33:09.203257

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'dbcef990e5c8'
down_revision = 'ba7fd41b9072'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('answer', schema=None) as batch_op:
        batch_op.drop_column('votes')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('answer', schema=None) as batch_op:
        batch_op.add_column(sa.Column('votes', sa.INTEGER(), nullable=True))

    # ### end Alembic commands ###