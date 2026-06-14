"""用户公开信息 API"""
import json
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user, get_current_user_optional
from app.models.user import User, UserAlbum, Follow, ContactPayment
from app.models.order import Service, Demand, DemandStatus
from app.models.user import UserPost

router = APIRouter(prefix="/api/users", tags=["用户"])


@router.get("/{user_id}")
def get_user_profile(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user_optional)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    # 统计
    service_count = db.query(Service).filter(
        Service.seller_id == user_id, Service.is_active == True
    ).count()
    demand_count = db.query(Demand).filter(
        Demand.creator_id == user_id, Demand.status == DemandStatus.OPEN
    ).count()

    # 计算年龄
    age = None
    if user.birth_date:
        today = datetime.now()
        bd = user.birth_date
        age = today.year - bd.year - ((today.month, today.day) < (bd.month, bd.day))

    # 相册
    albums = db.query(UserAlbum).filter(UserAlbum.user_id == user_id).order_by(UserAlbum.sort_order).all()

    # 检查当前用户是否已付费解锁联系方式
    contact_unlocked = False
    if current_user and current_user.id != user_id:
        paid = db.query(ContactPayment).filter(
            ContactPayment.buyer_id == current_user.id,
            ContactPayment.seller_id == user_id,
        ).first()
        if paid:
            contact_unlocked = True

    result = {
        "id": user.id,
        "nickname": user.nickname,
        "avatar": user.avatar or "",
        "bio": user.bio,
        "photos": json.loads(user.photos) if user.photos else [],
        "phone": user.phone[:3] + "****" + user.phone[-4:] if user.phone else "",
        "is_verified": user.is_verified,
        "is_skill_verified": user.is_skill_verified,
        "member_level": user.member_level.value if user.member_level else "free",
        "checkin_streak": user.checkin_streak,
        "service_count": service_count,
        "demand_count": demand_count,
        # 新增人物展示字段
        "gender": user.gender,
        "age": age,
        "height": user.height,
        "education": user.education,
        "occupation": user.occupation,
        "residence_city": user.residence_city,
        "hometown": user.hometown,
        "tags": json.loads(user.tags) if user.tags else [],
        "online_status": user.online_status or False,
        "last_active_at": user.last_active_at.isoformat() if user.last_active_at else None,
        # 统计字段
        "view_count": user.view_count or 0,
        "rating_avg": user.rating_avg or 0.0,
        "completed_order_count": user.completed_order_count or 0,
        "follower_count": user.follower_count or 0,
        "following_count": user.following_count or 0,
        # 相册
        "albums": [{"id": a.id, "url": a.url, "sort_order": a.sort_order} for a in albums],
        # 联系方式
        "contact_price": user.contact_price or 0,
        "contact_unlocked": contact_unlocked,
    }

    if contact_unlocked:
        result["contact_phone"] = user.contact_phone or ""
        result["contact_qq"] = user.contact_qq or ""
        result["contact_wechat"] = user.contact_wechat or ""

    return result


@router.get("/{user_id}/services")
def list_user_services(user_id: int, page: int = 1, page_size: int = 20, db: Session = Depends(get_db)):
    services = db.query(Service).filter(
        Service.seller_id == user_id, Service.is_active == True
    ).order_by(Service.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return {"data": [{
        "id": s.id,
        "title": s.title,
        "description": s.description[:100],
        "skill_type": s.skill_type,
        "price": s.price,
        "cover_image": s.cover_image,
        "created_at": s.created_at.isoformat(),
    } for s in services]}


@router.get("/{user_id}/demands")
def list_user_demands(user_id: int, page: int = 1, page_size: int = 20, db: Session = Depends(get_db)):
    demands = db.query(Demand).filter(
        Demand.creator_id == user_id, Demand.status == DemandStatus.OPEN
    ).order_by(Demand.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return {"data": [{
        "id": d.id,
        "title": d.title,
        "description": d.description[:100],
        "skill_type": d.skill_type,
        "budget": d.budget,
        "location": d.location,
        "created_at": d.created_at.isoformat(),
    } for d in demands]}


from pydantic import BaseModel


class CreatePostRequest(BaseModel):
    content: str
    images: list[str] = []


@router.post("/posts")
def create_post(req: CreatePostRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not req.content.strip():
        raise HTTPException(status_code=400, detail="内容不能为空")
    import json
    post = UserPost(
        user_id=user.id,
        content=req.content,
        images=json.dumps(req.images[:9]),
    )
    db.add(post)
    db.commit()
    db.refresh(post)
    return {"id": post.id, "content": post.content, "created_at": post.created_at.isoformat()}


@router.get("/{user_id}/posts")
def list_user_posts(user_id: int, page: int = 1, page_size: int = 20, db: Session = Depends(get_db)):
    posts = db.query(UserPost).filter(
        UserPost.user_id == user_id
    ).order_by(UserPost.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return {"data": [{"id": p.id, "content": p.content, "images": json.loads(p.images) if p.images else [], "created_at": p.created_at.isoformat(), "user_id": p.user_id} for p in posts]}


# ====== 关注/取关 ======


@router.get("/me/following")
def get_my_following(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """获取我关注的所有用户（含个人资料）"""
    follows = db.query(Follow).filter(Follow.follower_id == current_user.id).order_by(Follow.created_at.desc()).all()
    result = []
    for f in follows:
        u = db.query(User).filter(User.id == f.followee_id).first()
        if not u:
            continue
        age = None
        if u.birth_date:
            from datetime import datetime
            today = datetime.now()
            bd = u.birth_date
            age = today.year - bd.year - ((today.month, today.day) < (bd.month, bd.day))
        tags = json.loads(u.tags) if u.tags else []
        result.append({
            "id": u.id,
            "nickname": u.nickname,
            "avatar": u.avatar or "",
            "gender": u.gender or "",
            "age": age,
            "height": u.height,
            "education": u.education or "",
            "residence": u.residence_city or "",
            "tags": tags,
            "rating_avg": u.rating_avg or 0.0,
            "completed_order_count": u.completed_order_count or 0,
            "follower_count": u.follower_count or 0,
        })
    return {"data": result}


@router.post("/{user_id}/follow")
def follow_user(user_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """关注用户"""
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="不能关注自己")
    target = db.query(User).filter(User.id == user_id).first()
    if not target:
        raise HTTPException(status_code=404, detail="用户不存在")
    existing = db.query(Follow).filter(
        Follow.follower_id == current_user.id,
        Follow.followee_id == user_id,
    ).first()
    if existing:
        return {"followed": True, "message": "已经关注"}
    follow = Follow(follower_id=current_user.id, followee_id=user_id)
    db.add(follow)
    target.follower_count = (target.follower_count or 0) + 1
    current_user.following_count = (current_user.following_count or 0) + 1
    db.commit()
    return {"followed": True, "follower_count": target.follower_count}


@router.post("/{user_id}/unfollow")
def unfollow_user(user_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """取关用户"""
    follow = db.query(Follow).filter(
        Follow.follower_id == current_user.id,
        Follow.followee_id == user_id,
    ).first()
    if not follow:
        return {"followed": False, "message": "未关注"}
    db.delete(follow)
    target = db.query(User).filter(User.id == user_id).first()
    if target:
        target.follower_count = max(0, (target.follower_count or 0) - 1)
    current_user.following_count = max(0, (current_user.following_count or 0) - 1)
    db.commit()
    return {"followed": False, "follower_count": target.follower_count if target else 0}


@router.get("/{user_id}/follow/check")
def check_follow(user_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """检查是否已关注"""
    if user_id == current_user.id:
        return {"is_self": True, "followed": False}
    follow = db.query(Follow).filter(
        Follow.follower_id == current_user.id,
        Follow.followee_id == user_id,
    ).first()
    return {"followed": follow is not None}


# ====== 联系方式付费解锁 ======


@router.get("/{user_id}/contact")
def get_contact_info(user_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """获取联系方式（如果已付费则直接返回，否则返回价格）"""
    if user_id == current_user.id:
        return {"is_self": True, "contact_price": 0}
    seller = db.query(User).filter(User.id == user_id).first()
    if not seller:
        raise HTTPException(status_code=404, detail="用户不存在")
    paid = db.query(ContactPayment).filter(
        ContactPayment.buyer_id == current_user.id,
        ContactPayment.seller_id == user_id,
    ).first()
    if paid:
        return {
            "unlocked": True,
            "contact_phone": seller.contact_phone or "",
            "contact_qq": seller.contact_qq or "",
            "contact_wechat": seller.contact_wechat or "",
        }
    return {"unlocked": False, "contact_price": seller.contact_price or 0}


@router.post("/{user_id}/contact/unlock")
def unlock_contact(user_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """付费解锁联系方式"""
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="不能解锁自己的联系方式")
    seller = db.query(User).filter(User.id == user_id).first()
    if not seller:
        raise HTTPException(status_code=404, detail="用户不存在")
    price = seller.contact_price or 0
    if price <= 0:
        raise HTTPException(status_code=400, detail="该用户联系方式为免费公开")
    # 检查是否已解锁
    existing = db.query(ContactPayment).filter(
        ContactPayment.buyer_id == current_user.id,
        ContactPayment.seller_id == user_id,
    ).first()
    if existing:
        return {
            "unlocked": True,
            "contact_phone": seller.contact_phone or "",
            "contact_qq": seller.contact_qq or "",
            "contact_wechat": seller.contact_wechat or "",
        }
    # 扣款
    if current_user.cash_balance < price:
        raise HTTPException(status_code=400, detail=f"余额不足，需要 ¥{price}，当前余额 ¥{current_user.cash_balance}")
    current_user.cash_balance -= price
    seller.cash_balance += price
    payment = ContactPayment(buyer_id=current_user.id, seller_id=user_id, amount=price)
    db.add(payment)
    db.commit()
    return {
        "unlocked": True,
        "contact_phone": seller.contact_phone or "",
        "contact_qq": seller.contact_qq or "",
        "contact_wechat": seller.contact_wechat or "",
        "amount": price,
    }
