import pymysql
import random
import hashlib
from faker import Faker

# 创建Faker实例，使用中文
fake = Faker('zh_CN')

# 数据库配置，参考mysqlTest.py
DB_CONFIG = {
    'host': '192.168.202.165',
    'user': 'cai',
    'password': '8888',
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor
}

# 数据库名称
DB_NAME = 'smart_assistant'

def create_database():
    """创建数据库"""
    try:
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME} DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        print(f"数据库 {DB_NAME} 创建成功！")
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"创建数据库出错: {e}")
        raise

def create_tables():
    """创建表结构"""
    try:
        # 更新配置，连接到新创建的数据库
        config = DB_CONFIG.copy()
        config['database'] = DB_NAME
        conn = pymysql.connect(**config)
        cursor = conn.cursor()
        
        # 创建用户表
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INT PRIMARY KEY AUTO_INCREMENT,
            username VARCHAR(50) NOT NULL UNIQUE,
            password VARCHAR(128) NOT NULL,
            openid VARCHAR(64),
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        
        # 创建历史记录表
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS history_records (
            id INT PRIMARY KEY AUTO_INCREMENT,
            user_id INT NOT NULL,
            title VARCHAR(255) NOT NULL,
            summary TEXT,
            content LONGTEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        
        print("表结构创建成功！")
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"创建表结构出错: {e}")
        raise

def generate_password_hash(password):
    """生成密码哈希值"""
    hash_obj = hashlib.sha256()
    hash_obj.update(password.encode('utf-8'))
    return hash_obj.hexdigest()

def insert_test_data():
    """插入测试数据"""
    try:
        # 连接到数据库
        config = DB_CONFIG.copy()
        config['database'] = DB_NAME
        conn = pymysql.connect(**config)
        cursor = conn.cursor()
        
        # 先检查test用户是否已存在
        cursor.execute("SELECT id FROM users WHERE username = 'test'")
        result = cursor.fetchone()
        
        if result:
            print("test用户已存在，跳过用户创建。")
            user_id = result['id']
        else:
            # 插入test用户
            password_hash = generate_password_hash('test123')
            fake_openid = 'wx_' + ''.join(random.choice('0123456789abcdef') for _ in range(28))
            
            cursor.execute("""
            INSERT INTO users (username, password, openid) 
            VALUES (%s, %s, %s)
            """, ('test', password_hash, fake_openid))
            
            user_id = cursor.lastrowid
            print(f"test用户创建成功，ID: {user_id}")
        
        # 检查是否已有历史记录
        cursor.execute("SELECT COUNT(*) as count FROM history_records WHERE user_id = %s", (user_id,))
        record_count = cursor.fetchone()['count']
        
        if record_count > 0:
            print(f"用户已有 {record_count} 条历史记录，跳过历史记录创建。")
        else:
            # 插入10条随机历史记录
            for i in range(10):
                title = fake.sentence(nb_words=6)[:-1]  # 去掉句号
                summary = fake.paragraph(nb_sentences=2)
                content = '\n\n'.join([fake.paragraph(nb_sentences=5) for _ in range(random.randint(3, 6))])
                created_time = fake.date_time_between(start_date='-30d', end_date='now')
                
                cursor.execute("""
                INSERT INTO history_records (user_id, title, summary, content, created_at)
                VALUES (%s, %s, %s, %s, %s)
                """, (user_id, title, summary, content, created_time))
            
            print(f"成功为用户 {user_id} 创建了10条历史记录！")
        
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"插入测试数据出错: {e}")
        raise

def main():
    """主函数"""
    try:
        # 创建数据库
        create_database()
        # 创建表结构
        create_tables()
        # 插入测试数据
        insert_test_data()
        
        print("数据库初始化完成！")
        print("测试用户: test")
        print("密码: test123")
    except Exception as e:
        print(f"数据库初始化失败: {e}")

if __name__ == "__main__":
    main()
