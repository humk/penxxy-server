from typing import Dict, Any, Optional
import httpx


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
            
            return result 