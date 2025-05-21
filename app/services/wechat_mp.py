from typing import Dict, Any, Optional
import httpx
import xml.etree.ElementTree as ET
import time
import asyncio
from datetime import datetime

from app.orchestrator.orchestrator import orchestrator
from app.utils.logger import get_logger

# 获取微信公众号服务的日志记录器
logger = get_logger("wechat_mp")

class WechatMPService:
    """
    微信公众号服务
    """
    
    def __init__(
        self, 
        appid: str, 
        secret: str, 
        token: str, 
        aes_key: Optional[str] = None
    ):
        self.appid = appid
        self.secret = secret
        self.token = token
        self.aes_key = aes_key
        self.base_url = "https://api.weixin.qq.com"
        # 存储正在处理的消息
        self.processing_messages = {}
    
    async def get_access_token(self) -> str:
        """
        获取公众号全局接口调用凭据
        """
        url = f"{self.base_url}/cgi-bin/token"
        params = {
            "grant_type": "client_credential",
            "appid": self.appid,
            "secret": self.secret,
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            
            result = response.json()
            if "errcode" in result and result["errcode"] != 0:
                raise Exception(f"获取access_token失败: {result['errmsg']}")
            
            return result["access_token"]
    
    async def parse_xml_message(self, xml_content: bytes) -> Dict[str, Any]:
        """
        解析XML消息
        """
        root = ET.fromstring(xml_content)
        message = {}
        for child in root:
            message[child.tag] = child.text
        
        return message
    
    def generate_reply(self, message: Dict[str, Any], content: str) -> str:
        """
        生成回复消息
        """
        from_user_name = message.get("FromUserName")
        to_user_name = message.get("ToUserName")
        timestamp = int(time.time())
        
        reply_xml = f"""
<xml>
<ToUserName><![CDATA[{from_user_name}]]></ToUserName>
<FromUserName><![CDATA[{to_user_name}]]></FromUserName>
<CreateTime>{timestamp}</CreateTime>
<MsgType><![CDATA[text]]></MsgType>
<Content><![CDATA[{content}]]></Content>
</xml>
"""
        
        return reply_xml.strip()
    
    async def process_message_async(self, message: Dict[str, Any]):
        """
        异步处理消息
        """
        try:
            msg_type = message.get("MsgType")
            
            if msg_type == "text":
                content = message.get("Content", "").strip()
                from_user = message.get("FromUserName")
                
                # 使用Orchestrator中的论文问答Agent进行处理
                result = await orchestrator.process_query(content, agent_id="paper_qa")
                response_text = result.get("response", "抱歉，我无法理解您的问题。")
                
                # 通过客服消息接口发送回复
                await self.send_custom_message(from_user, "text", response_text)
                
            elif msg_type == "event":
                event = message.get("Event")
                from_user = message.get("FromUserName")
                
                if event == "subscribe":
                    welcome_msg = "感谢您关注我们的公众号！我是您的论文助手，可以帮您查找和解读学术论文。\n\n您可以直接发送论文相关问题，例如：\n- 最近有哪些关于大型语言模型的研究？\n- 介绍一下论文2303.08774\n- 人工智能在医疗领域的最新进展"
                    await self.send_custom_message(from_user, "text", welcome_msg)
        
        except Exception as e:
            logger.error(f"异步处理消息时出错: {str(e)}")
            # 如果处理失败，发送错误提示
            try:
                from_user = message.get("FromUserName")
                await self.send_custom_message(
                    from_user, 
                    "text", 
                    "很抱歉，处理您的消息时出现了错误，请稍后再试。"
                )
            except:
                pass
    
    async def auto_reply(self, xml_content: bytes) -> str:
        """
        自动回复功能 - 使用论文问答Agent
        """
        try:
            # 解析消息
            message = await self.parse_xml_message(xml_content)
            
            # 获取消息类型
            msg_type = message.get("MsgType")
            
            # 处理不同类型的消息
            if msg_type == "text":
                # 文本消息，获取内容
                content = message.get("Content", "").strip()
                from_user = message.get("FromUserName")
                
                # 检查是否正在处理该用户的消息
                if from_user in self.processing_messages:
                    # 如果正在处理，返回处理中的提示
                    return self.generate_reply(
                        message, 
                        "您的问题正在处理中，请稍候..."
                    )
                
                # 标记该用户的消息正在处理
                self.processing_messages[from_user] = datetime.now()
                
                # 创建异步任务处理消息
                asyncio.create_task(self.process_message_async(message))
                
                # 立即返回处理中的提示
                return self.generate_reply(
                    message, 
                    "您的问题正在处理中，请稍候..."
                )
                
            elif msg_type == "event":
                # 处理事件消息
                event = message.get("Event")
                
                if event == "subscribe":
                    # 关注事件，立即返回欢迎消息
                    welcome_msg = "感谢您关注我们的公众号！我是您的论文助手，可以帮您查找和解读学术论文。\n\n您可以直接发送论文相关问题，例如：\n- 最近有哪些关于大型语言模型的研究？\n- 介绍一下论文2303.08774\n- 人工智能在医疗领域的最新进展"
                    return self.generate_reply(message, welcome_msg)
                
                # 其他事件类型
                return ""
            
            # 默认回复
            return self.generate_reply(message, "感谢您的消息，我们会尽快处理。")
        
        except Exception as e:
            logger.error(f"自动回复出错: {str(e)}")
            return "很抱歉，处理您的消息时出现了错误，请稍后再试。"
    
    async def send_custom_message(self, openid: str, message_type: str, content: str) -> Dict[str, Any]:
        """
        发送客服消息
        
        Args:
            openid: 用户的openid
            message_type: 消息类型，目前只支持text
            content: 消息内容
        
        Returns:
            微信API返回结果
        """
        try:
            # 获取access_token
            access_token = await self.get_access_token()
            
            # 构造请求URL
            url = f"{self.base_url}/cgi-bin/message/custom/send?access_token={access_token}"
            
            # 构造请求数据
            if message_type == "text":
                data = {
                    "touser": openid,
                    "msgtype": "text",
                    "text": {
                        "content": content
                    }
                }
            else:
                raise ValueError(f"不支持的消息类型: {message_type}")
            
            # 发送请求
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=data)
                response.raise_for_status()
                
                result = response.json()
                if result.get("errcode", 0) != 0:
                    raise Exception(f"发送客服消息失败: {result.get('errmsg')}")
                
                # 发送成功后，从处理列表中移除
                if openid in self.processing_messages:
                    del self.processing_messages[openid]
                
                return result
        except Exception as e:
            logger.error(f"发送客服消息失败: {str(e)}")
            # 发送失败后，从处理列表中移除
            if openid in self.processing_messages:
                del self.processing_messages[openid]
            raise 