"""收藏/关注 API"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User, UserFavorite
from app.models.order import Service, Demand

router = APIRouter(prefix="/api/favorites", tags=["收藏"])


@router.post("")
def toggle_favorite(item_type: str, item_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if item_type not in ("service", "demand"):
        raise HTTPException(status_code=400, detail="类型错误")
    existing = db.query(UserFavorite).filter(
        UserFavorite.user_id == user.id,
        UserFavorite.item_type == item_type,
        UserFavorite.item_id == item_id,
    ).first()
    if existing:
        db.delete(existing)
        db.commit()
        return {"status": "unfavorited"}
    fav = UserFavorite(user_id=user.id, item_type=item_type, item_id=item_id)
    db.add(fav)
    db.commit()
    return {"status": "favorited"}


@router.get("")
def list_favorites(item_type: str = "", user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    query = db.query(UserFavorite).filter(UserFavorite.user_id == user.id)
    if item_type:
        query = query.filter(UserFavorite.item_type == item_type)
    favs = query.order_by(UserFavorite.created_at.desc()).limit(50).all()

    result = []
    for f in favs:
        item = None
        if f.item_type == "service":
            s = db.query(Service).filter(Service.id == f.item_id).first()
            if s:
                item = {"id": s.id, "title": s.title, "description": s.description[:100] if s.description else "", "price": s.price, "skill_type": s.skill_type, "seller_nickname": s.seller.nickname, "seller_id": s.seller_id, "seller": {"id": s.seller.id, "nickname": s.seller.nickname, "avatar": s.seller.avatar}}
        elif f.item_type == "demand":
            d = db.query(Demand).filter(Demand.id == f.item_id).first()
            if d:
                item = {"id": d.id, "title": d.title, "description": d.description[:100] if d.description else "", "budget": d.budget, "skill_type": d.skill_type, "creator_nickname": d.creator.nickname, "creator_id": d.creator_id}
        if item:
            item["fav_type"] = f.item_type
            item["fav_created_at"] = f.created_at.isoformat()
            result.append(item)

    return {"data": result}


@router.get("/check")
def check_favorite(item_type: str, item_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    existing = db.query(UserFavorite).filter(
        UserFavorite.user_id == user.id,
        UserFavorite.item_type == item_type,
        UserFavorite.item_id == item_id,
    ).first()
    return {"favorited": existing is not None}
