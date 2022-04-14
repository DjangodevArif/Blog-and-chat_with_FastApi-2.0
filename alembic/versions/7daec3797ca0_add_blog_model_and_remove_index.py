"""[Add] blog model and remove index

Revision ID: 7daec3797ca0
Revises: 24158ae209eb
Create Date: 2021-11-26 22:57:47.442718

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7daec3797ca0'
down_revision = '0def36ed882f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('feed',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('user_id', sa.Integer(), nullable=True),
                    sa.Column('title', sa.String(length=80), nullable=True),
                    sa.Column('content', sa.String(), nullable=True),
                    sa.Column('timestamp', sa.DateTime(), nullable=True),
                    sa.Column('media', sa.JSON(), nullable=True),
                    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_table('comment',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('user_id', sa.Integer(), nullable=True),
                    sa.Column('feed_id', sa.Integer(), nullable=True),
                    sa.Column('content', sa.String(length=400), nullable=True),
                    sa.Column('timestamp', sa.DateTime(), nullable=True),
                    sa.ForeignKeyConstraint(['feed_id'], ['feed.id'], ),
                    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_table('reply',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('user_id', sa.Integer(), nullable=True),
                    sa.Column('comment_id', sa.Integer(), nullable=True),
                    sa.Column('content', sa.String(length=400), nullable=True),
                    sa.Column('timestamp', sa.DateTime(), nullable=True),
                    sa.ForeignKeyConstraint(['comment_id'], ['comment.id'], ),
                    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.drop_index('ix_privatechatroom_id', table_name='privatechatroom')
    op.drop_index('ix_roomchatmessage_id', table_name='roomchatmessage')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_index('ix_roomchatmessage_id',
                    'roomchatmessage', ['id'], unique=False)
    op.create_index('ix_privatechatroom_id',
                    'privatechatroom', ['id'], unique=False)
    op.drop_table('reply')
    op.drop_table('comment')
    op.drop_table('feed')
    # ### end Alembic commands ###
