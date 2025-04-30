import pymysql

try:
    # 创建数据库连接
    connection = pymysql.connect(
        host='192.168.202.165',       # 数据库主机地址
        user='cai',            # 数据库用户名
        password='8888',  # 替换为你的 MySQL 密码
        database='performance_schema'      # 要连接的数据库名
    )

    # 创建游标对象
    with connection.cursor() as cursor:
        # 执行查询
        sql = "SELECT * FROM users"
        cursor.execute(sql)

        # 获取查询结果
        result = cursor.fetchall()
        for row in result:
            print(row)

except pymysql.MySQLError as e:
    print(f"Error: {e}")
finally:
    # 关闭连接
    if connection:
        connection.close()

