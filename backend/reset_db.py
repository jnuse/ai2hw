import pymysql
from init_db import DB_CONFIG, DB_NAME

def reset_database():
    """重置数据库"""
    try:
        # 连接到MySQL服务器
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # 删除数据库
        cursor.execute(f"DROP DATABASE IF EXISTS {DB_NAME}")
        print(f"数据库 {DB_NAME} 已删除")
        
        cursor.close()
        conn.close()
        
        print("数据库重置完成！")
        print("请运行 init_db.py 重新初始化数据库。")
    except Exception as e:
        print(f"重置数据库出错: {e}")

if __name__ == "__main__":
    confirm = input("警告：此操作将删除数据库中的所有数据！是否继续？(y/n): ")
    if confirm.lower() == 'y':
        reset_database()
    else:
        print("操作已取消")
