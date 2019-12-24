"""init

Revision ID: 89ada066a9e9
Revises: 
Create Date: 2019-12-24 17:01:52.808182

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '89ada066a9e9'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('meme',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=256), nullable=False),
    sa.Column('url', sa.String(length=65536), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('murmur',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('sentence', sa.String(length=65536), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('murmur')
    op.drop_table('meme')
    # ### end Alembic commands ###