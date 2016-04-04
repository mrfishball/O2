"""empty message

Revision ID: ac994e25e3cd
Revises: 31cc48533301
Create Date: 2016-03-05 03:32:30.145038

"""

# revision identifiers, used by Alembic.
revision = 'ac994e25e3cd'
down_revision = '31cc48533301'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table(u'snippet')
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table(u'snippet',
    sa.Column(u'id', sa.INTEGER(), nullable=False),
    sa.Column(u'title', sa.VARCHAR(length=100), nullable=True),
    sa.Column(u'slug', sa.VARCHAR(length=100), nullable=True),
    sa.Column(u'body', sa.TEXT(), nullable=True),
    sa.Column(u'status', sa.SMALLINT(), nullable=True),
    sa.Column(u'created_timestamp', sa.DATETIME(), nullable=True),
    sa.Column(u'modified_timestamp', sa.DATETIME(), nullable=True),
    sa.PrimaryKeyConstraint(u'id')
    )
    ### end Alembic commands ###