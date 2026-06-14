"""需求相关 API"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.order import Demand, Application, DemandStatus
from app.models.message import Notification

router = APIRouter(prefix="/api/demands", tags=["需求"])


class CreateDemandRequest(BaseModel):
    title: str
    description: str
    skill_type: str
    budget: float = 0
    has_interview_bonus: bool = False
    interview_bonus_amount: float = 0
    location: str = ""


class ApplyRequest(BaseModel):
    video_url: str = ""
    message: str = ""


@router.post("")
def create_demand(req: CreateDemandRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if user.daily_post_quota <= 0:
        raise HTTPException(status_code=400, detail="今日发布次数已用完，请签到获取")

    demand = Demand(
        creator_id=user.id,
        title=req.title,
        description=req.description,
        skill_type=req.skill_type,
        budget=req.budget,
        has_interview_bonus=req.has_interview_bonus,
        interview_bonus_amount=req.interview_bonus_amount,
        location=req.location,
    )
    user.daily_post_quota -= 1
    db.add(demand)
    db.commit()
    db.refresh(demand)
    return {"id": demand.id, "title": demand.title, "status": "created"}


@router.get("")
def list_demands(skill_type: str = "", page: int = 1, page_size: int = 20, db: Session = Depends(get_db)):
    query = db.query(Demand).filter(Demand.status == DemandStatus.OPEN)
    if skill_type:
        query = query.filter(Demand.skill_type == skill_type)
    total = query.count()
    demands = query.order_by(Demand.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return {"total": total, "page": page, "data": [{
        "id": d.id,
        "title": d.title,
        "description": d.description[:100],
        "skill_type": d.skill_type,
        "budget": d.budget,
        "has_interview_bonus": d.has_interview_bonus,
        "location": d.location,
        "creator": {"id": d.creator.id, "nickname": d.creator.nickname, "avatar": d.creator.avatar},
        "creator_nickname": d.creator.nickname,
        "created_at": d.created_at.isoformat(),
        "applicant_count": d.applicant_count or 0,
    } for d in demands]}


@router.get("/{demand_id}")
def get_demand(demand_id: int, db: Session = Depends(get_db)):
    demand = db.query(Demand).filter(Demand.id == demand_id).first()
    if not demand:
        raise HTTPException(status_code=404, detail="需求不存在")
    return {
        "id": demand.id,
        "title": demand.title,
        "description": demand.description,
        "skill_type": demand.skill_type,
        "budget": demand.budget,
        "has_interview_bonus": demand.has_interview_bonus,
        "interview_bonus_amount": demand.interview_bonus_amount,
        "location": demand.location,
        "status": demand.status.value,
        "creator": {"id": demand.creator.id, "nickname": demand.creator.nickname, "avatar": demand.creator.avatar},
        "created_at": demand.created_at.isoformat(),
    }


@router.post("/{demand_id}/apply")
def apply_demand(demand_id: int, req: ApplyRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    demand = db.query(Demand).filter(Demand.id == demand_id).first()
    if not demand or demand.status != DemandStatus.OPEN:
        raise HTTPException(status_code=404, detail="需求不存在或已关闭")

    existing = db.query(Application).filter(
        Application.demand_id == demand_id, Application.applicant_id == user.id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="你已经报名过了")

    app = Application(demand_id=demand_id, applicant_id=user.id, video_url=req.video_url, message=req.message)
    db.add(app)

    # 通知需求发布者
    notif = Notification(
        user_id=demand.creator_id,
        type="system",
        title=f"{user.nickname} 报名了您的需求",
        content=req.message or f"{user.nickname} 报名了「{demand.title}」",
        related_id=demand_id,
    )
    db.add(notif)

    db.commit()
    return {"id": app.id, "status": "applied"}


@router.post("/{demand_id}/applications/{application_id}/accept")
def accept_application(demand_id: int, application_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    demand = db.query(Demand).filter(Demand.id == demand_id).first()
    if not demand or demand.creator_id != user.id:
        raise HTTPException(status_code=403, detail="只有需求发布者可审核报名")
    app = db.query(Application).filter(Application.id == application_id, Application.demand_id == demand_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="报名不存在")
    if app.status != "pending":
        raise HTTPException(status_code=400, detail="报名已处理")
    app.status = "approved"
    db.commit()
    # 自动创建订单
    from app.models.order import Order, OrderStatus
    order = Order(
        order_no=f"SG{datetime.now().strftime('%Y%m%d%H%M%S%f')}{user.id}",
        order_type="demand",
        demand_id=demand_id,
        buyer_id=app.applicant_id,
        seller_id=user.id,
        amount=demand.budget,
        status=OrderStatus.CONFIRMED,
    )
    # 发通知给报名者
    notif = Notification(
        user_id=app.applicant_id,
        type="order",
        title="报名已通过",
        content=f"{user.nickname} 通过了您的报名申请，订单已创建",
        related_id=order.id,
    )
    db.add(notif)
    db.add(order)
    demand.status = DemandStatus.CLOSED
    db.commit()
    return {"status": "approved", "order_id": order.id}


@router.post("/{demand_id}/applications/{application_id}/reject")
def reject_application(demand_id: int, application_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    demand = db.query(Demand).filter(Demand.id == demand_id).first()
    if not demand or demand.creator_id != user.id:
        raise HTTPException(status_code=403, detail="只有需求发布者可审核报名")
    app = db.query(Application).filter(Application.id == application_id, Application.demand_id == demand_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="报名不存在")
    if app.status != "pending":
        raise HTTPException(status_code=400, detail="报名已处理")
    app.status = "rejected"
    db.commit()
    return {"status": "rejected"}


@router.get("/{demand_id}/applications")
def list_applications(demand_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    demand = db.query(Demand).filter(Demand.id == demand_id).first()
    if not demand or demand.creator_id != user.id:
        raise HTTPException(status_code=403, detail="只有需求发布者可查看报名")
    apps = db.query(Application).filter(Application.demand_id == demand_id).all()
    return {"data": [{
        "id": a.id,
        "applicant_id": a.applicant_id,
        "applicant": {"id": a.applicant.id, "nickname": a.applicant.nickname, "avatar": a.applicant.avatar},
        "video_url": a.video_url,
        "message": a.message,
        "status": a.status,
        "created_at": a.created_at.isoformat(),
    } for a in apps]}
