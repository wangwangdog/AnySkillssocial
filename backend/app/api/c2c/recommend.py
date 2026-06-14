"""首页推荐 API"""
import json
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User
from app.models.order import Service, Order, OrderStatus

router = APIRouter(prefix="/api/recommend", tags=["推荐"])


@router.get("/providers")
def get_recommend_providers(db: Session = Depends(get_db)):
    """返回首页推荐的服务提供者（每人2项服务）"""
    # 按用户ID排序，取7位达人（当前ID 1-7）
    users = db.query(User).filter(User.id.in_([1, 2, 3, 4, 5, 6, 7])).all()

    result = []
    for u in users:
        # 查询该用户未被预约的服务（排除有 active order 的）
        active_service_ids = [
            r[0] for r in db.query(Order.service_id).filter(
                Order.service_id.isnot(None),
                Order.status.in_([OrderStatus.CONFIRMED, OrderStatus.IN_PROGRESS]),
            ).all()
        ]
        services = db.query(Service).filter(
            Service.seller_id == u.id,
            Service.is_active == True,
            ~Service.id.in_(active_service_ids) if active_service_ids else True,
        ).order_by(Service.created_at.desc()).limit(2).all()

        # 计算年龄
        age = None
        if u.birth_date:
            from datetime import datetime
            today = datetime.now()
            bd = u.birth_date
            age = today.year - bd.year - ((today.month, today.day) < (bd.month, bd.day))

        tags = json.loads(u.tags) if u.tags else []

        for s in services:
            result.append({
                "id": s.id,
                "title": s.title,
                "price": s.price,
                "skill_type": s.skill_type or "",
                "created_at": s.created_at.isoformat() if s.created_at else "",
                "seller": {
                    "id": u.id,
                    "nickname": u.nickname,
                    "avatar": u.avatar or "",
                },
                "profile": {
                    "gender": u.gender or "",
                    "age": age,
                    "height": u.height,
                    "education": u.education or "",
                    "residence": u.residence_city or "",
                    "tags": tags,
                },
            })

    return {"data": result}
