#!/usr/bin/env python3
"""SkillGate C2C 测试数据生成脚本（适配真实表结构）"""

import sys
import random
import string
from datetime import datetime, timedelta
from sqlalchemy import text
from pathlib import Path
import json

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
print(f"项目根目录：{project_root}")

# 数据库配置
from app.core.database import engine

# 测试数据配置
TEST_USERS = 20
TEST_SERVICES = 100
TEST_DEMANDS = 100

# 模拟数据池
SKILLS = [
    "Python 开发", "前端开发", "UI 设计", "数据分析", "机器学习",
    "文案写作", "视频剪辑", "翻译服务", "法律咨询", "会计服务",
    "心理咨询", "健身指导", "摄影摄像", "音乐制作", "编程教学",
    "外语教学", "营销策划", "品牌设计", "网站优化", "App 开发"
]

CITIES = ["北京", "上海", "广州", "深圳", "杭州", "成都", "武汉", "南京"]

# 生成随机字符串
def random_string(length=6):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

# 生成随机手机号
def random_phone():
    return f"1{random.randint(3,9)}{random.randint(100000000, 999999999)}"

# 生成测试用户
def generate_test_users():
    print(f"📝 生成 {TEST_USERS} 个测试用户...")
    users = []
    
    for i in range(TEST_USERS):
        phone = random_phone()
        nickname = f"测试用户{i+1}_{random_string(3)}"
        
        user_data = {
            "phone": phone,
            "nickname": nickname,
            "password_hash": "test_password_123456",
            "avatar": f"https://api.dicebear.com/7.x/avataaars/svg?seed={random_string(4)}",
            "bio": f"这是一个测试用户，擅长{random.choice(SKILLS)}",
            "rating_avg": round(random.uniform(3.5, 5.0), 2),
            "completed_order_count": random.randint(0, 50),
            "follower_count": random.randint(0, 200),
            "following_count": random.randint(0, 100),
            "is_verified": random.choice([True, False]),
            "is_skill_verified": random.choice([True, False]),
            "skill_type": random.choice(SKILLS),
            "online_status": random.choice([True, False]),
            "last_active_at": datetime.now() - timedelta(hours=random.randint(0, 48)),
            "view_count": random.randint(0, 1000),
            "cash_balance": round(random.uniform(0, 10000), 2),
            "points_balance": random.randint(0, 10000),
            "created_at": datetime.now() - timedelta(days=random.randint(1, 365)),
            "updated_at": datetime.now()
        }
        
        users.append(user_data)
        print(f"   ✓ {nickname} ({phone})")
    
    return users

# 插入用户到数据库
def insert_users(users):
    print(f"📝 插入 {len(users)} 个用户到数据库...")
    
    with engine.connect() as conn:
        # 检查是否已有用户
        result = conn.execute(text("SELECT COUNT(*) FROM users"))
        count = result.scalar()
        if count > 0:
            print(f"   ⚠️  已存在 {count} 个用户，跳过插入")
            result = conn.execute(text("SELECT id, phone FROM users"))
            return [row._asdict() for row in result]
        
        # 插入用户
        for user_data in users:
            try:
                conn.execute(text(
                    "INSERT INTO users (phone, nickname, password_hash, avatar, bio, rating_avg, "
                    "completed_order_count, follower_count, following_count, is_verified, is_skill_verified, "
                    "skill_type, online_status, last_active_at, view_count, cash_balance, points_balance, "
                    "created_at, updated_at) "
                    "VALUES (:phone, :nickname, :password_hash, :avatar, :bio, :rating_avg, "
                    ":completed_order_count, :follower_count, :following_count, :is_verified, :is_skill_verified, "
                    ":skill_type, :online_status, :last_active_at, :view_count, :cash_balance, :points_balance, "
                    ":created_at, :updated_at)"
                ), user_data)
            except Exception as e:
                print(f"   ✗ 插入用户 {user_data['nickname']} 失败：{e}")
                continue
        
        conn.commit()
        print(f"   ✓ 成功插入 {len(users)} 个用户")
        
        # 返回用户 ID 列表
        result = conn.execute(text("SELECT id, phone, nickname FROM users"))
        return [row._asdict() for row in result]

def generate_test_services(user_ids):
    print(f"📝 生成 {TEST_SERVICES} 个服务...")
    services = []
    
    for i in range(TEST_SERVICES):
        user = random.choice(user_ids)
        skill = random.choice(SKILLS)
        city = random.choice(CITIES)
        
        service_data = {
            "seller_id": user['id'],
            "title": f"专业{skill}服务_{random_string(3)}",
            "description": f"提供高质量的{skill}服务，经验丰富，质量保证。", 
            "skill_type": skill,
            "price": round(random.uniform(50, 1000), 2),
            "cover_image": f"https://picsum.photos/seed/{random_string(4)}/400/300",
            "city": city,
            "duration": random.choice(["1 小时", "2 小时", "半天", "1 天", "3 天", "1 周"]),
            "view_count": random.randint(0, 1000),
            "order_count": random.randint(0, 100),
            "is_active": True,
            "created_at": datetime.now() - timedelta(days=random.randint(1, 365))
        }
        
        services.append(service_data)
        if i < 5:
            print(f"   ✓ {service_data['title']} (¥{service_data['price']})")
    
    print(f"   ... 共生成 {TEST_SERVICES} 个服务")
    return services

def insert_services(services):
    print(f"📝 插入 {len(services)} 个服务到数据库...")
    
    with engine.connect() as conn:
        try:
            for service_data in services:
                try:
                    conn.execute(text(
                        "INSERT INTO services (seller_id, title, description, skill_type, price, "
                        "cover_image, city, duration, view_count, order_count, is_active, created_at) "
                        "VALUES (:seller_id, :title, :description, :skill_type, :price, "
                        ":cover_image, :city, :duration, :view_count, :order_count, :is_active, :created_at)"
                    ), service_data)
                except Exception as e:
                    print(f"   ✗ 插入服务失败：{e}")
                    continue
            
            conn.commit()
            print(f"   ✓ 成功插入 {len(services)} 个服务")
        except Exception as e:
            print(f"   ✗ 数据库错误：{e}")
            conn.rollback()

def generate_test_demands(user_ids):
    print(f"📝 生成 {TEST_DEMANDS} 个需求...")
    demands = []
    
    for i in range(TEST_DEMANDS):
        user = random.choice(user_ids)
        skill = random.choice(SKILLS)
        
        demand_data = {
            "user_id": user['id'],
            "title": f"寻求{skill}服务_{random_string(3)}",
            "description": f"我需要一位擅长{skill}的专业人士，要求有相关经验。",
            "skill_type": skill,
            "budget_min": round(random.uniform(100, 500), 2),
            "budget_max": round(random.uniform(500, 2000), 2),
            "status": random.choice(["available", "available", "matched"]),
            "cover_image": f"https://picsum.photos/seed/{random_string(4)}/400/300",
            "view_count": random.randint(0, 500),
            "created_at": datetime.now() - timedelta(days=random.randint(1, 30))
        }
        
        demands.append(demand_data)
        if i < 5:
            print(f"   ✓ {demand_data['title']} (¥{demand_data['budget_min']}-{demand_data['budget_max']})")
    
    print(f"   ... 共生成 {TEST_DEMANDS} 个需求")
    return demands

def insert_demands(demands):
    print(f"📝 插入 {len(demands)} 个需求到数据库...")
    
    with engine.connect() as conn:
        try:
            for demand_data in demands:
                try:
                    conn.execute(text(
                        "INSERT INTO demands (user_id, title, description, skill_type, "
                        "budget_min, budget_max, status, cover_image, view_count, created_at) "
                        "VALUES (:user_id, :title, :description, :skill_type, "
                        ":budget_min, :budget_max, :status, :cover_image, :view_count, :created_at)"
                    ), demand_data)
                except Exception as e:
                    print(f"   ✗ 插入需求失败：{e}")
                    continue
            
            conn.commit()
            print(f"   ✓ 成功插入 {len(demands)} 个需求")
        except Exception as e:
            print(f"   ✗ 数据库错误：{e}")
            conn.rollback()

def verify_data():
    print("\n📊 验证数据...")
    
    with engine.connect() as conn:
        # 统计用户
        result = conn.execute(text("SELECT COUNT(*) as count FROM users"))
        user_count = result.scalar()
        print(f"   用户总数：{user_count}")
        
        # 统计服务
        result = conn.execute(text("SELECT COUNT(*) as count FROM services"))
        service_count = result.scalar()
        print(f"   服务总数：{service_count}")
        
        # 统计需求
        result = conn.execute(text("SELECT COUNT(*) as count FROM demands"))
        demand_count = result.scalar()
        print(f"   需求总数：{demand_count}")
        
        # 统计可用服务
        result = conn.execute(text("SELECT COUNT(*) as count FROM services WHERE is_active=1"))
        active_services = result.scalar()
        print(f"   活跃服务：{active_services}")
        
        # 统计可用需求
        result = conn.execute(text("SELECT COUNT(*) as count FROM demands WHERE status='available'"))
        available_demands = result.scalar()
        print(f"   可用需求：{available_demands}")
        
        # 获取随机用户手机号用于测试登录
        result = conn.execute(text("SELECT phone FROM users LIMIT 5"))
        phones = [row[0] for row in result]
        print(f"   测试账号（前 5 个）：{phones}")
        
        return {
            "users": user_count,
            "services": service_count,
            "demands": demand_count,
            "active_services": active_services,
            "available_demands": available_demands,
            "test_phones": phones
        }

def main():
    print("=" * 50)
    print("SkillGate C2C 测试数据生成")
    print("=" * 50)
    
    # 1. 生成用户
    test_users = generate_test_users()
    
    # 2. 插入用户
    user_ids = insert_users(test_users)
    
    if not user_ids:
        print("\n⚠️  用户表已存在数据，跳过服务/需求生成")
        return
    
    # 3. 生成并插入服务
    test_services = generate_test_services(user_ids)
    insert_services(test_services)
    
    # 4. 生成并插入需求
    test_demands = generate_test_demands(user_ids)
    insert_demands(test_demands)
    
    # 5. 验证
    stats = verify_data()
    
    print("\n" + "=" * 50)
    print("✅ 测试数据生成完成！")
    print("=" * 50)
    print(f"📊 统计：{stats['users']} 用户，{stats['services']} 服务，{stats['demands']} 需求")
    print(f"📊 活跃：{stats['active_services']} 服务，{stats['available_demands']} 需求")
    print("\n📱 访问地址：http://localhost:9902/skillgate/c2c/")
    print("📱 测试账号（手机号）：任意一个，密码：test_password_123456")
    print(f"   示例：{stats['test_phones'][0]}")

if __name__ == "__main__":
    main()
