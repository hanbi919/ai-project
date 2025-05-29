import aiohttp
import asyncio
import json
import random
import string
from typing import Dict, List, Optional, AsyncIterator


class AsyncDifyAgentStreamClient:
    def __init__(self, api_key: str, base_url: str = "http://139.210.101.45:12449/v1"):
        """
        异步初始化 Dify Agent 客户端
        :param api_key: Dify API 密钥
        :param base_url: Dify API 基础地址
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "text/event-stream"
        }
        self.session = None  # 将在首次请求时初始化

    async def _ensure_session(self) -> aiohttp.ClientSession:
        """确保有可用的aiohttp会话"""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session

    async def stream_agent_response(
        self,
        query: str,
        inputs: Optional[Dict] = None,
        user_id: Optional[str] = None,
        conversation_id: Optional[str] = None
    ) -> Dict[str, Optional[List[str]]]:
        """
        异步流式调用 Agent 并处理响应
        :param query: 用户查询内容
        :param inputs: 额外输入参数(可选)
        :param user_id: 用户ID(可选)
        :param conversation_id: 会话ID(可选)
        :return: 包含回答列表和会话ID的字典
        """
        endpoint = f"{self.base_url}/chat-messages"
        payload = {
            "inputs": inputs or {},
            "query": query,
            "response_mode": "streaming",
            "user": user_id or f"user_{self._generate_random_id()}",
        }

        if conversation_id:
            payload["conversation_id"] = conversation_id

        session = await self._ensure_session()
        answers = []
        current_conversation_id = None

        print(f"\n[Agent] 问题: {query}\n[Agent] 开始响应:", end="\n\n", flush=True)

        try:
            async with session.post(
                endpoint,
                headers=self.headers,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                if response.status != 200:
                    error = await response.text()
                    print(f"请求失败: {response.status}")
                    print(error)
                    return {"answer": None, "conversation_id": None}

                async for line in response.content:
                    line = line.strip()
                    if not line:
                        continue

                    if line.startswith(b'data: '):
                        try:
                            data = json.loads(line[6:])  # 去掉 b'data: ' 前缀

                            if 'conversation_id' in data:
                                current_conversation_id = data['conversation_id']

                            if data.get('event') == 'message' and 'answer' in data:
                                answer = data['answer']
                                answers.append(answer)
                                print(answer, end='', flush=True)

                        except json.JSONDecodeError as e:
                            print(f"\nJSON解析错误: {e}")
                            continue

            return {
                "answer": "".join(answers),
                "conversation_id": current_conversation_id
            }

        except (aiohttp.ClientError, asyncio.TimeoutError) as e:
            print(f"\n请求异常: {e}")
            return {"answer": None, "conversation_id": None}

    async def close(self):
        """关闭客户端会话"""
        if self.session and not self.session.closed:
            await self.session.close()

    def _generate_random_id(self) -> str:
        """生成随机用户ID"""
        return ''.join(random.choices(string.ascii_letters + string.digits, k=8))


async def main():
    # 替换为你的实际 API 密钥
    API_KEY = "app-wmEP04yuHznvhCVASXwacicE"

    # 初始化客户端
    client = AsyncDifyAgentStreamClient(API_KEY)

    try:
        # 示例1: 简单查询
        print("示例1: 简单查询")
        response = await client.stream_agent_response(
            query="个体工商户设立登记咋办"
        )
        print(f"\n完整回答: {response['answer']}")

        # # 示例2: 带上下文的连续对话
        # print("\n\n示例2: 连续对话")

        # # 第一轮对话
        # print("\n第一轮:")
        # response1 = await client.stream_agent_response(
        #     query="我想了解新能源汽车行业",
        #     user_id="user_12345",
        # )

        # if response1["conversation_id"]:
        #     # 第二轮对话(使用相同的会话ID)
        #     print("\n第二轮:")
        #     response2 = await client.stream_agent_response(
        #         query="请重点分析特斯拉的市场表现",
        #         user_id="user_12345",
        #         conversation_id=response1["conversation_id"]
        #     )
        #     print(f"\n完整回答: {response2['answer']}")

    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())
