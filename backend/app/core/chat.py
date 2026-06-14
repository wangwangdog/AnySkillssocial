"""WebSocket 即时聊天服务"""
import json
import asyncio
from datetime import datetime, timezone
from typing import Dict, Set
from fastapi import WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User, UserPost
from app.models.order import Order, OrderStatus


class ConnectionManager:
    """管理 WebSocket 连接"""
    def __init__(self):
        # active_connections: Dict[websocket, user_id]
        self.active_connections: Dict[WebSocket, int] = {}
        # user_connections: Dict[user_id, Set[websocket]]
        self.user_connections: Dict[int, Set[WebSocket]] = {}
        # order_rooms: Dict[order_id, Set[websocket]]
        self.order_rooms: Dict[int, Set[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, user_id: int, order_id: int | None = None):
        """建立连接"""
        await websocket.accept()
        self.active_connections[websocket] = user_id
        
        # 记录用户连接
        if user_id not in self.user_connections:
            self.user_connections[user_id] = set()
        self.user_connections[user_id].add(websocket)
        
        # 如果关联订单，加入订单房间
        if order_id:
            if order_id not in self.order_rooms:
                self.order_rooms[order_id] = set()
            self.order_rooms[order_id].add(websocket)
        
        # 发送欢迎消息
        await self.send_personal(
            user_id, 
            {"type": "system", "content": "已连接到聊天室", "timestamp": datetime.now(timezone.utc).isoformat()}
        )
    
    def disconnect(self, websocket: WebSocket):
        """断开连接"""
        if websocket in self.active_connections:
            user_id = self.active_connections.pop(websocket)
            
            # 从用户连接中移除
            if user_id in self.user_connections:
                self.user_connections[user_id].discard(websocket)
                if not self.user_connections[user_id]:
                    del self.user_connections[user_id]
            
            # 从订单房间中移除
            for order_id, room in list(self.order_rooms.items()):
                room.discard(websocket)
                if not room:
                    del self.order_rooms[order_id]
    
    async def send_personal(self, user_id: int, message: dict):
        """发送个人消息"""
        if user_id in self.user_connections:
            # 复制连接列表以防迭代修改
            connections = list(self.user_connections[user_id])
            disconnected = []
            for websocket in connections:
                try:
                    await websocket.send_json(message)
                except Exception:
                    disconnected.append(websocket)
            # 清理断开的连接
            for ws in disconnected:
                self.disconnect(ws)
    
    async def send_order(self, order_id: int, message: dict):
        """发送订单消息（买卖双方）"""
        if order_id in self.order_rooms:
            connections = list(self.order_rooms[order_id])
            for websocket in connections:
                try:
                    await websocket.send_json(message)
                except Exception:
                    pass
    
    def is_online(self, user_id: int) -> bool:
        """检查用户是否在线"""
        return user_id in self.user_connections and len(self.user_connections[user_id]) > 0


# 全局管理器
manager = ConnectionManager()


async def websocket_endpoint(websocket: WebSocket, user_id: int, order_id: int | None = None):
    """WebSocket 端点"""
    await manager.connect(websocket, user_id, order_id)
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # 处理消息
            await handle_message(message, user_id, order_id)
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        print(f"WebSocket 错误：{e}")
        manager.disconnect(websocket)


async def handle_message(message: dict, sender_id: int, order_id: int | None = None):
    """处理聊天消息"""
    msg_type = message.get("type", "text")
    content = message.get("content", "")
    
    if msg_type == "text":
        # 保存到数据库（如果有关联订单）
        if order_id:
            save_chat_message(order_id, sender_id, "text", content)
        
        # 转发给订单的另一方
        if order_id:
            other_user_id = get_other_user(order_id, sender_id)
            await manager.send_order(order_id, {
                "type": "chat",
                "content": content,
                "sender_id": sender_id,
                "order_id": order_id,
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
            
    elif msg_type == "typing":
        # 正在输入通知
        if order_id:
            other_user_id = get_other_user(order_id, sender_id)
            await manager.send_personal(other_user_id, {
                "type": "typing",
                "sender_id": sender_id,
                "order_id": order_id
            })


def save_chat_message(order_id: int, user_id: int, msg_type: str, content: str):
    """保存消息到数据库"""
    # 这里应该创建 ChatMessage 表并保存，当前先记录到日志
    print(f"[Chat] Order:{order_id} User:{user_id} {msg_type}: {content[:50]}...")


def get_other_user(order_id: int, current_user_id: int) -> int:
    """获取订单的另一方用户 ID"""
    # 简化实现，实际应从数据库查询
    return current_user_id  # 占位
