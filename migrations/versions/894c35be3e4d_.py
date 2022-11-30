"""empty message

Revision ID: 894c35be3e4d
Revises: 35f09fb60359
Create Date: 2022-11-11 17:40:29.524341

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '894c35be3e4d'
down_revision = '35f09fb60359'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('course',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('label', sa.String(length=100), nullable=True),
    sa.Column('fk_session_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['fk_session_id'], ['session.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.add_column('subscription', sa.Column('fk_course_id', sa.Integer(), nullable=True))
    op.drop_constraint('subscription_fk_session_id_fkey', 'subscription', type_='foreignkey')
    op.drop_constraint('subscription_fk_level_id_fkey', 'subscription', type_='foreignkey')
    op.drop_constraint('subscription_fk_language_id_fkey', 'subscription', type_='foreignkey')
    op.create_foreign_key(None, 'subscription', 'course', ['fk_course_id'], ['id'])
    op.drop_column('subscription', 'fk_session_id')
    op.drop_column('subscription', 'fk_level_id')
    op.drop_column('subscription', 'fk_language_id')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('subscription', sa.Column('fk_language_id', sa.INTEGER(), autoincrement=False, nullable=True))
    op.add_column('subscription', sa.Column('fk_level_id', sa.INTEGER(), autoincrement=False, nullable=True))
    op.add_column('subscription', sa.Column('fk_session_id', sa.INTEGER(), autoincrement=False, nullable=True))
    op.drop_constraint(None, 'subscription', type_='foreignkey')
    op.create_foreign_key('subscription_fk_language_id_fkey', 'subscription', 'language', ['fk_language_id'], ['id'])
    op.create_foreign_key('subscription_fk_level_id_fkey', 'subscription', 'level', ['fk_level_id'], ['id'])
    op.create_foreign_key('subscription_fk_session_id_fkey', 'subscription', 'session', ['fk_session_id'], ['id'])
    op.drop_column('subscription', 'fk_course_id')
    op.drop_table('course')
    # ### end Alembic commands ###
