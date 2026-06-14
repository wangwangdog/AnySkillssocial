"""添加 slot, coupon, chat 相关表

Revision ID: 0001
Revises: 
Create Date: 2026-05-24
"""
from alembic import op
import sqlalchemy as sa

revision = '0001'
down_revision = None


def upgrade() -> None:
    # 创建优惠券表
    op.create_table('coupons',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('code', sa.String(50), unique=True, nullable=False, index=True),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('description', sa.String(200)),
        sa.Column('coupon_type', sa.String(20), nullable=False),  # discount/percent/fixed
        sa.Column('value', sa.Float, nullable=False),
        sa.Column('min_amount', sa.Float, default=0),
        sa.Column('max_discount', sa.Float),
        sa.Column('skill_type', sa.String(50)),
        sa.Column('service_id', sa.Integer),
        sa.Column('total_count', sa.Integer, default=1),
        sa.Column('used_count', sa.Integer, default=0),
        sa.Column('valid_from', sa.DateTime),
        sa.Column('valid_to', sa.DateTime),
        sa.Column('creator_id', sa.Integer, sa.ForeignKey('users.id')),
        sa.Column('is_admin', sa.Boolean, default=False),
        sa.Column('is_active', sa.Boolean, default=True),
        sa.Column('created_at', sa.DateTime)
    )
    
    # 创建用户优惠券表
    op.create_table('user_coupons',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('coupon_id', sa.Integer, sa.ForeignKey('coupons.id'), nullable=False),
        sa.Column('user_id', sa.Integer, sa.ForeignKey('users.id'), nullable=False),
        sa.Column('status', sa.String(20), default='available'),  # available/used/expired
        sa.Column('used_at', sa.DateTime),
        sa.Column('used_order_id', sa.Integer),
        sa.Column('created_at', sa.DateTime)
    )
    
    # 创建时间槽表（预约）
    op.create_table('time_slots',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('service_id', sa.Integer, sa.ForeignKey('services.id'), nullable=False, index=True),
        sa.Column('seller_id', sa.Integer, sa.ForeignKey('users.id'), nullable=False, index=True),
        sa.Column('slot_date', sa.DateTime, nullable=False, index=True),
        sa.Column('start_time', sa.Time, nullable=False),
        sa.Column('end_time', sa.Time, nullable=False),
        sa.Column('status', sa.String(20), default='available'),  # available/booked/completed
        sa.Column('price', sa.Float),
        sa.Column('note', sa.String(200)),
        sa.Column('created_at', sa.DateTime),
        sa.Column('updated_at', sa.DateTime)
    )
    
    # 创建预约记录表
    op.create_table('bookings',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('slot_id', sa.Integer, sa.ForeignKey('time_slots.id'), nullable=False),
        sa.Column('buyer_id', sa.Integer, sa.ForeignKey('users.id'), nullable=False),
        sa.Column('status', sa.String(20), default='confirmed'),
        sa.Column('remark', sa.String(200)),
        sa.Column('created_at', sa.DateTime)
    )
    
    # 创建卖家工作时间表
    op.create_table('seller_schedules',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('seller_id', sa.Integer, sa.ForeignKey('users.id'), nullable=False),
        sa.Column('weekday_start', sa.Time),
        sa.Column('weekday_end', sa.Time),
        sa.Column('weekend_start', sa.Time),
        sa.Column('weekend_end', sa.Time),
        sa.Column('rest_days', sa.String(10)),  # 如 "1,3,5" 表示周一三五休息
        sa.Column('advance_days', sa.Integer, default=7),
        sa.Column('is_active', sa.Boolean, default=True),
        sa.Column('updated_at', sa.DateTime)
    )


def downgrade() -> None:
    # 反向迁移（删除表）
    op.drop_table('seller_schedules')
    op.drop_table('bookings')
    op.drop_table('time_slots')
    op.drop_table('user_coupons')
    op.drop_table('coupons')
