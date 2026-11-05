import aiohttp
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class SMMProviderAPI:
    """
    Standard SMM Panel v2 API Client.
    Mos keladi: Mediasmm, JustSMM, Peakerr, JAP, SMMFollows, Perfect Panel, SmartPanel va barcha standart panellar.
    """

    @staticmethod
    async def add_order(api_url: str, api_key: str, service_id: int, link: str, quantity: int) -> Dict[str, Any]:
        """
        SMM Providerga yangi buyurtma yuborish
        """
        if not api_url or not api_key:
            return {"error": "API sozlanmagan"}

        payload = {
            "key": api_key,
            "action": "add",
            "service": service_id,
            "link": link,
            "quantity": quantity
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(api_url, data=payload, timeout=aiohttp.ClientTimeout(total=20)) as resp:
                    if resp.status == 200:
                        data = await resp.json(content_type=None)
                        logger.info(f"SMM API Add Order Javobi: {data}")
                        return data
                    else:
                        text = await resp.text()
                        logger.error(f"SMM API Xatolik HTTP {resp.status}: {text}")
                        return {"error": f"HTTP {resp.status}"}
        except Exception as e:
            logger.error(f"SMM API Exception (add_order): {e}")
            return {"error": str(e)}

    @staticmethod
    async def get_order_status(api_url: str, api_key: str, order_id: str) -> Dict[str, Any]:
        """
        Buyurtma holatini tekshirish
        """
        if not api_url or not api_key:
            return {"error": "API sozlanmagan"}

        payload = {
            "key": api_key,
            "action": "status",
            "order": order_id
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(api_url, data=payload, timeout=aiohttp.ClientTimeout(total=15)) as resp:
                    if resp.status == 200:
                        return await resp.json(content_type=None)
                    return {"error": f"HTTP {resp.status}"}
        except Exception as e:
            logger.error(f"SMM API Exception (get_order_status): {e}")
            return {"error": str(e)}

    @staticmethod
    async def get_balance(api_url: str, api_key: str) -> Dict[str, Any]:
        """
        Provayderdagi API hisob qoldig'ini bilish
        """
        if not api_url or not api_key:
            return {"error": "API URL yoki Key kiritilmagan"}

        payload = {
            "key": api_key,
            "action": "balance"
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(api_url, data=payload, timeout=aiohttp.ClientTimeout(total=15)) as resp:
                    if resp.status == 200:
                        return await resp.json(content_type=None)
                    return {"error": f"HTTP {resp.status}"}
        except Exception as e:
            logger.error(f"SMM API Exception (get_balance): {e}")
            return {"error": str(e)}

    @staticmethod
    async def get_services(api_url: str, api_key: str) -> Any:
        """
        Provayderdagi barcha xizmatlar ro'yxatini olish
        """
        if not api_url or not api_key:
            return {"error": "API sozlanmagan"}

        payload = {
            "key": api_key,
            "action": "services"
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(api_url, data=payload, timeout=aiohttp.ClientTimeout(total=20)) as resp:
                    if resp.status == 200:
                        return await resp.json(content_type=None)
                    return {"error": f"HTTP {resp.status}"}
        except Exception as e:
            logger.error(f"SMM API Exception (get_services): {e}")
            return {"error": str(e)}
