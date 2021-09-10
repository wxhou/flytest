"""update

Revision ID: 6ae68afcce7d
Revises: d1090c9733eb
Create Date: 2021-07-21 16:13:32.765997

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '6ae68afcce7d'
down_revision = 'd1090c9733eb'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('apscheduler_jobs', schema=None) as batch_op:
        batch_op.drop_index('ix_apscheduler_jobs_next_run_time')

    op.drop_table('apscheduler_jobs')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('apscheduler_jobs',
    sa.Column('id', mysql.VARCHAR(length=191), nullable=False),
    sa.Column('next_run_time', mysql.DOUBLE(asdecimal=True), nullable=True),
    sa.Column('job_state', sa.BLOB(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    mysql_default_charset='utf8',
    mysql_engine='InnoDB'
    )
    with op.batch_alter_table('apscheduler_jobs', schema=None) as batch_op:
        batch_op.create_index('ix_apscheduler_jobs_next_run_time', ['next_run_time'], unique=False)

    # ### end Alembic commands ###
