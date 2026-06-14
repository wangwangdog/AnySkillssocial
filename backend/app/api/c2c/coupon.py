"""优惠券 API"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from datetime import datetime, timezone, timedelta
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.coupon import Coupon, CouponType, CouponStatus, UserCoupon
from app.models.order import Service

router = APIRouter(prefix="/api/coupon", tags=["优惠券"])


class CreateCouponRequest(BaseModel):
    name: str
    description: str = ""
    coupon_type: str  # discount/percent/fixed
    value: float
    min_amount: float = 0
    max_discount: float | None = None
    total_count: int = 100
    valid_days: int = 30  # 有效期天数
    skill_type: str | None = None
    service_id: int | None = None


class ClaimCouponRequest(BaseModel):
    code: str


@router.post("/admin/create", status_code=201)
def create_coupon(
    req: CreateCouponRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """创建优惠券（商家/管理员）"""
    # 生成券码
    import random, string
    code = "".join(random.choices(string.ascii_uppercase + string.digits, k=10))
    
    coupon = Coupon(
        code=code,
        name=req.name,
        description=req.description,
        coupon_type=CouponType(req.coupon_type),
        value=req.value,
        min_amount=req.min_amount,
        max_discount=req.max_discount,
        total_count=req.total_count,
        valid_from=datetime.now(timezone.utc),
        valid_to=datetime.now(timezone.utc) + timedelta(days=req.valid_days),
        creator_id=user.id,
        is_admin=False
    )
    db.add(coupon)
    db.commit()
    db.refresh(coupon)
    
    return {
        "id": coupon.id,
        "code": coupon.code,
        "name": coupon.name,
        "type": coupon.coupon_type.value,
        "value": coupon.value
    }


@router.post("/claim")
def claim_coupon(req: ClaimCouponRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """领取优惠券"""
    coupon = db.query(Coupon).filter(Coupon.code == req.code).first()
    if not coupon:
        raise HTTPException(404, "优惠券不存在")
    if not coupon.is_active:
        raise HTTPException(400, "优惠券已下架")
    if coupon.used_count >= coupon.total_count:
        raise HTTPException(400, "优惠券已领完")
    
    # 检查是否已领取
    existing = db.query(UserCoupon).filter(
        UserCoupon.coupon_id == coupon.id,
        UserCoupon.user_id == user.id
    ).first()
    if existing:
        raise HTTPException(400, "您已经领取过该优惠券")
    
    # 创建用户优惠券
    user_coupon = UserCoupon(
        coupon_id=coupon.id,
        user_id=user.id,
        status=CouponStatus.AVAILABLE
    )
    db.add(user_coupon)
    
    # 更新已使用数
    coupon.used_count += 1
    db.commit()
    db.refresh(user_coupon)
    
    return {
        "id": user_coupon.id,
        "code": coupon.code,
        "name": coupon.name,
        "expires_at": coupon.valid_to.isoformat()
    }


@router.get("/my")
def list_my_coupons(
    status: str = "available",  # available/used/expired
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """我的优惠券"""
    query = db.query(UserCoupon).join(Coupon).filter(UserCoupon.user_id == user.id)
    
    if status:
        query = query.filter(UserCoupon.status == CouponStatus(status))
    
    coupons = query.order_by(UserCoupon.created_at.desc()).all()
    
    return {
        "data": [{
            "id": uc.id,
            "code": c.code,
            "name": c.name,
            "description": c.description,
            "type": c.coupon_type.value,
            "value": c.value,
            "min_amount": c.min_amount,
            "status": uc.status.value,
            "valid_from": c.valid_from.isoformat(),
            "valid_to": c.valid_to.isoformat(),
            "skill_type": c.skill_type
        } for uc, c in coupons]
    }


@router.post("/apply")
def apply_coupon(
    coupon_id: int,
    service_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """计算优惠价格"""
    uc = db.query(UserCoupon).join(Coupon).filter(
        UserCoupon.id == coupon_id,
        UserCoupon.user_id == user.id,
        UserCoupon.status == CouponStatus.AVAILABLE
    ).first()
    
    if not uc:
        raise HTTPException(404, "优惠券无效或已使用")
    
    coupon = uc.coupon
    service = db.query(Service).filter(Service.id == service_id).first()
    if not service:
        raise HTTPException(404, "服务不存在")
    
    # 验证使用条件
    if service.price < coupon.min_amount:
        raise HTTPException(400, f"订单金额需满¥{coupon.min_amount}才能使用")
    if coupon.skill_type and service.skill_type != coupon.skill_type:
        raise HTTPException(400, "优惠券不适用于该服务类型")
    
    # 计算优惠
    original_price = service.price
    if coupon.coupon_type == CouponType.FIXED:
        discount = coupon.value
    elif coupon.coupon_type == CouponType.PERCENT:
        discount = original_price * (1 - coupon.value)
        if coupon.max_discount and discount > coupon.max_discount:
            discount = coupon.max_discount
    else:  # discount 类型
        discount = coupon.value
    
    final_price = max(0, original_price - discount)
    
    return {
        "original_price": original_price,
        "discount": discount,
        "final_price": final_price,
        "coupon_code": coupon.code
    }
