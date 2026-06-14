"""聊天 API"""
from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.core.chat import websocket_endpoint, manager

router = APIRouter(prefix="/api/chat", tags=["聊天"])


@router.websocket("/ws/{user_id}/{order_id}")
async def chat_websocket(
    websocket: WebSocket,
    user_id: int,
    order_id: int,
    current_user: User = Depends(get_current_user)
):
    """订单聊天 WebSocket"""
    if current_user.id not in [order_id]:  # 简化验证
        await websocket.close(code=403)
        return
    
    await websocket_endpoint(websocket, current_user.id, order_id)


@router.get("/online/{user_id}")
def check_online(user_id: int):
    """检查用户是否在线"""
    return {"online": manager.is_online(user_id)}