# 智能职场助手后端

## 数据库初始化

### 前置条件

1. 安装Python 3.6+
2. 安装依赖：`pip install -r requirements.txt`
3. 确保MySQL服务器已启动

### 初始化数据库

运行以下命令初始化数据库：

```bash
python init_db.py
```

## API服务

### 启动API服务

在完成数据库初始化后，可以启动API服务：

```bash
python app.py
```

服务将在 http://localhost:5000 运行。

### API测试

提供了一个测试脚本，可以测试所有API功能：

```bash
python api_test.py
```

运行后会提示选择登录方式，可以选择密码登录或微信登录进行测试。

## 微信小程序配置

在实际部署前，需要在`app.py`中修改微信小程序配置：

```python
# 微信小程序配置
WECHAT_CONFIG = {
    'appid': 'your_appid_here',  # 替换为实际的小程序AppID
    'secret': 'your_secret_here'  # 替换为实际的小程序AppSecret
}
```

## API端点

### 用户相关

- **POST /api/login** - 用户名密码登录
  - 请求：`{"username": "test", "password": "test123"}`
  - 响应：`{"code": 0, "message": "登录成功", "data": {"token": "...", "user": {...}}}`

- **POST /api/login/wechat** - 微信登录
  - 请求：`{"code": "wx_code_from_client"}`
  - 响应：`{"code": 0, "message": "微信登录成功", "data": {"token": "...", "user": {...}}}`

- **GET /api/user/info** - 获取用户信息
  - 请求头：`Authorization: Bearer {token}`
  - 响应：`{"code": 0, "message": "获取成功", "data": {...}}`

### 历史记录相关

- **GET /api/history** - 获取历史记录列表
  - 请求头：`Authorization: Bearer {token}`
  - 查询参数：`page=1&page_size=10`
  - 响应：`{"code": 0, "message": "获取成功", "data": {"total": 10, "list": [...]}}`

- **GET /api/history/{record_id}** - 获取历史记录详情
  - 请求头：`Authorization: Bearer {token}`
  - 响应：`{"code": 0, "message": "获取成功", "data": {...}}`

- **POST /api/history** - 创建历史记录
  - 请求头：`Authorization: Bearer {token}`
  - 请求：`{"title": "标题", "summary": "摘要", "content": "内容"}`
  - 响应：`{"code": 0, "message": "创建成功", "data": {"id": 1}}`

- **DELETE /api/history/{record_id}** - 删除历史记录
  - 请求头：`Authorization: Bearer {token}`
  - 响应：`{"code": 0, "message": "删除成功"}`

### 聊天相关

- **POST /api/chat** - 发送聊天消息
  - 请求头：`Authorization: Bearer {token}`
  - 请求：`{"message": "你好"}`
  - 响应：`{"code": 0, "message": "请求成功", "data": {"reply": "回复内容", "record_id": 1}}`

## 数据库结构

1. **users 表**：存储用户信息
   - id: 用户ID（主键）
   - username: 用户名
   - password: 密码（SHA-256哈希）
   - openid: 微信OpenID
   - created_at: 创建时间
   - updated_at: 更新时间

2. **history_records 表**：存储历史记录
   - id: 记录ID（主键）
   - user_id: 用户ID（外键）
   - title: 标题
   - summary: 摘要
   - content: 内容
   - created_at: 创建时间

## 测试用户

初始化后会创建一个测试用户：
- 用户名：test
- 密码：test123

通过微信登录时，系统会自动创建新用户。
