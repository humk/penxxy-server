from typing import Dict, Any, Optional
import json

import httpx


class WechatMiniService:
    """
    微信小程序服务
    """
    
    def __init__(self, appid: str, secret: str):
        self.appid = appid
        self.secret = secret
        self.base_url = "https://api.weixin.qq.com"
    
    async def code2session(self, code: str) -> Dict[str, Any]:
        """
        登录凭证校验，获取用户openid和sessionkey
        """
        url = f"{self.base_url}/sns/jscode2session"
        params = {
            "appid": self.appid,
            "secret": self.secret,
            "js_code": code,
            "grant_type": "authorization_code",
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            
            result = response.json()
            if "errcode" in result and result["errcode"] != 0:
                raise Exception(f"微信接口错误: {result['errmsg']}")
            
            return result
    
    async def get_access_token(self) -> str:
        """
        获取小程序全局接口调用凭据
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
    
    async def get_phone_number(self, code: str) -> Dict[str, Any]:
        """
        获取用户手机号
        """
        # 获取access_token
        access_token = await self.get_access_token()
        
        # 构建请求
        url = f"{self.base_url}/wxa/business/getuserphonenumber?access_token={access_token}"
        data = {"code": code}
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=data)
            response.raise_for_status()
            
            result = response.json()
            if result.get("errcode") != 0:
                raise Exception(f"获取手机号失败: {result.get('errmsg')}")
            
            return result 