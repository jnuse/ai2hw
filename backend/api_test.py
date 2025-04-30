import requests
import json

# API基础URL
BASE_URL = 'http://localhost:5000/api'

# 测试密码登录
def test_password_login():
    print("=== 测试密码登录 ===")
    url = f"{BASE_URL}/login"
    data = {
        "username": "test",
        "password": "test123"
    }
    response = requests.post(url, json=data)
    result = response.json()
    print(f"状态码: {response.status_code}")
    print(f"响应内容: {json.dumps(result, ensure_ascii=False, indent=2)}")
    
    if result.get('code') == 0:
        token = result['data']['token']
        return token
    else:
        print("密码登录失败")
        return None

# 测试微信登录
def test_wechat_login():
    print("=== 测试微信登录 ===")
    url = f"{BASE_URL}/login/wechat"
    
    # 在实际应用中，这里应该是从微信服务器获取的code
    # 在测试环境中，我们模拟一个code
    data = {
        "code": "test_wechat_code"
    }
    response = requests.post(url, json=data)
    result = response.json()
    print(f"状态码: {response.status_code}")
    print(f"响应内容: {json.dumps(result, ensure_ascii=False, indent=2)}")
    
    if result.get('code') == 0:
        token = result['data']['token']
        return token
    else:
        print("微信登录失败")
        return None

# 测试获取用户信息
def test_get_user_info(token):
    print("\n=== 测试获取用户信息 ===")
    url = f"{BASE_URL}/user/info"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    response = requests.get(url, headers=headers)
    result = response.json()
    print(f"状态码: {response.status_code}")
    print(f"响应内容: {json.dumps(result, ensure_ascii=False, indent=2)}")

# 测试获取历史记录列表
def test_get_history_list(token):
    print("\n=== 测试获取历史记录列表 ===")
    url = f"{BASE_URL}/history?page=1&page_size=5"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    response = requests.get(url, headers=headers)
    result = response.json()
    print(f"状态码: {response.status_code}")
    print(f"响应内容: {json.dumps(result, ensure_ascii=False, indent=2)}")
    
    if result.get('code') == 0 and result['data']['list']:
        return result['data']['list'][0]['id']  # 返回第一条记录的ID
    else:
        return None

# 测试获取历史记录详情
def test_get_history_detail(token, record_id):
    print("\n=== 测试获取历史记录详情 ===")
    url = f"{BASE_URL}/history/{record_id}"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    response = requests.get(url, headers=headers)
    result = response.json()
    print(f"状态码: {response.status_code}")
    print(f"响应内容: {json.dumps(result, ensure_ascii=False, indent=2)}")

# 测试创建历史记录
def test_create_history(token):
    print("\n=== 测试创建历史记录 ===")
    url = f"{BASE_URL}/history"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    data = {
        "title": "API测试记录",
        "summary": "这是通过API测试脚本创建的历史记录",
        "content": "这是历史记录的详细内容，可以包含很多文本。\n这是第二行内容。"
    }
    response = requests.post(url, json=data, headers=headers)
    result = response.json()
    print(f"状态码: {response.status_code}")
    print(f"响应内容: {json.dumps(result, ensure_ascii=False, indent=2)}")
    
    if result.get('code') == 0:
        return result['data']['id']
    else:
        return None

# 测试聊天
def test_chat(token, conversation_id=None):
    print("\n=== 测试聊天 ===")
    url = f"{BASE_URL}/chat"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    data = {
        "message": "你好，请简单介绍一下自己",
        "conversationId": conversation_id
    }
    
    print(f"发送消息: {data['message']}")
    if conversation_id:
        print(f"使用已有会话: {conversation_id}")
    
    response = requests.post(url, json=data, headers=headers)
    result = response.json()
    print(f"状态码: {response.status_code}")
    
    if result.get('code') == 0:
        print(f"助手回复: {result['data']['reply']}")
        return result['data']['record_id']
    else:
        print(f"请求失败: {json.dumps(result, ensure_ascii=False, indent=2)}")
        return None

# 测试继续聊天
def test_continue_chat(token, record_id):
    print("\n=== 测试继续聊天 ===")
    url = f"{BASE_URL}/chat"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    data = {
        "message": "你能提供一些职场建议吗？",
        "conversationId": record_id
    }
    
    print(f"发送消息: {data['message']}")
    print(f"使用已有会话: {record_id}")
    
    response = requests.post(url, json=data, headers=headers)
    result = response.json()
    print(f"状态码: {response.status_code}")
    
    if result.get('code') == 0:
        print(f"助手回复: {result['data']['reply']}")
        return result['data']['record_id']
    else:
        print(f"请求失败: {json.dumps(result, ensure_ascii=False, indent=2)}")
        return None

# 测试获取示例问题
def test_get_examples():
    print("\n=== 测试获取示例问题 ===")
    url = f"{BASE_URL}/examples"
    response = requests.get(url)
    result = response.json()
    print(f"状态码: {response.status_code}")
    print(f"响应内容: {json.dumps(result, ensure_ascii=False, indent=2)}")

# 测试删除历史记录
def test_delete_history(token, record_id):
    print("\n=== 测试删除历史记录 ===")
    url = f"{BASE_URL}/history/{record_id}"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    response = requests.delete(url, headers=headers)
    result = response.json()
    print(f"状态码: {response.status_code}")
    print(f"响应内容: {json.dumps(result, ensure_ascii=False, indent=2)}")

# 运行所有测试
def run_all_tests():
    # 测试获取示例问题（无需登录）
    test_get_examples()
    
    # 选择登录方式
    login_method = input("请选择登录方式 (1:密码登录, 2:微信登录): ")
    
    # 根据用户选择执行不同的登录方法
    if login_method == "2":
        token = test_wechat_login()
        login_type = "微信登录"
    else:
        token = test_password_login()
        login_type = "密码登录"
    
    if not token:
        print(f"{login_type}失败，终止测试")
        return
    
    # 获取用户信息
    test_get_user_info(token)
    
    # 获取历史记录列表，并获取第一条记录的ID
    record_id = test_get_history_list(token)
    
    # 如果存在历史记录，测试获取详情
    if record_id:
        test_get_history_detail(token, record_id)
    
    # 测试聊天功能
    chat_record_id = test_chat(token)
    
    # 如果聊天成功，测试继续聊天
    if chat_record_id:
        test_continue_chat(token, chat_record_id)
    
    # 创建新的历史记录
    new_record_id = test_create_history(token)
    
    # 如果创建成功，删除该记录（清理测试数据）
    if new_record_id:
        test_delete_history(token, new_record_id)
    
    print("\n所有测试完成！")

if __name__ == "__main__":
    run_all_tests()
