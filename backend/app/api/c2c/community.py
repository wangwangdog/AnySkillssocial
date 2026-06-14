"""社区动态 API"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import union, desc
from app.core.database import get_db
from app.models.user import User, UserPost
from app.models.order import Service, Demand, Order, OrderStatus, Rating

router = APIRouter(prefix="/api/community", tags=["社区"])


@router.get("/feed")
def get_feed(page: int = 1, page_size: int = 20, db: Session = Depends(get_db)):
    """聚合社区动态：新服务、新需求、完成订单、新用户"""
    offset = (page - 1) * page_size
    limit = page_size

    import json
    from datetime import datetime, timezone

    activities = []

    # 新服务
    for s in db.query(Service).filter(Service.is_active == True).order_by(Service.created_at.desc()).limit(limit).all():
        activities.append({
            "type": "service",
            "user_id": s.seller_id,
            "user_nickname": s.seller.nickname,
            "user_avatar": s.seller.avatar or "",
            "title": s.title,
            "content": f"发布了新服务「{s.title}」¥{s.price:.0f}",
            "detail": s.description[:100] if s.description else "",
            "item_id": s.id,
            "skill_type": s.skill_type,
            "price": s.price,
            "created_at": s.created_at.isoformat(),
        })

    # 新需求
    for d in db.query(Demand).order_by(Demand.created_at.desc()).limit(limit).all():
        activities.append({
            "type": "demand",
            "user_id": d.creator_id,
            "user_nickname": d.creator.nickname,
            "user_avatar": d.creator.avatar or "",
            "title": d.title,
            "content": f"发布了新需求「{d.title}」预算¥{d.budget:.0f}",
            "detail": d.description[:100] if d.description else "",
            "item_id": d.id,
            "skill_type": d.skill_type,
            "budget": d.budget,
            "created_at": d.created_at.isoformat(),
        })

    # 完成的订单（含评价）
    for o in db.query(Order).filter(Order.status == OrderStatus.COMPLETED).order_by(Order.updated_at.desc()).limit(limit).all():
        rating_text = ""
        if o.ratings:
            r = o.ratings[0]
            rating_text = f" ⭐{'⭐'* (r.score-1)} {r.score}分"
            if r.comment:
                rating_text += f" 「{r.comment[:30]}」"

        svc_name = o.service.title if o.service else (o.demand.title if o.demand else "订单")
        activities.append({
            "type": "completed",
            "user_id": o.seller_id,
            "user_nickname": o.seller.nickname,
            "user_avatar": o.seller.avatar or "",
            "title": f"订单完成 {svc_name}",
            "content": f"完成了服务「{svc_name}」¥{o.amount:.0f}{rating_text}",
            "detail": "",
            "order_id": o.id,
            "rating_score": o.ratings[0].score if o.ratings else None,
            "rating_comment": o.ratings[0].comment if o.ratings else None,
            "created_at": (o.updated_at or o.created_at).isoformat(),
        })

    # 用户动态
    for p in db.query(UserPost).order_by(UserPost.created_at.desc()).limit(limit).all():
        import json
        images = json.loads(p.images) if p.images else []
        activities.append({
            "type": "post",
            "user_id": p.user_id,
            "user_nickname": p.user.nickname,
            "user_avatar": p.user.avatar or "",
            "title": "新动态",
            "content": p.content[:200],
            "detail": "",
            "images": images[:3],  # Show up to 3 images in feed
            "post_id": p.id,
            "created_at": p.created_at.isoformat(),
        })

    # 新用户
    for u in db.query(User).order_by(User.created_at.desc()).limit(limit).all():
        activities.append({
            "type": "new_user",
            "user_id": u.id,
            "user_nickname": u.nickname,
            "user_avatar": u.avatar or "",
            "title": "新伙伴加入",
            "content": f"新成员 {u.nickname} 加入了SkillGate",
            "detail": u.bio[:100] if u.bio else "",
            "created_at": u.created_at.isoformat(),
        })

    # 按时间排序
    activities.sort(key=lambda a: a["created_at"], reverse=True)

    # 分页
    total = len(activities)
    paged = activities[offset:offset + limit]

    return {
        "total": total,
        "page": page,
        "data": paged,
    }


def get_current_user_optional(token: str | None = Depends(None), db: Session = Depends(get_db)):
    """Optional auth - doesn't require login"""
    return None


@router.get("/posts")
def get_community_posts(page: int = 1, page_size: int = 20, db: Session = Depends(get_db)):
    """获取全平台用户动态，按时间倒序"""
    offset = (page - 1) * page_size
    import json

    posts = db.query(UserPost).order_by(UserPost.created_at.desc()).offset(offset).limit(page_size).all()
    total = db.query(UserPost).count()

    return {
        "total": total,
        "page": page,
        "data": [{
            "id": p.id,
            "type": "post",
            "user_id": p.user_id,
            "user_nickname": p.user.nickname,
            "user_avatar": p.user.avatar or "",
            "content": p.content,
            "images": json.loads(p.images) if p.images else [],
            "created_at": p.created_at.isoformat(),
        } for p in posts],
    }
