"""认证相关 API"""
from fastapi import APIRouter, Depends, HTTPException, status
import json
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import hash_password, verify_password, create_access_token, get_current_user
from app.models.user import User

router = APIRouter(prefix="/api/auth", tags=["认证"])


class RegisterRequest(BaseModel):
    phone: str
    nickname: str
    password: str


class LoginRequest(BaseModel):
    phone: str
    password: str


@router.post("/register")
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    if db.query(User).filter(User.phone == req.phone).first():
        raise HTTPException(status_code=400, detail="手机号已注册")
    if db.query(User).filter(User.nickname == req.nickname).first():
        raise HTTPException(status_code=400, detail="昵称已存在")

    user = User(
        phone=req.phone,
        nickname=req.nickname,
        password_hash=hash_password(req.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token({"sub": user.id})
    return {"token": token, "user": {"id": user.id, "nickname": user.nickname, "phone": user.phone}}


@router.post("/login")
def login(req: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.phone == req.phone).first()
    if not user or not verify_password(req.password, user.password_hash):
        raise HTTPException(status_code=401, detail="手机号或密码错误")

    token = create_access_token({"sub": user.id})
    return {"token": token, "user": {"id": user.id, "nickname": user.nickname, "phone": user.phone}}


@router.get("/me")
def get_me(user: User = Depends(get_current_user)):
    return {
        "id": user.id,
        "nickname": user.nickname,
        "phone": user.phone,
        "avatar": user.avatar,
        "bio": user.bio,
        "photos": json.loads(user.photos) if user.photos else [],
        "is_verified": user.is_verified,
        "is_skill_verified": user.is_skill_verified,
        "member_level": user.member_level.value,
        "cash_balance": user.cash_balance,
        "points_balance": user.points_balance,
        "checkin_streak": user.checkin_streak,
        "daily_post_quota": user.daily_post_quota,
    }


# ====== 个人认证 ======


class RealnameCertRequest(BaseModel):
    real_name: str
    id_card: str


@router.get("/certification")
def get_certification(user: User = Depends(get_current_user)):
    """获取当前用户认证状态"""
    phone_done = bool(user.phone)
    realname_done = bool(user.is_verified) or (bool(user.real_name) and bool(user.id_card))
    face_done = bool(user.face_photo)
    done_count = sum([phone_done, realname_done, face_done])
    stars = done_count
    return {
        "stars": stars,
        "items": [
            {"key": "phone", "label": "手机认证", "done": phone_done, "desc": "绑定手机号"},
            {"key": "realname", "label": "实名认证", "done": realname_done, "desc": "姓名 + 身份证"},
            {"key": "face", "label": "人脸认证", "done": face_done, "desc": "上传人脸照片"},
        ],
        "real_name": user.real_name or "",
        "id_card": user.id_card[:4] + "****" + user.id_card[-4:] if user.id_card else "",
        "face_photo": user.face_photo or "",
    }


@router.post("/cert/realname")
def submit_realname(req: RealnameCertRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """提交实名认证"""
    if len(req.id_card) != 18:
        raise HTTPException(status_code=400, detail="身份证号格式错误")
    user.real_name = req.real_name
    user.id_card = req.id_card
    user.is_verified = True
    db.commit()
    return {"status": "ok", "message": "实名认证成功"}


class FaceCertRequest(BaseModel):
    photo_url: str


@router.post("/cert/face")
def submit_face(req: FaceCertRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """提交人脸认证照片"""
    if not req.photo_url:
        raise HTTPException(status_code=400, detail="请上传照片")
    user.face_photo = req.photo_url
    user.is_verified = True
    db.commit()
    return {"status": "ok", "message": "人脸认证成功"}
