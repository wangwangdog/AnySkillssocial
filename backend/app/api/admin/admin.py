"""后台管理/数据统计 API"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from sqlalchemy.sql import func as sql_func
from datetime import datetime, timezone, timedelta
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User, MemberLevel, UserPost
from app.models.order import Order, OrderStatus, Service, Demand
import json

router = APIRouter(prefix="/api/admin", tags=["管理"])


def require_admin(user: User = Depends(get_current_user)):
    """管理员权限检查（临时：ID=1 为管理员）"""
    if user.id != 1:  # TODO: 添加 is_admin 字段
        raise HTTPException(403, "需要管理员权限")
    return user


@router.get("/stats/overview")
def get_overview(user: User = Depends(require_admin), db: Session = Depends(get_db)):
    """数据总览"""
    # 用户统计
    total_users = db.query(User).count()
    today_users = db.query(User).filter(
        sql_func.date(User.created_at) == sql_func.date(datetime.now(timezone.utc))
    ).count()
    
    # 订单统计
    total_orders = db.query(Order).count()
    today_orders = db.query(Order).filter(
        sql_func.date(Order.created_at) == sql_func.date(datetime.now(timezone.utc))
    ).count()
    completed_orders = db.query(Order).filter(Order.status == OrderStatus.COMPLETED).count()
    
    # 服务统计
    total_services = db.query(Service).filter(Service.is_active == True).count()
    total_demands = db.query(Demand).count()
    
    # 今日收入（完成订单的总金额）
    today_revenue = db.query(func.sum(Order.amount)).filter(
        Order.status == OrderStatus.COMPLETED,
        sql_func.date(Order.settled_at) == sql_func.date(datetime.now(timezone.utc))
    ).scalar() or 0
    
    return {
        "users": {
            "total": total_users,
            "today": today_users
        },
        "orders": {
            "total": total_orders,
            "today": today_orders,
            "completed": completed_orders
        },
        "services": {
            "active": total_services,
            "demands": total_demands
        },
        "revenue": {
            "today": today_revenue
        }
    }


@router.get("/stats/orders/trend")
def get_order_trend(
    days: int = 30,
    user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """订单趋势（最近 N 天）"""
    start_date = datetime.now(timezone.utc) - timedelta(days=days)
    
    # 按天聚合
    daily = db.query(
        date(Order.created_at).label("date"),
        func.count(Order.id).label("count"),
        func.sum(Order.amount).label("amount")
    ).filter(
        Order.created_at >= start_date
    ).group_by(
        sql_func.date(Order.created_at)
    ).order_by(
        sql_func.date(Order.created_at).desc()
    ).all()
    
    return {
        "data": [{
            "date": d.date.isoformat(),
            "count": d.count,
            "amount": d.amount or 0
        } for d in daily]
    }


@router.get("/stats/users/list")
def get_user_list(
    page: int = 1,
    page_size: int = 20,
    user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """用户列表"""
    total = db.query(User).count()
    users = db.query(User).order_by(User.created_at.desc()).offset((page-1)*page_size).limit(page_size).all()
    
    return {
        "total": total,
        "page": page,
        "data": [{
            "id": u.id,
            "nickname": u.nickname,
            "phone": u.phone,
            "is_verified": u.is_verified,
            "member_level": u.member_level.value,
            "cash_balance": u.cash_balance,
            "points_balance": u.points_balance,
            "created_at": u.created_at.isoformat()
        } for u in users]
    }


@router.post("/users/ban/{user_id}")
def ban_user(
    user_id: int,
    reason: str = "",
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """封禁用户"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(404, "用户不存在")
    
    user.is_banned = True
    db.commit()
    
    return {"status": "banned", "reason": reason}


@router.post("/users/unban/{user_id}")
def unban_user(
    user_id: int,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """解封用户"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(404, "用户不存在")
    
    user.is_banned = False
    db.commit()
    
    return {"status": "unbanned"}


@router.get("/orders/list")
def get_orders(
    status: str = "",
    page: int = 1,
    page_size: int = 20,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """订单列表"""
    query = db.query(Order)
    if status:
        query = query.filter(Order.status == OrderStatus(status))
    
    total = query.count()
    orders = query.order_by(Order.created_at.desc()).offset((page-1)*page_size).limit(page_size).all()
    
    return {
        "total": total,
        "page": page,
        "data": [{
            "id": o.id,
            "order_no": o.order_no,
            "buyer": {"id": o.buyer_id, "nickname": o.buyer.nickname},
            "seller": {"id": o.seller_id, "nickname": o.seller.nickname},
            "amount": o.amount,
            "status": o.status.value,
            "created_at": o.created_at.isoformat()
        } for o in orders]
    }


# ==================== 内容管理 ====================


@router.get("/services/pending")
def get_pending_services(
    page: int = 1,
    page_size: int = 20,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """待审核服务列表"""
    query = db.query(Service).filter(Service.is_active == False)
    total = query.count()
    services = query.order_by(Service.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return {
        "total": total,
        "page": page,
        "data": [{
            "id": s.id,
            "title": s.title,
            "description": s.description,
            "skill_type": s.skill_type,
            "price": s.price,
            "seller": {"id": s.seller_id, "nickname": s.seller.nickname if s.seller else ""},
            "created_at": s.created_at.isoformat()
        } for s in services]
    }


@router.post("/services/approve/{service_id}")
def approve_service(
    service_id: int,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """通过服务审核"""
    svc = db.query(Service).filter(Service.id == service_id).first()
    if not svc:
        raise HTTPException(404, "服务不存在")
    svc.is_active = True
    db.commit()
    return {"status": "approved"}


@router.post("/services/reject/{service_id}")
def reject_service(
    service_id: int,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """拒绝服务审核"""
    svc = db.query(Service).filter(Service.id == service_id).first()
    if not svc:
        raise HTTPException(404, "服务不存在")
    db.delete(svc)
    db.commit()
    return {"status": "rejected"}


@router.get("/posts/list")
def get_all_posts(
    page: int = 1,
    page_size: int = 20,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """用户动态列表（含发布者信息）"""
    query = db.query(UserPost).join(User, UserPost.user_id == User.id)
    total = query.count()
    posts = query.order_by(UserPost.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return {
        "total": total,
        "page": page,
        "data": [{
            "id": p.id,
            "content": p.content,
            "images": json.loads(p.images) if p.images else [],
            "author": {"id": p.user.id, "nickname": p.user.nickname, "avatar": p.user.avatar or ""},
            "created_at": p.created_at.isoformat()
        } for p in posts]
    }


@router.delete("/posts/{post_id}")
def delete_post(
    post_id: int,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """删除用户动态"""
    post = db.query(UserPost).filter(UserPost.id == post_id).first()
    if not post:
        raise HTTPException(404, "动态不存在")
    db.delete(post)
    db.commit()
    return {"status": "deleted"}
