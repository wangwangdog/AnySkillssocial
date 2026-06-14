"""服务广场 API"""
import json
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import desc
from datetime import datetime, timezone
from app.core.database import get_db
from app.core.security import get_current_user, get_current_user_optional
from app.models.user import User
from app.models.order import Service, Order, OrderStatus, Rating

router = APIRouter(prefix="/api/services", tags=["服务"])


class CreateServiceRequest(BaseModel):
    title: str
    description: str
    skill_type: str
    price: float
    cover_image: str = ""
    location: str = ""
    city: str = ""
    duration: str = ""
    images: list[str] = []


@router.post("")
def create_service(req: CreateServiceRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    svc = Service(
        seller_id=user.id,
        title=req.title,
        description=req.description,
        skill_type=req.skill_type,
        price=req.price,
        cover_image=req.cover_image,
        location=req.location,
        city=req.city,
        duration=req.duration,
        images=json.dumps(req.images[:9]),
    )
    db.add(svc)
    db.commit()
    db.refresh(svc)
    return {"id": svc.id, "title": svc.title}


@router.get("")
def list_services(
    skill_type: str = "",
    city: str = "",
    price_min: float = 0,
    price_max: float = 0,
    gender: str = "",
    sort_by: str = "newest",   # newest / price_asc / price_desc / popular
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    query = db.query(Service).filter(Service.is_active == True)

    if skill_type:
        query = query.filter(Service.skill_type == skill_type)
    if city:
        query = query.filter(Service.city == city)
    if price_min > 0:
        query = query.filter(Service.price >= price_min)
    if price_max > 0:
        query = query.filter(Service.price <= price_max)
    if gender:
        query = query.join(User, Service.seller_id == User.id).filter(User.gender == gender)

    # 排序
    if sort_by == "price_asc":
        query = query.order_by(Service.price.asc())
    elif sort_by == "price_desc":
        query = query.order_by(Service.price.desc())
    elif sort_by == "popular":
        query = query.order_by(Service.order_count.desc(), Service.view_count.desc())
    else:
        query = query.order_by(Service.created_at.desc())

    total = query.count()
    services = query.offset((page - 1) * page_size).limit(page_size).all()

    # 计算每个卖家的评分
    def seller_rating(seller_id):
        ratings = db.query(Rating).filter(
            Rating.ratee_id == seller_id
        ).all()
        if ratings:
            avg = sum(r.score for r in ratings) / len(ratings)
            return round(avg, 1), len(ratings)
        return 0.0, 0

    return {
        "total": total,
        "page": page,
        "data": [{
            "id": s.id,
            "title": s.title,
            "description": s.description[:100] if s.description else "",
            "skill_type": s.skill_type,
            "price": s.price,
            "cover_image": s.cover_image,
            "location": s.location or "",
            "city": s.city or "",
            "duration": s.duration or "",
            "order_count": s.order_count or 0,
            "seller": {
                "id": s.seller.id,
                "nickname": s.seller.nickname,
                "avatar": s.seller.avatar or "",
                "gender": s.seller.gender or "",
                "residence_city": s.seller.residence_city or "",
                "birth_date": s.seller.birth_date.isoformat() if s.seller.birth_date else None,
            },
            "seller_nickname": s.seller.nickname,
            "seller_rating_avg": seller_rating(s.seller.id)[0],
            "seller_rating_count": seller_rating(s.seller.id)[1],
            "created_at": s.created_at.isoformat(),
        } for s in services],
    }


@router.get("/{service_id}")
def get_service(service_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user_optional)):
    svc = db.query(Service).filter(Service.id == service_id).first()
    if not svc:
        raise HTTPException(status_code=404, detail="服务不存在")

    # 增加浏览量
    svc.view_count = (svc.view_count or 0) + 1
    db.commit()

    # 卖家评分
    ratings = db.query(Rating).filter(Rating.ratee_id == svc.seller_id).all()
    rating_avg = round(sum(r.score for r in ratings) / len(ratings), 1) if ratings else 0.0

    # 最近的评价
    recent_ratings = db.query(Rating).filter(
        Rating.order_id.in_(
            db.query(Order.id).filter(Order.seller_id == svc.seller_id, Order.status == OrderStatus.COMPLETED)
        )
    ).order_by(Rating.created_at.desc()).limit(5).all()

    # 检查是否已被预约（存在非取消/完成的订单）
    active_order = db.query(Order).filter(
        Order.service_id == service_id,
        Order.status.in_([OrderStatus.CONFIRMED, OrderStatus.IN_PROGRESS]),
    ).first()
    is_booked = active_order is not None
    is_self_order = False
    if current_user and active_order:
        is_self_order = active_order.buyer_id == current_user.id or active_order.seller_id == current_user.id

    return {
        "id": svc.id,
        "title": svc.title,
        "description": svc.description,
        "skill_type": svc.skill_type,
        "price": svc.price,
        "cover_image": svc.cover_image,
        "location": svc.location or "",
        "city": svc.city or "",
        "duration": svc.duration or "",
        "images": json.loads(svc.images) if svc.images else [],
        "view_count": svc.view_count or 0,
        "order_count": svc.order_count or 0,
        "is_booked": is_booked,
        "is_self_order": is_self_order,
        "order_id": active_order.id if active_order and is_self_order else None,
        "seller": {
            "id": svc.seller.id,
            "nickname": svc.seller.nickname,
            "avatar": svc.seller.avatar or "",
            "gender": svc.seller.gender or "",
            "residence_city": svc.seller.residence_city or "",
            "birth_date": svc.seller.birth_date.isoformat() if svc.seller.birth_date else None,
            "bio": svc.seller.bio or "",
            "is_verified": svc.seller.is_verified,
            "is_skill_verified": svc.seller.is_skill_verified,
        },
        "seller_rating_avg": rating_avg,
        "seller_rating_count": len(ratings),
        "seller_service_count": db.query(Service).filter(
            Service.seller_id == svc.seller_id, Service.is_active == True
        ).count(),
        "ratings": [{
            "id": r.id,
            "score": r.score,
            "comment": r.comment or "",
            "rater_nickname": r.rater.nickname if r.rater else "",
            "rater_avatar": r.rater.avatar or "" if r.rater else "",
            "created_at": r.created_at.isoformat(),
        } for r in recent_ratings],
        "created_at": svc.created_at.isoformat(),
    }
