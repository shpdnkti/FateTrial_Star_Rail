import json
import requests
import logging
from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Context, Star, register
from astrbot.api.all import *
from astrbot.api.message_components import *

@register("Star_Rail", "FateTrial", "崩坏星穹铁道攻略查询插件", "1.0.0")
class StrategyQuery(Star):
    @filter.command("崩铁查询")
    async def query_strategy(self, event: AstrMessageEvent, *, message: str):
        yield event.plain_result("正在查询攻略，请稍候...")
        try:
            url = f'https://api.yaohud.cn/api/v5/mihoyou/xing?key=SqGWZxWJxEWagRFxkqB&msg={message}'
            response = requests.post(url, data={'key1': 'value1', 'key2': 'value2'})
            
            try:
                result = response.json()
            except json.JSONDecodeError as e:
                logging.error(f"JSON解析失败: {str(e)}")
                yield event.plain_result(f"数据解析失败，原始响应：\n{response.text}")
                return

            if result['code'] == '200':
                # 格式化输出信息
                formatted_msg = self.format_strategy_result(result)
                yield event.plain_result(formatted_msg)
            else:
                yield event.plain_result("抱歉，查询失败，请稍后重试。")
        except requests.RequestException as e:
            logging.error(f"请求失败: {str(e)}")
            yield event.plain_result(f"网络请求失败，请稍后重试。错误信息：{str(e)}")

    def format_strategy_result(self, result: dict) -> str:
        """格式化攻略查询结果"""
        # 基础信息
        formatted_msg = f"""
⭐ 角色攻略：{result['name']} ⭐
🖼️ 角色简介：
{result['icon']}
🎯 获取途径：{result['take']}
💫 光锥推荐：
{' '.join([cone['name'] for cone in result['guangzhui']])}
🔮 遗器推荐：
{result['recommendation']['one']['early']} + {result['recommendation']['two']['early']}
📊 遗器词条：
躯干：{result['zhuct']['qu']}
脚步：{result['zhuct']['jiao']}
位面球：{result['zhuct']['wei']}
连接绳：{result['zhuct']['lian']}
💠 主词条优先级：
{result['fuct']}
"""

        # 动态处理配队推荐
        if 'ranks' in result and isinstance(result['ranks'], list):
            formatted_msg += "🤝 配队推荐：\n"
            for i, rank in enumerate(result['ranks'], start=1):
                formatted_msg += f"{i}️⃣ {rank['name']}\n"
                formatted_msg += f"阵容：{rank['idstext']}\n"
                formatted_msg += f"说明：{rank['collocation']}\n\n"
        else:
            formatted_msg += "🤝 配队推荐：暂无数据\n\n"

        # 其他信息
        formatted_msg += f"""
💡 遗器说明：
{result['bytion']}
📝 数据来源：{result['tips']}
"""
        return formatted_msg