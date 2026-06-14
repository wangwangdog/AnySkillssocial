"""签到 & 会员 API"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User, MemberLevel

router = APIRouter(prefix="/api/checkin", tags=["签到"])


@router.post("")
def checkin(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    if user.last_checkin_date == today:
        raise HTTPException(status_code=400, detail="今日已签到")

    # 连续签到
    from datetime import timedelta
    yesterday = (datetime.now(timezone.utc) - timedelta(days=1)).strftime("%Y-%m-%d")
    if user.last_checkin_date == yesterday:
        user.checkin_streak += 1
    else:
        user.checkin_streak = 1

    user.last_checkin_date = today
    user.daily_post_quota += 3  # 签到送发布次数

    # 连续签到额外奖励
    bonus = ""
    if user.checkin_streak == 7:
        user.daily_post_quota += 2
        bonus = "连续签到7天，额外奖励2次发布机会"
    elif user.checkin_streak == 30:
        user.cash_balance += 1.0
        bonus = "连续签到30天，奖励1元现金"

    db.commit()
    return {
        "streak": user.checkin_streak,
        "daily_post_quota": user.daily_post_quota,
        "bonus": bonus,
    }


@router.get("/status")
def checkin_status(user: User = Depends(get_current_user)):
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    return {
        "checked_in_today": user.last_checkin_date == today,
        "streak": user.checkin_streak,
        "daily_post_quota": user.daily_post_quota,
    }
