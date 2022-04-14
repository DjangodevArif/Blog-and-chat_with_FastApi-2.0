"""[MOD] datetime now 

Revision ID: ccbd1fa497ab
Revises: c7a185948b6c
Create Date: 2022-04-07 17:50:49.755089

"""
import datetime
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ccbd1fa497ab'
down_revision = 'c7a185948b6c'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column(table_name="roomchatmessage",
                    column_name="timestamp",
                    server_default=datetime.datetime.now(),
                    existing_server_default=datetime.datetime.utcnow(),
                    )
    # pass
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###