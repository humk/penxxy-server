from typing import Dict, Any, Optional
import json
import time
import random
import string
import hashlib
import xml.etree.ElementTree as ET
import uuid

import httpx


class WechatPayService:
    """
    微信支付服务
    """
    
    def __init__(
        self, 
        appid: str, 
        mchid: str, 
        key: str,
        cert_path: Optional[str] = None,
        key_path: Optional[str] = None,
    ):
        self.appid = appid
        self.mchid = mchid
        self.key = key
        self.cert_path = cert_path
        self.key_path = key_path
        self.api_url = "https://api.mch.weixin.qq.com"
    
    def _generate_sign(self, data: Dict[str, Any]) -> str:
        """
        生成签名
        """
        # 按照key=value&key=value的格式，并按字典序排序
        string_to_sign = '&'.join(['%s=%s' % (key, data[key]) for key in sorted(data)])
        
        # 在string_to_sign最后拼接上key=key
        string_to_sign += f"&key={self.key}"
        
        # 进行MD5加密
        return hashlib.md5(string_to_sign.encode('utf-8')).hexdigest().upper()
    
    def _dict_to_xml(self, data: Dict[str, Any]) -> str:
        """
        将字典转换为XML
        """
        xml = ["<xml>"]
        for k, v in data.items():
            if isinstance(v, str):
                xml.append(f"<{k}><![CDATA[{v}]]></{k}>")
            else:
                xml.append(f"<{k}>{v}</{k}>")
        xml.append("</xml>")
        return "".join(xml)
    
    async def _xml_to_dict(self, xml: str) -> Dict[str, Any]:
        """
        将XML转换为字典
        """
        root = ET.fromstring(xml)
        data = {}
        for child in root:
            data[child.tag] = child.text
        
        return data
    
    async def create_jsapi_order(
        self,
        openid: str,
        out_trade_no: str,
        amount: int,
        description: str,
    ) -> Dict[str, Any]:
        """
        创建JSAPI支付订单
        """
        # 构建请求参数
        nonce_str = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(32))
        data = {
            "appid": self.appid,
            "mch_id": self.mchid,
            "nonce_str": nonce_str,
            "body": description,
            "out_trade_no": out_trade_no,
            "total_fee": amount,  # 单位：分
            "spbill_create_ip": "127.0.0.1",  # 实际应用中应该获取客户端IP
            "notify_url": "https://your-domain.com/api/v1/wechat/pay/notify",  # 支付结果通知地址
            "trade_type": "JSAPI",
            "openid": openid,
        }
        
        # 生成签名
        data["sign"] = self._generate_sign(data)
        
        # 转换为XML
        xml_data = self._dict_to_xml(data)
        
        # 发送请求
        url = f"{self.api_url}/pay/unifiedorder"
        async with httpx.AsyncClient() as client:
            response = await client.post(url, content=xml_data)
            response.raise_for_status()
            
            # 解析响应
            result = await self._xml_to_dict(response.text)
            
            if result["return_code"] != "SUCCESS" or result["result_code"] != "SUCCESS":
                error_msg = result.get("err_code_des") or result.get("return_msg")
                raise Exception(f"创建订单失败: {error_msg}")
            
            # 生成支付参数
            timestamp = str(int(time.time()))
            noncestr = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(32))
            package = f"prepay_id={result['prepay_id']}"
            
            pay_params = {
                "appId": self.appid,
                "timeStamp": timestamp,
                "nonceStr": noncestr,
                "package": package,
                "signType": "MD5",
            }
            
            # 生成签名
            pay_params["paySign"] = self._generate_sign(pay_params)
            
            return pay_params
    
    async def process_callback(self, xml_data: bytes) -> Dict[str, Any]:
        """
        处理支付结果通知
        """
        # 解析XML
        result = await self._xml_to_dict(xml_data.decode("utf-8"))
        
        # 验证签名
        sign = result.pop("sign", "")
        if self._generate_sign(result) != sign:
            raise Exception("签名验证失败")
        
        return result 