"""优惠券模型"""
import enum
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Enum, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class CouponType(str, enum.Enum):
    DISCOUNT = "discount"    # 折扣券（满 100 减 20）
    PERCENT = "percent"     # 百分比券（9 折）
    FIXED = "fixed"         # 固定减免（减 10 元）


class CouponStatus(str, enum.Enum):
    AVAILABLE = "available"
    USED = "used"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


class Coupon(Base):
    """优惠券"""
    __tablename__ = "coupons"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # 基础信息
    code = Column(String(50), unique=True, index=True, nullable=False)  # 券码
    name = Column(String(100), nullable=False)                         # 名称
    description = Column(String(200), default="")                     # 描述
    
    # 类型和金额
    coupon_type = Column(Enum(CouponType), nullable=False)
    value = Column(Float, nullable=False)  # 金额或折扣（如 0.9 表示 9 折，20 表示减 20）
    
    # 使用条件
    min_amount = Column(Float, default=0)  # 最低消费金额
    max_discount = Column(Float, nullable=True)  # 最高优惠金额（百分比券用）
    
    # 范围
    skill_type = Column(String(50), nullable=True)  # 适用技能类型，None 表示全部
    service_id = Column(Integer, nullable=True)     # 指定服务 ID，None 表示全部
    
    # 数量
    total_count = Column(Integer, default=1)        # 总张数
    used_count = Column(Integer, default=0)         # 已使用数
    
    # 时间
    valid_from = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    valid_to = Column(DateTime, nullable=True)       # 过期时间
    
    # 创建者
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # 商家创建
    is_admin = Column(Boolean, default=False)        # 是否管理员创建（全平台）
    
    # 状态
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    # 关系
    user_coupons = relationship("UserCoupon", back_populates="coupon")


class UserCoupon(Base):
    """用户优惠券（领取记录）"""
    __tablename__ = "user_coupons"
    
    id = Column(Integer, primary_key=True, index=True)
    coupon_id = Column(Integer, ForeignKey("coupons.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    status = Column(Enum(CouponStatus), default=CouponStatus.AVAILABLE)
    used_at = Column(DateTime, nullable=True)
    used_order_id = Column(Integer, nullable=True)  # 使用的订单 ID
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    # 关系
    coupon = relationship("Coupon", back_populates="user_coupons")
    
    # 唯一约束：一个用户只能领一张（针对限领一张的券）
    __table_args__ = (
        # 这里可以根据需求添加唯一约束
    )
