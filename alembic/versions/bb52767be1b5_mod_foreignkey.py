"""[MOD] foreignkey 

Revision ID: bb52767be1b5
Revises: d61611253d32
Create Date: 2021-09-05 16:40:08.572221

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'bb52767be1b5'
down_revision = 'd61611253d32'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_index(op.f('ix_roomchatmessage_id'), 'roomchatmessage', ['id'], unique=False)
    op.drop_constraint('roomchatmessage_user_fkey', 'roomchatmessage', type_='foreignkey')
    op.create_foreign_key(None, 'roomchatmessage', 'users', ['user'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'roomchatmessage', type_='foreignkey')
    op.create_foreign_key('roomchatmessage_user_fkey', 'roomchatmessage', 'users', ['user'], ['id'], ondelete='CASCADE')
    op.drop_index(op.f('ix_roomchatmessage_id'), table_name='roomchatmessage')
    # ### end Alembic commands ###
