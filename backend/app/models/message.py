"""消息 & 通知模型"""
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Index
from sqlalchemy.orm import relationship
from app.core.database import Base


class Conversation(Base):
    """会话"""
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    # 发起方
    initiator_id = Column(Integer, ForeignKey("users.id"), index=True)
    # 接收方
    recipient_id = Column(Integer, ForeignKey("users.id"), index=True)
    last_message = Column(String(500), default="")
    last_time = Column(DateTime, nullable=True)
    initiator_unread = Column(Integer, default=0)
    recipient_unread = Column(Integer, default=0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    initiator = relationship("User", foreign_keys=[initiator_id])
    recipient = relationship("User", foreign_keys=[recipient_id])
    messages = relationship("Message", back_populates="conversation", order_by="Message.created_at")

    __table_args__ = (
        Index("ix_conversation_pair", "initiator_id", "recipient_id", unique=True),
    )


class Message(Base):
    """消息"""
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), index=True)
    sender_id = Column(Integer, ForeignKey("users.id"), index=True)
    content = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    conversation = relationship("Conversation", back_populates="messages")
    sender = relationship("User")


class Notification(Base):
    """系统通知"""
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    type = Column(String(20), default="system")  # system / order / message
    title = Column(String(200))
    content = Column(Text, default="")
    related_id = Column(Integer, nullable=True)  # 关联的订单/需求ID
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
