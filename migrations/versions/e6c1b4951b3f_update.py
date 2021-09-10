"""update

Revision ID: e6c1b4951b3f
Revises: ea6b030e3337
Create Date: 2021-07-27 14:43:56.029779

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'e6c1b4951b3f'
down_revision = 'ea6b030e3337'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('cron_tab_task',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('task_id', sa.String(length=256), nullable=True),
    sa.Column('func_name', sa.String(length=256), nullable=True),
    sa.Column('trigger', sa.String(length=64), nullable=True),
    sa.Column('args', sa.String(length=128), nullable=True),
    sa.Column('kwargs', sa.String(length=128), nullable=True),
    sa.Column('max_instances', sa.Integer(), nullable=True),
    sa.Column('times', sa.String(length=128), nullable=True),
    sa.Column('misfire_grace_time', sa.Integer(), nullable=True),
    sa.Column('next_run_time', sa.String(length=256), nullable=True),
    sa.Column('start_date', sa.String(length=256), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('cron_tab_task', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_cron_tab_task_task_id'), ['task_id'], unique=False)

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

    with op.batch_alter_table('cron_tab_task', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_cron_tab_task_task_id'))

    op.drop_table('cron_tab_task')
    # ### end Alembic commands ###