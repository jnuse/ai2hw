# 数据库配置
DB_CONFIG = {
    'host': '192.168.202.165',
    'user': 'cai',
    'password': '8888',
    'charset': 'utf8mb4',
    'cursorclass': 'DictCursor'
}

# 数据库名称
DB_NAME = 'smart_assistant'

# API 配置
API_CONFIG = {
    'host': '0.0.0.0',
    'port': 5000,
    'debug': True,
    'secret_key': 'smart_assistant_secret_key',
    'jwt_expiration': 86400  # 24小时，单位：秒
}

# 星火大模型配置
SPARK_CONFIG = {
    'app_id': 'xxx',  # 替换为实际的应用ID
    'api_key': 'xxx',  # 替换为实际的API Key
    'api_secret': 'xxx',  # 替换为实际的API Secret
    'spark_url': 'wss://spark-api.xf-yun.com/v1/x1'  # 更新为指定的星火大模型API地址
}

# 微信小程序配置
WECHAT_CONFIG = {
    'appid': 'touristappid',  # 替换为实际的小程序AppID
    'secret': 'your_secret_here'  # 替换为实际的小程序AppSecret
}
