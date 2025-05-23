from locust import HttpUser, task, between, events
from locust.env import Environment
import random
import string

# 初始化环境（Locust 2.x+ 的正确方式）
env = Environment()
# locust -f tests/test_nlu.py --web-host=0.0.0.0

def random_user_id(length=16):
    """生成随机用户标识"""
    letters = string.ascii_lowercase + string.digits
    return ''.join(random.choice(letters) for _ in range(length))


class ChatApiUser(HttpUser):
    # host = "http://116.141.0.77:5005"  # 基础地址
    host = "http://116.141.0.77:5678"  # 基础地址
    wait_time = between(0.1, 0.3)      # 缩短等待时间以快速完成400请求

    questions = [
        "门诊慢特病待遇认定怎么办理",
        "医保报销需要什么材料",
        "如何查询医保余额",
        "异地就医怎么备案",
        "生育津贴如何申领"
    ]

    @task
    def ask_question(self):
        # 准备随机请求数据
        # payload = {
        #     "sender": f"{random_user_id()}",
        #     "message": f"{random.choice(self.questions)}"
        # }
        payload = {
            "question": f"用户问题：“{random.choice(self.questions)}”，用户标识：“{random_user_id()}”"
        }

        # 发送POST请求
        with self.client.post(
            # "/webhooks/rest/webhook",
            "/chat",
            json=payload,
            headers={"Content-Type": "application/json"},
            catch_response=True
        ) as response:
            # 验证响应
            if response.status_code != 200:
                response.failure(f"HTTP {response.status_code}")
            elif not response.json().get("success", False):
                response.failure("API returned failure")


# 精确控制总请求数
request_count = 0
target_requests = 400


@events.request.add_listener
def track_requests(request_type, name, response_time, response_length, exception, **kwargs):
    global request_count, target_requests
    if exception is None:  # 只统计成功的请求
        request_count += 1
        print(f"✅ 已完成请求: {request_count}/{target_requests}", end="\r")

        if request_count >= target_requests:
            print("\n🎯 已达到目标请求数，停止测试")
            env.runner.quit()


@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    global env
    env = environment  # 保存环境引用
    print(f"🚀 测试开始，目标请求数: {target_requests}")


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    print(f"🛑 测试结束，实际完成请求: {request_count}")
