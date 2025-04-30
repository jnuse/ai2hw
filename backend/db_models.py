import pymysql
import hashlib
from datetime import datetime

# 数据库配置
DB_CONFIG = {
    'host': '192.168.202.165',
    'user': 'cai',
    'password': '8888',
    'database': 'smart_assistant',
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor
}

class Database:
    """数据库连接类"""
    
    @staticmethod
    def get_connection():
        """获取数据库连接"""
        return pymysql.connect(**DB_CONFIG)
    
    @staticmethod
    def execute_query(sql, params=None):
        """执行查询语句"""
        conn = None
        try:
            conn = Database.get_connection()
            with conn.cursor() as cursor:
                cursor.execute(sql, params)
                return cursor.fetchall()
        finally:
            if conn:
                conn.close()
    
    @staticmethod
    def execute_update(sql, params=None):
        """执行更新语句"""
        conn = None
        try:
            conn = Database.get_connection()
            with conn.cursor() as cursor:
                result = cursor.execute(sql, params)
                conn.commit()
                return result
        finally:
            if conn:
                conn.close()
    
    @staticmethod
    def execute_insert(sql, params=None):
        """执行插入语句，返回新插入的ID"""
        conn = None
        try:
            conn = Database.get_connection()
            with conn.cursor() as cursor:
                cursor.execute(sql, params)
                conn.commit()
                return cursor.lastrowid
        finally:
            if conn:
                conn.close()

class User:
    """用户模型"""
    
    @staticmethod
    def hash_password(password):
        """哈希密码"""
        hash_obj = hashlib.sha256()
        hash_obj.update(password.encode('utf-8'))
        return hash_obj.hexdigest()
    
    @staticmethod
    def verify_password(password, hashed_password):
        """验证密码"""
        return User.hash_password(password) == hashed_password
    
    @staticmethod
    def get_by_username(username):
        """通过用户名获取用户"""
        users = Database.execute_query(
            "SELECT * FROM users WHERE username = %s",
            (username,)
        )
        return users[0] if users else None
    
    @staticmethod
    def get_by_id(user_id):
        """通过ID获取用户"""
        users = Database.execute_query(
            "SELECT * FROM users WHERE id = %s",
            (user_id,)
        )
        return users[0] if users else None
    
    @staticmethod
    def authenticate(username, password):
        """用户认证"""
        user = User.get_by_username(username)
        if user and User.verify_password(password, user['password']):
            return user
        return None
    
    @staticmethod
    def create(username, password, openid=None):
        """创建用户"""
        hashed_password = User.hash_password(password)
        return Database.execute_insert(
            "INSERT INTO users (username, password, openid) VALUES (%s, %s, %s)",
            (username, hashed_password, openid)
        )

class HistoryRecord:
    """历史记录模型"""
    
    @staticmethod
    def get_by_id(record_id):
        """通过ID获取记录"""
        records = Database.execute_query(
            "SELECT * FROM history_records WHERE id = %s",
            (record_id,)
        )
        return records[0] if records else None
    
    @staticmethod
    def get_by_user_id(user_id, limit=20, offset=0):
        """获取用户的历史记录"""
        return Database.execute_query(
            "SELECT * FROM history_records WHERE user_id = %s ORDER BY created_at DESC LIMIT %s OFFSET %s",
            (user_id, limit, offset)
        )
    
    @staticmethod
    def create(user_id, title, summary, content):
        """创建历史记录"""
        return Database.execute_insert(
            "INSERT INTO history_records (user_id, title, summary, content) VALUES (%s, %s, %s, %s)",
            (user_id, title, summary, content)
        )
    
    @staticmethod
    def delete(record_id):
        """删除历史记录"""
        return Database.execute_update(
            "DELETE FROM history_records WHERE id = %s",
            (record_id,)
        )
