from locust import between, events, FastHttpUser
from locust.env import Environment
from locust.user.task import task
import random
import string
import time
import asyncio
from test_dify import AsyncDifyAgentStreamClient

# 初始化环境
env = Environment()


def random_user_id(length=16):
    """生成随机用户标识"""
    letters = string.ascii_lowercase + string.digits
    return ''.join(random.choice(letters) for _ in range(length))


class AsyncLocustUser(FastHttpUser):
    """
    自定义异步用户基类，解决协程未等待问题
    """
    abstract = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._loop = asyncio.get_event_loop()

    def run(self, *args, **kwargs):
        async def run_user():
            try:
                await self.on_start()
                while True:
                    await self.execute_next_task()
            except asyncio.CancelledError:
                await self.on_stop()
            except Exception as e:
                self.environment.events.user_error.fire(
                    user_instance=self, exception=e, tb=e.__traceback__)
                await self.on_stop()

        self._task = asyncio.create_task(run_user())

    async def execute_next_task(self):
        if not self.tasks:
            return

        task = random.choice(self.tasks)
        await task(self)

    async def on_start(self):
        """用户可以覆盖的异步启动方法"""
        pass

    async def on_stop(self):
        """用户可以覆盖的异步停止方法"""
        pass


class AsyncChatApiUser(AsyncLocustUser):
    wait_time = between(0.1, 0.3)
    host = "http://139.210.101.45:12449/v1"

    questions = [
        "门诊慢特病待遇认定怎么办理",
        "医保报销需要什么材料",
        "如何查询医保余额",
        "异地就医怎么备案",
        "生育津贴如何申领"
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client = None
        self.user_id = random_user_id()
        self.api_key = "app-wmEP04yuHznvhCVASXwacicE"

    async def on_start(self):
        """异步启动方法"""
        await super().on_start()
        self.client = AsyncDifyAgentStreamClient(self.api_key)

    async def on_stop(self):
        """异步停止方法"""
        await super().on_stop()
        if self.client:
            await self.client.close()

    @task
    async def ask_question(self):
        try:
            start_time = time.time()
            question = random.choice(self.questions)

            response = await self.client.stream_agent_response(
                query=question,
                user_id=self.user_id
            )

            response_time = int((time.time() - start_time) * 1000)
            answer_length = len(
                response['answer']) if response and 'answer' in response else 0

            self.environment.events.request.fire(
                request_type="DifyAPI",
                name="agent_query",
                response_time=response_time,
                response_length=answer_length,
                exception=None
            )

            if response and 'answer' in response:
                print(f"用户 {self.user_id} 问题: {question}")
                print(f"回答: {response['answer'][:50]}...")

        except Exception as e:
            self.environment.events.request.fire(
                request_type="DifyAPI",
                name="agent_query",
                response_time=0,
                response_length=0,
                exception=e
            )
            print(f"请求失败: {str(e)}")


# 精确控制总请求数
request_count = 0
target_requests = 400


@events.request.add_listener
def track_requests(request_type, name, response_time, response_length, exception, **kwargs):
    global request_count, target_requests
    if exception is None:
        request_count += 1
        print(f"✅ 已完成请求: {request_count}/{target_requests}", end="\r")

        if request_count >= target_requests:
            print("\n🎯 已达到目标请求数，停止测试")
            env.runner.quit()


@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    global env
    env = environment
    print(f"🚀 测试开始，目标请求数: {target_requests}")


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    print(f"🛑 测试结束，实际完成请求: {request_count}")
