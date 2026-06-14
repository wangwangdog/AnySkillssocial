"""C2C 端 API 模块"""
from . import auth, demands, services, orders, checkin, users, messages, community, favorites, payment, recommend, upload, chat, slot, search, coupon

__all__ = [
    'auth', 'demands', 'services', 'orders', 'checkin', 'users',
    'messages', 'community', 'favorites', 'payment', 'recommend',
    'upload', 'chat', 'slot', 'search', 'coupon'
]
