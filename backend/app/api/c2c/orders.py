"""订单 & 打卡 API"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.order import Order, OrderStatus, Demand, DemandStatus, Service
from app.models.message import Notification
from app.models.order import Rating

router = APIRouter(prefix="/api/orders", tags=["订单"])


class CreateOrderRequest(BaseModel):
    order_type: str  # demand / service
    demand_id: int | None = None
    service_id: int | None = None
    seller_id: int


class CheckinRequest(BaseModel):
    photo: str = ""
    location: str = ""


@router.post("")
def create_order(req: CreateOrderRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if user.id == req.seller_id:
        raise HTTPException(status_code=400, detail="不能给自己下单")

    seller = db.query(User).filter(User.id == req.seller_id).first()
    if not seller:
        raise HTTPException(status_code=404, detail="卖家不存在")

    amount = 0
    if req.order_type == "demand" and req.demand_id:
        demand = db.query(Demand).filter(Demand.id == req.demand_id).first()
        if not demand or demand.status != DemandStatus.OPEN:
            raise HTTPException(status_code=400, detail="需求不存在或已关闭")
        amount = demand.budget
        demand.status = DemandStatus.CLOSED
    elif req.order_type == "service" and req.service_id:
        svc = db.query(Service).filter(Service.id == req.service_id).first()
        if not svc or not svc.is_active:
            raise HTTPException(status_code=400, detail="服务不存在或已下架")
        amount = svc.price

    order = Order(
        order_no=f"SG{datetime.now().strftime('%Y%m%d%H%M%S%f')}{user.id}",
        order_type=req.order_type,
        demand_id=req.demand_id,
        service_id=req.service_id,
        buyer_id=user.id,
        seller_id=req.seller_id,
        amount=amount,
        status=OrderStatus.CONFIRMED,
    )

    # 检查余额并扣款
    if amount > 0:
        if (user.cash_balance or 0) < amount:
            raise HTTPException(status_code=400, detail=f"余额不足，需要 ¥{amount}，当前余额 ¥{user.cash_balance or 0}")
        user.cash_balance -= amount
        seller.cash_balance = (seller.cash_balance or 0) + amount

        # 流水记录
        from app.models.user import CashFlow
        db.add(CashFlow(user_id=user.id, amount=-amount, flow_type="payment", status="completed", remark=f"订单#{order.order_no} 支付"))
        db.add(CashFlow(user_id=seller.id, amount=amount, flow_type="payment", status="completed", remark=f"订单#{order.order_no} 收款"))

    # 更新服务成交数
    if req.service_id:
        svc = db.query(Service).filter(Service.id == req.service_id).first()
        if svc:
            svc.order_count = (svc.order_count or 0) + 1

    # 发通知给卖家
    notif = Notification(
        user_id=req.seller_id,
        type="order",
        title="您有新订单",
        content=f"{user.nickname} 向您下单，金额 ¥{amount}",
        related_id=order.id,
    )
    db.add(notif)
    db.add(order)
    db.commit()
    db.refresh(order)
    return {"id": order.id, "order_no": order.order_no, "amount": order.amount, "status": order.status.value}


@router.get("/{order_id}")
def get_order(order_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    if order.buyer_id != user.id and order.seller_id != user.id:
        raise HTTPException(status_code=403, detail="无权查看此订单")
    return {
        "id": order.id,
        "order_no": order.order_no,
        "order_type": order.order_type,
        "amount": order.amount,
        "status": order.status.value,
        "buyer": {
            "id": order.buyer.id,
            "nickname": order.buyer.nickname,
            "avatar": order.buyer.avatar,
        },
        "seller": {
            "id": order.seller.id,
            "nickname": order.seller.nickname,
            "avatar": order.seller.avatar,
        },
        "service": {
            "title": order.service.title,
            "skill_type": order.service.skill_type,
        } if order.service else None,
        "demand": {
            "title": order.demand.title,
            "skill_type": order.demand.skill_type,
        } if order.demand else None,
        "buyer_checkin_time": order.buyer_checkin_time.isoformat() if order.buyer_checkin_time else None,
        "seller_checkin_time": order.seller_checkin_time.isoformat() if order.seller_checkin_time else None,
        "buyer_checkout_time": order.buyer_checkout_time.isoformat() if order.buyer_checkout_time else None,
        "seller_checkout_time": order.seller_checkout_time.isoformat() if order.seller_checkout_time else None,
        "created_at": order.created_at.isoformat(),
        "rating": {
            "score": order.ratings[0].score,
            "comment": order.ratings[0].comment,
            "rater_id": order.ratings[0].rater_id,
            "ratee_id": order.ratings[0].ratee_id,
        } if order.ratings else None,
    }


@router.get("")
def list_orders(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    orders = db.query(Order).filter(
        (Order.buyer_id == user.id) | (Order.seller_id == user.id)
    ).order_by(Order.created_at.desc()).limit(50).all()

    return {"data": [{
        "id": o.id,
        "order_no": o.order_no,
        "order_type": o.order_type,
        "amount": o.amount,
        "status": o.status.value,
        "buyer": {"id": o.buyer.id, "nickname": o.buyer.nickname},
        "seller": {"id": o.seller.id, "nickname": o.seller.nickname},
        "service": {
            "title": o.service.title,
            "skill_type": o.service.skill_type,
            "seller": {"nickname": o.service.seller.nickname}
        } if o.service else None,
        "demand": {
            "title": o.demand.title,
            "skill_type": o.demand.skill_type,
            "creator": {"nickname": o.demand.creator.nickname}
        } if o.demand else None,
        "checkin_location": o.checkin_location,
        "created_at": o.created_at.isoformat(),
    } for o in orders]}


@router.post("/{order_id}/checkin")
def checkin(order_id: int, req: CheckinRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    if order.status not in (OrderStatus.CONFIRMED, OrderStatus.IN_PROGRESS):
        raise HTTPException(status_code=400, detail="订单状态不允许打卡")

    now = datetime.now(timezone.utc)
    if user.id == order.buyer_id:
        order.buyer_checkin_time = now
        order.buyer_checkin_photo = req.photo
    elif user.id == order.seller_id:
        order.seller_checkin_time = now
        order.seller_checkin_photo = req.photo
    else:
        raise HTTPException(status_code=403, detail="无权操作此订单")

    order.checkin_location = req.location
    order.status = OrderStatus.IN_PROGRESS
    db.commit()
    return {"status": "checked_in"}


@router.post("/{order_id}/checkout")
def checkout(order_id: int, req: CheckinRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    if order.status != OrderStatus.IN_PROGRESS:
        raise HTTPException(status_code=400, detail="服务尚未开始")

    now = datetime.now(timezone.utc)
    if user.id == order.buyer_id:
        order.buyer_checkout_time = now
    elif user.id == order.seller_id:
        order.seller_checkout_time = now
    else:
        raise HTTPException(status_code=403, detail="无权操作此订单")

    # 双方都打卡结束才完成
    if order.buyer_checkout_time and order.seller_checkout_time:
        order.status = OrderStatus.COMPLETED
        order.settled_at = now
        # 佣金结算到积分
        seller = db.query(User).filter(User.id == order.seller_id).first()
        seller.points_balance += order.amount
        from app.models.user import PointsFlow
        db.add(PointsFlow(user_id=order.seller_id, amount=order.amount, flow_type="earn", remark=f"订单#{order.order_no}"))

    db.commit()
    return {"status": "checked_out", "order_status": order.status.value}
@router.post("/{order_id}/rate")
def rate_order(order_id: int, score: int = 5, comment: str = "", user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if score < 1 or score > 5:
        raise HTTPException(status_code=400, detail="评分须在1-5分之间")
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    if order.status != OrderStatus.COMPLETED:
        raise HTTPException(status_code=400, detail="只能对已完成的订单评价")

    if order.buyer_id != user.id and order.seller_id != user.id:
        raise HTTPException(status_code=403, detail="无权评价此订单")

    # 确定评价对象
    ratee_id = order.seller_id if user.id == order.buyer_id else order.buyer_id
    # 确定评价对象昵称
    ratee = db.query(User).filter(User.id == ratee_id).first()

    existing = db.query(Rating).filter(
        Rating.order_id == order_id, Rating.rater_id == user.id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="您已评价过此订单")

    rating = Rating(
        order_id=order_id,
        rater_id=user.id,
        ratee_id=ratee_id,
        score=score,
        comment=comment,
    )
    db.add(rating)
    db.commit()
    db.refresh(rating)
    return {
        "id": rating.id,
        "score": rating.score,
        "comment": rating.comment,
        "ratee": {"id": ratee.id, "nickname": ratee.nickname} if ratee else None,
        "created_at": rating.created_at.isoformat(),
    }


@router.get("/{order_id}/rating")
def get_order_rating(order_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    if order.buyer_id != user.id and order.seller_id != user.id:
        raise HTTPException(status_code=403, detail="无权查看")

    ratings = db.query(Rating).filter(Rating.order_id == order_id).all()
    return {"data": [{
        "id": r.id,
        "score": r.score,
        "comment": r.comment,
        "rater": {"id": r.rater.id, "nickname": r.rater.nickname},
        "ratee": {"id": r.ratee.id, "nickname": r.ratee.nickname},
        "created_at": r.created_at.isoformat(),
    } for r in ratings]}
