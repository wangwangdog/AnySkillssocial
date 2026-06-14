"""用户与账户模型"""
import enum
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Enum, Text, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.core.database import Base


class MemberLevel(str, enum.Enum):
    FREE = "free"
    SILVER = "silver"
    GOLD = "gold"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    phone = Column(String(20), unique=True, index=True, nullable=True)
    nickname = Column(String(50), unique=True, index=True)
    avatar = Column(String(500), default="")
    bio = Column(Text, default="")
    photos = Column(Text, default="")  # JSON array of photo URLs
    password_hash = Column(String(200), nullable=False)

    # 实名认证
    real_name = Column(String(50), nullable=True)
    id_card = Column(String(20), nullable=True)
    id_card_front = Column(String(500), nullable=True)
    id_card_back = Column(String(500), nullable=True)
    face_photo = Column(String(500), nullable=True)
    is_verified = Column(Boolean, default=False)

    # 技能认证
    skill_type = Column(String(50), nullable=True)
    skill_cert = Column(String(500), nullable=True)
    skill_video = Column(String(500), nullable=True)
    is_skill_verified = Column(Boolean, default=False)

    # 人物展示字段
    gender = Column(String(10), nullable=True)          # male / female / other
    birth_date = Column(DateTime, nullable=True)        # 用于计算年龄
    height = Column(Integer, nullable=True)              # cm
    weight = Column(Integer, nullable=True)              # kg
    education = Column(String(50), nullable=True)        # 学历
    occupation = Column(String(100), nullable=True)      # 职业
    residence_city = Column(String(50), nullable=True)   # 居住城市
    hometown = Column(String(50), nullable=True)         # 籍贯
    tags = Column(Text, default="[]")                    # JSON array 个人标签
    online_status = Column(Boolean, default=False)       # 是否在线
    last_active_at = Column(DateTime, nullable=True)     # 最后活跃时间

    # 统计字段
    view_count = Column(Integer, default=0)              # 主页浏览数
    rating_avg = Column(Float, default=0.0)              # 综合评分
    completed_order_count = Column(Integer, default=0)   # 完成订单数
    follower_count = Column(Integer, default=0)          # 粉丝数
    following_count = Column(Integer, default=0)         # 关注数

    # 联系方式（付费可见）
    contact_phone = Column(String(20), nullable=True)     # 联系手机
    contact_qq = Column(String(20), nullable=True)        # QQ
    contact_wechat = Column(String(50), nullable=True)    # 微信
    contact_price = Column(Float, default=0)              # 查看联系方式价格

    # 会员
    member_level = Column(Enum(MemberLevel), default=MemberLevel.FREE)
    member_expire_at = Column(DateTime, nullable=True)

    # 账户
    cash_balance = Column(Float, default=0.0)      # 现金
    points_balance = Column(Float, default=0.0)    # 积分

    # 签到
    checkin_streak = Column(Integer, default=0)
    last_checkin_date = Column(String(10), nullable=True)
    daily_post_quota = Column(Integer, default=3)

    # 状态
    is_banned = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # 关系
    demands = relationship("Demand", back_populates="creator")
    orders_as_buyer = relationship("Order", foreign_keys="Order.buyer_id", back_populates="buyer")
    orders_as_seller = relationship("Order", foreign_keys="Order.seller_id", back_populates="seller")
    services = relationship("Service", back_populates="seller")
    albums = relationship("UserAlbum", back_populates="user", cascade="all, delete-orphan")
    articles = relationship("Article", back_populates="author", cascade="all, delete-orphan")


class CashFlow(Base):
    """现金流水"""
    __tablename__ = "cash_flows"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    amount = Column(Float)
    flow_type = Column(String(20))  # recharge / withdraw / payment / refund
    status = Column(String(20), default="pending")  # pending / completed / failed
    remark = Column(String(200), default="")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class UserPost(Base):
    """用户发布的动态"""
    __tablename__ = "user_posts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    content = Column(Text, nullable=False)
    images = Column(Text, default="[]")  # JSON array of image URLs
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    user = relationship("User", foreign_keys=[user_id])


class PointsFlow(Base):
    """积分流水"""
    __tablename__ = "points_flows"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    amount = Column(Float)
    flow_type = Column(String(20))  # earn / spend / withdraw
    status = Column(String(20), default="completed")
    remark = Column(String(200), default="")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class UserFavorite(Base):
    """用户收藏/关注"""
    __tablename__ = "user_favorites"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    item_type = Column(String(20))  # service / demand
    item_id = Column(Integer)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class UserAlbum(Base):
    """用户相册"""
    __tablename__ = "user_albums"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    url = Column(String(500), nullable=False)
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="albums")


class Article(Base):
    """文章内容：技能攻略 / 行业资讯 / 生活分享"""
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, index=True)
    author_id = Column(Integer, ForeignKey("users.id"), index=True)
    title = Column(String(200), nullable=False)
    summary = Column(String(500), default="")
    content = Column(Text, default="")
    cover_image = Column(String(500), default="")
    category = Column(String(50), default="guide")  # guide / news / lifestyle
    tags = Column(String(200), default="")  # 逗号分隔
    view_count = Column(Integer, default=0)
    like_count = Column(Integer, default=0)
    status = Column(String(20), default="draft")  # draft / published
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    author = relationship("User", back_populates="articles")


class Follow(Base):
    """关注关系（人与人）"""
    __tablename__ = "follows"

    id = Column(Integer, primary_key=True, index=True)
    follower_id = Column(Integer, ForeignKey("users.id"), index=True)
    followee_id = Column(Integer, ForeignKey("users.id"), index=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        UniqueConstraint('follower_id', 'followee_id', name='uq_follow_follower_followee'),
    )


class ContactPayment(Base):
    """联系方式付费解锁记录"""
    __tablename__ = "contact_payments"

    id = Column(Integer, primary_key=True, index=True)
    buyer_id = Column(Integer, ForeignKey("users.id"), index=True)
    seller_id = Column(Integer, ForeignKey("users.id"), index=True)
    amount = Column(Float, default=0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
