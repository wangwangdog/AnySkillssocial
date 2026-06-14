"""需求、服务、订单模型"""
import enum
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Enum, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class DemandStatus(str, enum.Enum):
    OPEN = "open"           # 招募中
    CLOSED = "closed"       # 已截止
    COMPLETED = "completed" # 已完成


class OrderStatus(str, enum.Enum):
    PENDING = "pending"         # 待接单
    CONFIRMED = "confirmed"     # 已确认
    IN_PROGRESS = "in_progress" # 服务中（已打卡）
    COMPLETED = "completed"     # 已完成（双方打卡结束）
    CANCELLED = "cancelled"     # 已取消


class Demand(Base):
    """需求发布"""
    __tablename__ = "demands"

    id = Column(Integer, primary_key=True, index=True)
    creator_id = Column(Integer, ForeignKey("users.id"), index=True)
    title = Column(String(200))
    description = Column(Text)
    skill_type = Column(String(50))
    budget = Column(Float, default=0)
    has_interview_bonus = Column(Boolean, default=False)  # 面试福利
    interview_bonus_amount = Column(Float, default=0)
    status = Column(Enum(DemandStatus), default=DemandStatus.OPEN)
    location = Column(String(200), default="")

    # 扩展字段
    contact_phone = Column(String(20), nullable=True)    # 联系手机(可选公开)
    images = Column(Text, default="[]")                  # JSON array 需求配图
    applicant_count = Column(Integer, default=0)          # 报名人数(冗余)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    deadline = Column(DateTime, nullable=True)

    creator = relationship("User", back_populates="demands")
    applications = relationship("Application", back_populates="demand")


class Application(Base):
    """需求报名"""
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, index=True)
    demand_id = Column(Integer, ForeignKey("demands.id"), index=True)
    applicant_id = Column(Integer, ForeignKey("users.id"), index=True)
    video_url = Column(String(500), default="")
    message = Column(String(500), default="")
    status = Column(String(20), default="pending")  # pending / approved / rejected
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    demand = relationship("Demand", back_populates="applications")


class Service(Base):
    """服务发布（服务广场）"""
    __tablename__ = "services"

    id = Column(Integer, primary_key=True, index=True)
    seller_id = Column(Integer, ForeignKey("users.id"), index=True)
    title = Column(String(200))
    description = Column(Text)
    skill_type = Column(String(50))
    price = Column(Float)
    cover_image = Column(String(500), default="")

    location = Column(String(200), default="")       # 服务地区
    city = Column(String(50), default="")            # 城市(用于筛选)
    duration = Column(String(50), default="")        # 服务时长 "2小时"/"全天"
    images = Column(Text, default="[]")              # 多图 JSON array
    view_count = Column(Integer, default=0)
    order_count = Column(Integer, default=0)

    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    seller = relationship("User", back_populates="services")
    time_slots = relationship("TimeSlot", back_populates="service", cascade="all, delete-orphan")


class Order(Base):
    """订单"""
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    order_no = Column(String(50), unique=True, index=True)
    order_type = Column(String(20))  # demand / service
    demand_id = Column(Integer, ForeignKey("demands.id"), nullable=True)
    service_id = Column(Integer, ForeignKey("services.id"), nullable=True)

    buyer_id = Column(Integer, ForeignKey("users.id"), index=True)
    seller_id = Column(Integer, ForeignKey("users.id"), index=True)

    amount = Column(Float)
    status = Column(Enum(OrderStatus), default=OrderStatus.PENDING)

    # 打卡
    buyer_checkin_time = Column(DateTime, nullable=True)
    seller_checkin_time = Column(DateTime, nullable=True)
    buyer_checkout_time = Column(DateTime, nullable=True)
    seller_checkout_time = Column(DateTime, nullable=True)
    buyer_checkin_photo = Column(String(500), nullable=True)
    seller_checkin_photo = Column(String(500), nullable=True)
    checkin_location = Column(String(200), nullable=True)

    # 结算
    settled_at = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    service = relationship("Service", foreign_keys=[service_id])
    demand = relationship("Demand", foreign_keys=[demand_id])
    buyer = relationship("User", foreign_keys=[buyer_id], back_populates="orders_as_buyer")
    seller = relationship("User", foreign_keys=[seller_id], back_populates="orders_as_seller")
    ratings = relationship("Rating", back_populates="order")

class Rating(Base):
    """订单评价"""
    __tablename__ = "ratings"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), index=True)
    rater_id = Column(Integer, ForeignKey("users.id"), index=True)  # who rated
    ratee_id = Column(Integer, ForeignKey("users.id"), index=True)  # who was rated
    score = Column(Integer, default=5)  # 1-5
    comment = Column(String(500), default="")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    order = relationship("Order", back_populates="ratings")
    rater = relationship("User", foreign_keys=[rater_id])
    ratee = relationship("User", foreign_keys=[ratee_id])

