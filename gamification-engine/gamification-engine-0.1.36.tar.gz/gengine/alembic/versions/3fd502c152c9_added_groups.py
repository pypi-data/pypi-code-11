"""Added groups

Revision ID: 3fd502c152c9
Revises: 42ab7edc19e2
Create Date: 2015-03-31 14:48:03.675985

"""

# revision identifiers, used by Alembic.
revision = '3fd502c152c9'
down_revision = '42ab7edc19e2'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('groups',
    sa.Column('id', sa.BigInteger(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('users_groups',
    sa.Column('user_id', sa.BigInteger(), nullable=False),
    sa.Column('group_id', sa.BigInteger(), nullable=False),
    sa.ForeignKeyConstraint(['group_id'], ['groups.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('user_id', 'group_id')
    )
    op.create_index(op.f('ix_achievements_achievementcategory_id'), 'achievements', ['achievementcategory_id'], unique=False)
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_achievements_achievementcategory_id'), table_name='achievements')
    op.drop_table('users_groups')
    op.drop_table('groups')
    ### end Alembic commands ###
