import _thread as thread
import base64
import hashlib
import hmac
import json
import ssl
import time
from datetime import datetime
from time import mktime
from urllib.parse import urlencode, urlparse
from wsgiref.handlers import format_date_time

import websocket  # 需要安装 websocket-client 库

class SparkAPI:
    """星火大模型API封装类 - 基于WebSocket流式对话实现"""
    
    def __init__(self, app_id, api_key, api_secret, spark_url):
        self.app_id = app_id
        self.api_key = api_key
        self.api_secret = api_secret
        self.spark_url = spark_url
        self.host = urlparse(spark_url).netloc
        self.path = urlparse(spark_url).path
        
        # 从URL推断域名
        if '/v1/x1' in spark_url:
            self.domain = "x1"
        else:
            self.domain = "general"
    
    def create_url(self):
        """创建带鉴权信息的WebSocket URL"""
        # 生成RFC1123格式的时间戳
        now = datetime.now()
        date = format_date_time(mktime(now.timetuple()))
        
        # 拼接字符串
        signature_origin = "host: " + self.host + "\n"
        signature_origin += "date: " + date + "\n"
        signature_origin += "GET " + self.path + " HTTP/1.1"
        
        # 进行hmac-sha256加密
        signature_sha = hmac.new(self.api_secret.encode('utf-8'), 
                               signature_origin.encode('utf-8'),
                               digestmod=hashlib.sha256).digest()
        
        signature_sha_base64 = base64.b64encode(signature_sha).decode(encoding='utf-8')
        
        authorization_origin = f'api_key="{self.api_key}", algorithm="hmac-sha256", headers="host date request-line", signature="{signature_sha_base64}"'
        
        authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode(encoding='utf-8')
        
        # 将请求的鉴权参数组合为字典
        v = {
            "authorization": authorization,
            "date": date,
            "host": self.host
        }
        # 拼接鉴权参数，生成url
        url = self.spark_url + '?' + urlencode(v)
        return url
    
    def check_message_length(self, messages, max_length=8000):
        """检查并处理消息长度，防止超出模型限制"""
        total_length = 0
        for msg in messages:
            if 'content' in msg:
                total_length += len(msg['content'])
        
        # 如果总长度超过限制，移除最早的消息直到满足要求
        while total_length > max_length and len(messages) > 1:
            removed_msg = messages.pop(0)
            if 'content' in removed_msg:
                total_length -= len(removed_msg['content'])
        
        return messages
    
    def gen_params(self, messages, temperature=0.7, max_tokens=8192):
        """生成请求参数"""
        # 添加系统提示，限制回复长度
        system_prompt = {
            "role": "system",
            "content": "你是一个专业的智能职场助手。请注意：1. 你的回答应当精炼、简洁且专业，不超过300字；2. 请直接给出答案，不要解释你的思考过程；3. 始终保持礼貌和专业性。4.不要用markdown格式化你的回答。"
        }
        
        # 将系统提示放在消息的开头
        formatted_messages = [system_prompt]
        for msg in messages:
            formatted_messages.append(msg)
        
        data = {
            "header": {
                "app_id": self.app_id,
                "uid": "smart_assistant_uid",
            },
            "parameter": {
                "chat": {
                    "domain": self.domain,
                    "temperature": temperature,
                    "max_tokens": max_tokens
                }
            },
            "payload": {
                "message": {
                    "text": formatted_messages
                }
            }
        }
        return data
    
    def chat(self, messages, temperature=0.7, max_tokens=8192):
        """使用WebSocket与星火大模型进行对话"""
        # 检查消息总长度，避免超出模型限制
        messages = self.check_message_length(messages)
        
        # 创建一个结果容器
        result = {
            "success": False,
            "message": "",
            "content": ""
            # 不再包含reasoning字段，确保不返回思考过程
        }
        
        # 事件标记
        is_completed = False
        
        # WebSocket回调函数
        def on_message(ws, message):
            nonlocal is_completed
            try:
                data = json.loads(message)
                code = data['header']['code']
                
                if code != 0:
                    result["success"] = False
                    result["message"] = f"API返回错误: {data['header'].get('message', '')}"
                    result["error"] = data
                    is_completed = True
                    ws.close()
                else:
                    choices = data["payload"]["choices"]
                    status = choices["status"]
                    
                    # 获取回复内容
                    if 'text' in choices and len(choices['text']) > 0:
                        text = choices['text'][0]
                        
                        # 忽略思维链，不添加到结果中
                        # 如果有思维链，静默处理，不添加到结果
                        if 'reasoning_content' in text and text['reasoning_content']:
                            pass  # 忽略思维链
                        
                        # 获取主要回复内容
                        if 'content' in text and text['content']:
                            result["content"] += text["content"]
                    
                    # 当状态为2时表示回答完成
                    if status == 2:
                        result["success"] = True
                        result["message"] = "请求成功"
                        is_completed = True
                        ws.close()
            except Exception as e:
                result["success"] = False
                result["message"] = f"处理消息时出错: {str(e)}"
                is_completed = True
                ws.close()
        
        def on_error(ws, error):
            nonlocal is_completed
            result["success"] = False
            result["message"] = f"WebSocket错误: {str(error)}"
            result["error"] = str(error)
            is_completed = True
        
        def on_close(ws, close_status_code, close_reason):
            nonlocal is_completed
            # 确保标记为已完成
            is_completed = True
        
        def on_open(ws):
            # 连接建立后发送请求
            def run(*args):
                request_data = self.gen_params(messages, temperature, max_tokens)
                ws.send(json.dumps(request_data))
            thread.start_new_thread(run, ())
        
        # 创建WebSocket连接
        try:
            # 生成带鉴权的URL
            ws_url = self.create_url()
            
            # 创建WebSocket连接
            websocket.enableTrace(False)  # 关闭调试日志
            ws = websocket.WebSocketApp(
                ws_url,
                on_message=on_message,
                on_error=on_error,
                on_close=on_close,
                on_open=on_open
            )
            
            # 启动WebSocket客户端
            ws_thread = thread.start_new_thread(
                ws.run_forever, 
                (None, None, 0.1, None, {"cert_reqs": ssl.CERT_NONE})
            )
            
            # 等待结果，最长等待60秒
            timeout = 60
            start_time = time.time()
            while not is_completed and time.time() - start_time < timeout:
                time.sleep(0.1)
            
            # 如果等待超时
            if not is_completed:
                result["success"] = False
                result["message"] = "请求超时，未能获取完整回复"
            
            # # 确保回复不超过300字
            # if result["success"] and len(result["content"]) > 300:
            #     result["content"] = result["content"][:297] + "..."
            
            return result
            
        except Exception as e:
            return {
                "success": False,
                "message": f"创建WebSocket连接失败: {str(e)}",
                "error": str(e),
                "content": ""
            }
