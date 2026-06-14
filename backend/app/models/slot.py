"""预约排期模型"""
import enum
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Enum, Text, ForeignKey, Time
from sqlalchemy.orm import relationship
from app.core.database import Base


class SlotStatus(str, enum.Enum):
    AVAILABLE = "available"      # 可预约
    BOOKED = "booked"           # 已预订
    COMPLETED = "completed"     # 已完成
    CANCELLED = "cancelled"     # 已取消
    BLOCKED = "blocked"         # 不可用（休息/忙碌）


class TimeSlot(Base):
    """服务时间槽（按天创建）"""
    __tablename__ = "time_slots"
    
    id = Column(Integer, primary_key=True, index=True)
    service_id = Column(Integer, ForeignKey("services.id"), index=True, nullable=False)
    seller_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    
    # 日期和时间
    slot_date = Column(DateTime, nullable=False, index=True)  # 日期（UTC）
    start_time = Column(Time, nullable=False)                 # 开始时间
    end_time = Column(Time, nullable=False)                   # 结束时间
    
    # 状态
    status = Column(Enum(SlotStatus), default=SlotStatus.AVAILABLE)
    
    # 价格
    price = Column(Float, default=0.0)  # 可能有时段折扣
    
    # 备注
    note = Column(String(200), default="")  # 如"上午时段"、"周末特惠"
    
    # 时间
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # 关系
    service = relationship("Service", back_populates="time_slots")
    booking = relationship("Booking", back_populates="slot", uselist=False)


class Booking(Base):
    """预约订单"""
    __tablename__ = "bookings"
    
    id = Column(Integer, primary_key=True, index=True)
    slot_id = Column(Integer, ForeignKey("time_slots.id"), index=True, nullable=False)
    buyer_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    
    # 预约信息
    booking_time = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    status = Column(String(20), default="pending")  # pending / confirmed / cancelled / completed
    
    # 备注
    remark = Column(String(200), default="")
    
    # 时间
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    # 关系
    slot = relationship("TimeSlot", back_populates="booking")
    buyer = relationship("User", foreign_keys=[buyer_id])


class SellerSchedule(Base):
    """卖家工作时间表（模板）"""
    __tablename__ = "seller_schedules"
    
    id = Column(Integer, primary_key=True, index=True)
    seller_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    
    # 工作时段模板
    weekday_start = Column(Time, nullable=True)  # 周一至周五开始时间
    weekday_end = Column(Time, nullable=True)    # 周一至周五结束时间
    weekend_start = Column(Time, nullable=True)  # 周末开始时间
    weekend_end = Column(Time, nullable=True)    # 周末结束时间
    
    # 休息日
    rest_days = Column(String(10), default="")  # "1,3,5" 表示周一、三、五休息
    
    # 提前预约天数
    advance_days = Column(Integer, default=7)    # 可提前预约的天数
    
    is_active = Column(Boolean, default=True)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # 关系
    seller = relationship("User")


# 修改 Service 模型（如果存在的话）
# 需要在 order.py 或 services.py 中添加 time_slots 关系
