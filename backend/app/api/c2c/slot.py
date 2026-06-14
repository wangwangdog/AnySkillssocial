"""预约排期 API"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from datetime import datetime, timezone, timedelta
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.slot import TimeSlot, SlotStatus, Booking, SellerSchedule
from app.models.order import Service

router = APIRouter(prefix="/api/slot", tags=["预约"])


class CreateSlotRequest(BaseModel):
    date: str  # YYYY-MM-DD
    start_time: str  # HH:MM
    end_time: str  # HH:MM
    price: float = 0.0
    note: str = ""


class CreateBookingRequest(BaseModel):
    slot_id: int
    remark: str = ""


@router.post("/seller/schedule")
def create_schedule(
    weekday_start: str = "09:00",
    weekday_end: str = "18:00",
    weekend_start: str = "10:00",
    weekend_end: str = "20:00",
    rest_days: str = "",
    advance_days: int = 7,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """创建卖家工作时间表"""
    schedule = SellerSchedule(
        seller_id=user.id,
        weekday_start=weekday_start,
        weekday_end=weekday_end,
        weekend_start=weekend_start,
        weekend_end=weekend_end,
        rest_days=rest_days,
        advance_days=advance_days
    )
    db.add(schedule)
    db.commit()
    return {"id": schedule.id, "status": "created"}


@router.post("/service/{service_id}/slots")
def create_slot(
    service_id: int,
    req: CreateSlotRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """卖家创建时间槽"""
    svc = db.query(Service).filter(Service.id == service_id, Service.seller_id == user.id).first()
    if not svc:
        raise HTTPException(404, "服务不存在")
    
    slot = TimeSlot(
        service_id=service_id,
        seller_id=user.id,
        slot_date=datetime.strptime(req.date, "%Y-%m-%d").replace(tzinfo=timezone.utc),
        start_time=req.start_time,
        end_time=req.end_time,
        price=req.price or svc.price,
        note=req.note
    )
    db.add(slot)
    db.commit()
    db.refresh(slot)
    return {"id": slot.id, "status": "created"}


@router.get("/service/{service_id}/slots")
def list_slots(
    service_id: int,
    date: str = "",  # YYYY-MM-DD
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取时间槽列表"""
    query = db.query(TimeSlot).filter(TimeSlot.service_id == service_id)
    
    if date:
        query = query.filter(TimeSlot.slot_date == datetime.strptime(date, "%Y-%m-%d").replace(tzinfo=timezone.utc))
    else:
        # 默认未来 7 天
        today = datetime.now(timezone.utc).date()
        query = query.filter(TimeSlot.slot_date >= today)
    
    slots = query.order_by(TimeSlot.slot_date, TimeSlot.start_time).all()
    
    return {
        "data": [{
            "id": s.id,
            "date": s.slot_date.strftime("%Y-%m-%d"),
            "start_time": str(s.start_time),
            "end_time": str(s.end_time),
            "status": s.status.value,
            "price": s.price,
            "note": s.note,
            "booked": s.booking is not None
        } for s in slots]
    }


@router.post("/booking")
def create_booking(req: CreateBookingRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """买家预约时间槽"""
    slot = db.query(TimeSlot).filter(TimeSlot.id == req.slot_id).first()
    if not slot:
        raise HTTPException(404, "时间槽不存在")
    if slot.status != SlotStatus.AVAILABLE:
        raise HTTPException(400, "该时段不可用")
    
    # 创建预约
    booking = Booking(
        slot_id=req.slot_id,
        buyer_id=user.id,
        remark=req.remark
    )
    db.add(booking)
    
    # 更新状态
    slot.status = SlotStatus.BOOKED
    
    db.commit()
    db.refresh(booking)
    
    return {
        "id": booking.id,
        "slot": {
            "date": slot.slot_date.strftime("%Y-%m-%d"),
            "time": f"{slot.start_time}-{slot.end_time}"
        }
    }


@router.get("/seller/bookings")
def list_my_bookings(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """卖家查看我的预约"""
    bookings = db.query(Booking).join(TimeSlot).filter(
        TimeSlot.seller_id == user.id
    ).order_by(Booking.created_at.desc()).all()
    
    return {
        "data": [{
            "id": b.id,
            "slot_date": b.slot.slot_date.strftime("%Y-%m-%d"),
            "time": f"{b.slot.start_time}-{b.slot.end_time}",
            "buyer": {"id": b.buyer_id, "nickname": db.query(User).filter(User.id == b.buyer_id).first().nickname},
            "status": b.status,
            "remark": b.remark
        } for b in bookings]
    }
