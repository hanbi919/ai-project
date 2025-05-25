from locust import HttpUser, task, between, events
from locust.env import Environment
import random
import string

# 初始化环境（Locust 2.x+ 的正确方式）
env = Environment()
"""
locust -f tests/locust_test_proxy.py --users 20 \
 --spawn-rate 10 --web-host 0.0.0.0
"""
def random_user_id(length=16):
    """生成随机用户标识"""
    letters = string.ascii_lowercase + string.digits
    return ''.join(random.choice(letters) for _ in range(length))


class ChatApiUser(HttpUser):
    # host = "http://116.142.76.181:5005"  # 基础地址
    # host = "http://116.141.0.116:5005"  # 基础地址
    host = "http://116.141.0.77:5678"  # 基础地址
    wait_time = between(0.1, 0.3)      # 缩短等待时间以快速完成400请求
    
    # questions = [
    #     "个人住房公积金账户合并"
    #     # "你好"
    # ]

    questions = [
        "门诊慢特病待遇认定怎么办理",
        "医保报销需要什么材料",
        "如何查询医保余额",
        "异地就医怎么备案",
        "生育津贴如何申领"
    ]

    def on_start(self):
        """每个用户开始时执行"""
        self.user_id = random_user_id()  # 为每个虚拟用户分配固定ID

    @task
    def ask_question(self):
        # 准备请求数据
        # payload = {
        #     "sender": self.user_id,  # 使用固定用户ID而非每次生成
        #     "message": random.choice(self.questions)
        # }
        payload = {
            "question": f"用户问题：“{random.choice(self.questions)}”，用户标识：“{random_user_id()}”"
        }

        # 发送POST请求
        with self.client.post(
            "/chat",
            # "/webhooks/rest/webhook",
            json=payload,
            headers={
                "Content-Type": "application/json",
                "X-Sender-ID": self.user_id  # 保持与sender一致
            },
            catch_response=True
        ) as response:
            # 更健壮的响应验证
            if response.status_code != 200:
                response.failure(f"HTTP {response.status_code}")
            elif not response.json():  # 检查是否有响应内容
                response.failure("Empty response")
            elif isinstance(response.json(), list) and not response.json():
                response.failure("Empty list response")


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
            env.runner.quit()  # 安全停止测试


@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    global env
    env = environment
    print(f"🚀 测试开始，目标请求数: {target_requests}")


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    print(f"🛑 测试结束，实际完成请求: {request_count}")
