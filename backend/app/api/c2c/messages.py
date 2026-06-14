"""私信 & 通知 API"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from datetime import datetime, timezone
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.message import Conversation, Message, Notification

router = APIRouter(prefix="/api", tags=["消息"])


# ========== 消息 ==========

class SendMessageRequest(BaseModel):
    recipient_id: int
    content: str


@router.post("/messages/send")
def send_message(req: SendMessageRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if user.id == req.recipient_id:
        raise HTTPException(status_code=400, detail="不能给自己发消息")
    recipient = db.query(User).filter(User.id == req.recipient_id).first()
    if not recipient:
        raise HTTPException(status_code=404, detail="用户不存在")

    # 查找或创建会话
    conv = db.query(Conversation).filter(
        or_(
            and_(Conversation.initiator_id == user.id, Conversation.recipient_id == req.recipient_id),
            and_(Conversation.initiator_id == req.recipient_id, Conversation.recipient_id == user.id),
        )
    ).first()

    if not conv:
        conv = Conversation(
            initiator_id=min(user.id, req.recipient_id),
            recipient_id=max(user.id, req.recipient_id),
        )
        db.add(conv)
        db.flush()

    now = datetime.now(timezone.utc)
    msg = Message(
        conversation_id=conv.id,
        sender_id=user.id,
        content=req.content,
        created_at=now,
    )
    db.add(msg)

    # 更新会话
    conv.last_message = req.content[:200]
    conv.last_time = now
    if user.id == conv.initiator_id:
        conv.recipient_unread = (conv.recipient_unread or 0) + 1
    else:
        conv.initiator_unread = (conv.initiator_unread or 0) + 1

    # 创建通知
    notif = Notification(
        user_id=req.recipient_id,
        type="message",
        title=f"{user.nickname} 发来一条消息",
        content=req.content[:200],
        related_id=conv.id,
    )
    db.add(notif)

    db.commit()
    return {"id": msg.id, "conversation_id": conv.id, "created_at": now.isoformat()}


@router.get("/messages/conversations")
def list_conversations(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    convs = db.query(Conversation).filter(
        or_(Conversation.initiator_id == user.id, Conversation.recipient_id == user.id)
    ).order_by(Conversation.last_time.desc()).limit(50).all()

    return {"data": [{
        "id": c.id,
        "other_user": {
            "id": other.id,
            "nickname": other.nickname,
            "avatar": other.avatar,
        },
        "last_message": c.last_message,
        "last_time": c.last_time.isoformat() if c.last_time else None,
        "unread": c.initiator_unread if user.id == c.initiator_id else c.recipient_unread,
    } for c in convs if (other := (c.recipient if user.id == c.initiator_id else c.initiator))]}


@router.get("/messages/{conversation_id}")
def get_conversation(conversation_id: int, page: int = 1, page_size: int = 50, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    conv = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if not conv:
        raise HTTPException(status_code=404, detail="会话不存在")
    if conv.initiator_id != user.id and conv.recipient_id != user.id:
        raise HTTPException(status_code=403, detail="无权查看")

    # 标记已读
    if user.id == conv.initiator_id:
        conv.initiator_unread = 0
    else:
        conv.recipient_unread = 0

    messages = db.query(Message).filter(
        Message.conversation_id == conversation_id
    ).order_by(Message.created_at.asc()).offset((page - 1) * page_size).limit(page_size).all()

    # 标记消息已读
    for m in messages:
        if m.sender_id != user.id and not m.is_read:
            m.is_read = True

    db.commit()

    # other user info
    other_id = conv.recipient_id if conv.initiator_id == user.id else conv.initiator_id
    other = db.query(User).filter(User.id == other_id).first()

    return {
        "conversation_id": conv.id,
        "other_user": {
            "id": other.id,
            "nickname": other.nickname,
            "avatar": other.avatar,
        } if other else None,
        "messages": [{
            "id": m.id,
            "sender_id": m.sender_id,
            "content": m.content,
            "is_read": m.is_read,
            "created_at": m.created_at.isoformat(),
        } for m in messages],
    }


# ========== 通知 ==========

@router.get("/notifications")
def list_notifications(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    notifs = db.query(Notification).filter(
        Notification.user_id == user.id
    ).order_by(Notification.created_at.desc()).limit(50).all()

    return {"data": [{
        "id": n.id,
        "type": n.type,
        "title": n.title,
        "content": n.content,
        "related_id": n.related_id,
        "is_read": n.is_read,
        "created_at": n.created_at.isoformat(),
    } for n in notifs]}


@router.post("/notifications/{notification_id}/read")
def mark_notification_read(notification_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    notif = db.query(Notification).filter(
        Notification.id == notification_id, Notification.user_id == user.id
    ).first()
    if not notif:
        raise HTTPException(status_code=404, detail="通知不存在")
    notif.is_read = True
    db.commit()
    return {"status": "ok"}


@router.post("/notifications/read-all")
def mark_all_notifications_read(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    db.query(Notification).filter(
        Notification.user_id == user.id, Notification.is_read == False
    ).update({"is_read": True})
    db.commit()
    return {"status": "ok"}


@router.get("/notifications/unread-count")
def unread_notification_count(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    count = db.query(Notification).filter(
        Notification.user_id == user.id, Notification.is_read == False
    ).count()
    return {"count": count}
