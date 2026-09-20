"""initial_schema

Revision ID: 001_initial_schema
Revises: 
Create Date: 2026-09-20 12:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '001_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # user_levels
    op.create_table(
        'user_levels',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.BigInteger(), nullable=False),
        sa.Column('guild_id', sa.BigInteger(), nullable=False),
        sa.Column('xp', sa.BigInteger(), nullable=False),
        sa.Column('level', sa.BigInteger(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'guild_id', name='uq_user_guild_level')
    )
    op.create_index('ix_user_levels_user_id', 'user_levels', ['user_id'])
    op.create_index('ix_user_levels_guild_id', 'user_levels', ['guild_id'])

    # economy_accounts
    op.create_table(
        'economy_accounts',
        sa.Column('user_id', sa.BigInteger(), nullable=False),
        sa.Column('wallet', sa.BigInteger(), nullable=False),
        sa.Column('bank', sa.BigInteger(), nullable=False),
        sa.Column('last_daily', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('user_id')
    )

    # inventory_items
    op.create_table(
        'inventory_items',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.BigInteger(), nullable=False),
        sa.Column('item_id', sa.String(length=64), nullable=False),
        sa.Column('item_name', sa.String(length=128), nullable=False),
        sa.Column('category', sa.String(length=64), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'item_id', name='uq_user_item_inventory')
    )
    op.create_index('ix_inventory_items_user_id', 'inventory_items', ['user_id'])

    # guild_settings
    op.create_table(
        'guild_settings',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('guild_id', sa.BigInteger(), nullable=False),
        sa.Column('prefix', sa.String(length=10), nullable=False),
        sa.Column('welcome_enabled', sa.Boolean(), nullable=False),
        sa.Column('welcome_channel_id', sa.BigInteger(), nullable=True),
        sa.Column('welcome_message', sa.Text(), nullable=True),
        sa.Column('leave_enabled', sa.Boolean(), nullable=False),
        sa.Column('leave_channel_id', sa.BigInteger(), nullable=True),
        sa.Column('leave_message', sa.Text(), nullable=True),
        sa.Column('mod_role_id', sa.BigInteger(), nullable=True),
        sa.Column('mute_role_id', sa.BigInteger(), nullable=True),
        sa.Column('mod_log_channel_id', sa.BigInteger(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('guild_id')
    )
    op.create_index('ix_guild_settings_guild_id', 'guild_settings', ['guild_id'])

    # count_games
    op.create_table(
        'count_games',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('guild_id', sa.BigInteger(), nullable=False),
        sa.Column('channel_id', sa.BigInteger(), nullable=False),
        sa.Column('current_count', sa.Integer(), nullable=False),
        sa.Column('last_user_id', sa.BigInteger(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('guild_id', 'channel_id', name='uq_guild_channel_count')
    )
    op.create_index('ix_count_games_guild_id', 'count_games', ['guild_id'])
    op.create_index('ix_count_games_channel_id', 'count_games', ['channel_id'])

    # businesses
    op.create_table(
        'businesses',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('owner_id', sa.BigInteger(), nullable=False),
        sa.Column('name', sa.String(length=64), nullable=False),
        sa.Column('balance', sa.BigInteger(), nullable=False),
        sa.Column('company_value', sa.BigInteger(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    op.create_index('ix_businesses_owner_id', 'businesses', ['owner_id'])

    # products
    op.create_table(
        'products',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('business_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=64), nullable=False),
        sa.Column('price', sa.Integer(), nullable=False),
        sa.Column('level', sa.Integer(), nullable=False),
        sa.Column('num_manufactured', sa.Integer(), nullable=False),
        sa.Column('num_employees', sa.Integer(), nullable=False),
        sa.Column('time_to_make_one_product', sa.Integer(), nullable=False),
        sa.Column('last_sold_timestamp', sa.DateTime(timezone=True), nullable=True),
        sa.Column('total_sold', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['business_id'], ['businesses.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('business_id', 'name', name='uq_business_product_name')
    )


def downgrade() -> None:
    op.drop_table('products')
    op.drop_table('businesses')
    op.drop_table('count_games')
    op.drop_table('guild_settings')
    op.drop_table('inventory_items')
    op.drop_table('economy_accounts')
    op.drop_table('user_levels')
