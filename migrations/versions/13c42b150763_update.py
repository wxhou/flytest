"""update

Revision ID: 13c42b150763
Revises: e6c1b4951b3f
Create Date: 2021-07-27 16:07:59.424310

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '13c42b150763'
down_revision = 'e6c1b4951b3f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('apscheduler_jobs', schema=None) as batch_op:
        batch_op.drop_index('ix_apscheduler_jobs_next_run_time')

    op.drop_table('apscheduler_jobs')
    with op.batch_alter_table('cron_tab_task', schema=None) as batch_op:
        batch_op.add_column(sa.Column('product_id', sa.Integer(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('cron_tab_task', schema=None) as batch_op:
        batch_op.drop_column('product_id')

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