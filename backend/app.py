from flask import Flask, request, jsonify, g
from flask_cors import CORS
import pymysql
import hashlib
import jwt
import datetime
import requests
import uuid
from functools import wraps
import json
from spark_api import SparkAPI
from config import DB_CONFIG, DB_NAME, API_CONFIG, SPARK_CONFIG, WECHAT_CONFIG
from db_models import User, HistoryRecord, Database

app = Flask(__name__)
CORS(app)  # 启用跨域请求支持

# 使用配置文件中的设置
app.config['SECRET_KEY'] = API_CONFIG['secret_key']
app.config['JWT_EXPIRATION_DELTA'] = API_CONFIG['jwt_expiration']

# 初始化星火大模型API客户端
spark_client = SparkAPI(
    SPARK_CONFIG['app_id'], 
    SPARK_CONFIG['api_key'], 
    SPARK_CONFIG['api_secret'],
    SPARK_CONFIG['spark_url']
)

# 数据库连接配置
db_config = DB_CONFIG.copy()
db_config['database'] = DB_NAME
db_config['cursorclass'] = pymysql.cursors.DictCursor  # 将字符串转换为实际的类

# 数据库连接函数
def get_db():
    if 'db' not in g:
        g.db = pymysql.connect(**db_config)
    return g.db

@app.teardown_appcontext
def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

# 密码哈希函数
def hash_password(password):
    hash_obj = hashlib.sha256()
    hash_obj.update(password.encode('utf-8'))
    return hash_obj.hexdigest()

# Token验证装饰器
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        # 从Authorization头获取token
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Bearer '):
                token = auth_header[7:]
        
        if not token:
            return jsonify({'code': 401, 'message': '未提供Token'}), 401
        
        try:
            # 解码token
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            
            # 获取用户信息
            current_user = User.get_by_id(data['user_id'])
            
            if not current_user:
                return jsonify({'code': 401, 'message': '无效的Token'}), 401
            
        except Exception as e:
            return jsonify({'code': 401, 'message': f'Token验证失败: {str(e)}'}), 401
        
        # 将用户信息存储在g对象中，以便在视图函数中使用
        g.current_user = current_user
        return f(*args, **kwargs)
    return decorated

# 登录API (用户名密码)
@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'code': 400, 'message': '请提供用户名和密码'}), 400
    
    username = data.get('username')
    password = data.get('password')
    
    # 验证用户
    user = User.authenticate(username, password)
    
    if not user:
        return jsonify({'code': 401, 'message': '用户名或密码错误'}), 401
    
    # 生成Token
    token_payload = {
        'user_id': user['id'],
        'username': user['username'],
        'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=app.config['JWT_EXPIRATION_DELTA'])
    }
    token = jwt.encode(token_payload, app.config['SECRET_KEY'], algorithm='HS256')
    
    return jsonify({
        'code': 0,
        'message': '登录成功',
        'data': {
            'token': token,
            'user': {
                'id': user['id'],
                'username': user['username']
            }
        }
    })

# 微信登录API
@app.route('/api/login/wechat', methods=['POST'])
def wechat_login():
    data = request.get_json()
    
    if not data or not data.get('code'):
        return jsonify({'code': 400, 'message': '请提供微信授权码'}), 400
    
    code = data.get('code')
    
    try:
        # 调用微信接口，获取openid和session_key
        wx_resp = None
        
        # 测试环境，模拟微信返回的数据
        if code == 'test_wechat_code':
            wx_resp = {
                'openid': 'wx_' + uuid.uuid4().hex[:28],
                'session_key': 'session_' + uuid.uuid4().hex
            }
        else:
            # 真实环境，调用微信API
            wx_url = f"https://api.weixin.qq.com/sns/jscode2session"
            params = {
                'appid': WECHAT_CONFIG['appid'],
                'secret': WECHAT_CONFIG['secret'],
                'js_code': code,
                'grant_type': 'authorization_code'
            }
            wx_result = requests.get(wx_url, params=params).json()
            
            if 'errcode' in wx_result:
                return jsonify({
                    'code': wx_result.get('errcode', 500),
                    'message': f"微信登录失败: {wx_result.get('errmsg', '未知错误')}"
                }), 400
            
            wx_resp = wx_result
        
        # 获取openid
        openid = wx_resp['openid']
        
        # 查询用户是否存在
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE openid = %s', (openid,))
        user = cursor.fetchone()
        
        # 如果用户不存在，则创建新用户
        if not user:
            username = f"wechat_user_{uuid.uuid4().hex[:8]}"
            password_hash = hash_password(uuid.uuid4().hex)  # 随机密码
            
            cursor.execute('''
                INSERT INTO users (username, password, openid)
                VALUES (%s, %s, %s)
            ''', (username, password_hash, openid))
            conn.commit()
            
            # 获取新创建的用户
            cursor.execute('SELECT * FROM users WHERE openid = %s', (openid,))
            user = cursor.fetchone()
        
        cursor.close()
        
        # 生成Token
        token_payload = {
            'user_id': user['id'],
            'username': user['username'],
            'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=app.config['JWT_EXPIRATION_DELTA'])
        }
        token = jwt.encode(token_payload, app.config['SECRET_KEY'], algorithm='HS256')
        
        return jsonify({
            'code': 0,
            'message': '微信登录成功',
            'data': {
                'token': token,
                'user': {
                    'id': user['id'],
                    'username': user['username']
                }
            }
        })
        
    except Exception as e:
        return jsonify({'code': 500, 'message': f'微信登录异常: {str(e)}'}), 500

# 用户信息API
@app.route('/api/user/info', methods=['GET'])
@token_required
def get_user_info():
    return jsonify({
        'code': 0,
        'message': '获取成功',
        'data': {
            'id': g.current_user['id'],
            'username': g.current_user['username'],
            'openid': g.current_user['openid']
        }
    })

# 历史记录列表API
@app.route('/api/history', methods=['GET'])
@token_required
def get_history_list():
    page = int(request.args.get('page', 1))
    page_size = int(request.args.get('page_size', 10))
    offset = (page - 1) * page_size
    
    # 查询历史记录
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, title, summary, created_at
        FROM history_records
        WHERE user_id = %s
        ORDER BY created_at DESC
        LIMIT %s OFFSET %s
    ''', (g.current_user['id'], page_size, offset))
    records = cursor.fetchall()
    
    # 查询总数
    cursor.execute('SELECT COUNT(*) as total FROM history_records WHERE user_id = %s', (g.current_user['id'],))
    total = cursor.fetchone()['total']
    cursor.close()
    
    # 格式化日期
    for record in records:
        record['created_at'] = record['created_at'].strftime('%Y-%m-%d %H:%M:%S')
    
    return jsonify({
        'code': 0,
        'message': '获取成功',
        'data': {
            'total': total,
            'list': records
        }
    })

# 历史记录详情API
@app.route('/api/history/<int:record_id>', methods=['GET'])
@token_required
def get_history_detail(record_id):
    # 查询记录详情
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, title, summary, content, created_at
        FROM history_records
        WHERE id = %s AND user_id = %s
    ''', (record_id, g.current_user['id']))
    record = cursor.fetchone()
    cursor.close()
    
    if not record:
        return jsonify({'code': 404, 'message': '记录不存在'}), 404
    
    # 格式化日期
    record['created_at'] = record['created_at'].strftime('%Y-%m-%d %H:%M:%S')
    
    # 添加调试日志
    app.logger.info(f"返回历史记录详情: {record}")
    
    return jsonify({
        'code': 0,
        'message': '获取成功',
        'data': record
    })

# 新增历史记录API
@app.route('/api/history', methods=['POST'])
@token_required
def create_history():
    data = request.get_json()
    
    if not data or not data.get('title'):
        return jsonify({'code': 400, 'message': '请提供记录标题'}), 400
    
    title = data.get('title')
    summary = data.get('summary', '')
    content = data.get('content', '')
    
    # 插入记录
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO history_records (user_id, title, summary, content)
        VALUES (%s, %s, %s, %s)
    ''', (g.current_user['id'], title, summary, content))
    conn.commit()
    record_id = cursor.lastrowid
    cursor.close()
    
    return jsonify({
        'code': 0,
        'message': '创建成功',
        'data': {
            'id': record_id
        }
    })

# 删除历史记录API
@app.route('/api/history/<int:record_id>', methods=['DELETE'])
@token_required
def delete_history(record_id):
    # 检查记录是否存在且属于当前用户
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM history_records WHERE id = %s AND user_id = %s', (record_id, g.current_user['id']))
    record = cursor.fetchone()
    
    if not record:
        cursor.close()
        return jsonify({'code': 404, 'message': '记录不存在或无权限删除'}), 404
    
    # 删除记录
    cursor.execute('DELETE FROM history_records WHERE id = %s', (record_id,))
    conn.commit()
    cursor.close()
    
    return jsonify({
        'code': 0,
        'message': '删除成功'
    })

# 聊天API (对接星火大模型)
@app.route('/api/chat', methods=['POST'])
@token_required
def chat():
    data = request.get_json()
    
    if not data or not data.get('message'):
        return jsonify({'code': 400, 'message': '请提供聊天内容'}), 400
    
    user_message = data.get('message')
    conversation_id = data.get('conversationId')  # 可能是None或已有会话ID
    
    # 准备对话历史记录
    messages = []
    record = None
    
    # 如果有会话ID，加载历史对话内容
    if conversation_id:
        # 查询历史对话
        record = HistoryRecord.get_by_id(conversation_id)
        if record and record['user_id'] == g.current_user['id']:
            try:
                # 尝试解析历史内容为消息格式
                content = record['content']
                lines = content.split('\n\n')
                for line in lines:
                    if line.startswith('用户: '):
                        messages.append({
                            "role": "user",
                            "content": line[4:]
                        })
                    elif line.startswith('助手: '):
                        messages.append({
                            "role": "assistant",
                            "content": line[4:]
                        })
            except Exception as e:
                app.logger.error(f"解析历史对话失败: {str(e)}")
    
    # 添加当前用户消息
    messages.append({
        "role": "user",
        "content": user_message
    })
    
    # 调用星火大模型API
    response = spark_client.chat(messages, temperature=0.9, max_tokens=8192)
    
    if not response['success']:
        return jsonify({
            'code': 500,
            'message': response['message'],
            'data': {'error': response.get('error', '未知错误')}
        }), 500
    
    assistant_response = response['content']
    
    # 为此次对话创建或更新历史记录
    conn = get_db()
    cursor = conn.cursor()
    
    # 生成标题和摘要，只有在新建记录时才使用
    title = user_message[:20] + ('...' if len(user_message) > 20 else '')
    summary = user_message[:50] + ('...' if len(user_message) > 50 else '')
    
    # 组织内容
    if not record:
        # 新对话
        content = f"用户: {user_message}\n\n助手: {assistant_response}"
    else:
        # 追加到现有对话
        content = record['content'] + f"\n\n用户: {user_message}\n\n助手: {assistant_response}"
    
    # 插入或更新记录
    if conversation_id and record:
        # 更新现有记录
        cursor.execute('''
            UPDATE history_records
            SET content = %s, updated_at = NOW()
            WHERE id = %s AND user_id = %s
        ''', (content, conversation_id, g.current_user['id']))
        conn.commit()
        record_id = conversation_id
    else:
        # 插入新记录
        cursor.execute('''
            INSERT INTO history_records (user_id, title, summary, content)
            VALUES (%s, %s, %s, %s)
        ''', (g.current_user['id'], title, summary, content))
        conn.commit()
        record_id = cursor.lastrowid
    
    cursor.close()
    
    return jsonify({
        'code': 0,
        'message': '请求成功',
        'data': {
            'reply': assistant_response,
            'record_id': record_id
        }
    })

# 示例问题API
@app.route('/api/examples', methods=['GET'])
def get_examples():
    examples = [
        '如何提高工作效率？',
        '职场中如何处理人际关系？',
        '如何准备晋升答辩？',
        '如何优化我的简历？',
        '如何进行有效的时间管理？',
        '如何处理工作中的压力和倦怠？',
        '如何提升自己的专业技能？',
        '如何和领导有效沟通？',
        '如何处理工作与生活的平衡？',
        '如何设定职业发展目标？'
    ]
    
    return jsonify({
        'code': 0,
        'message': '获取成功',
        'data': examples
    })

if __name__ == '__main__':
    app.run(
        host=API_CONFIG['host'], 
        port=API_CONFIG['port'], 
        debug=API_CONFIG['debug']
    )
