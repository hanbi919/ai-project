import requests
import json
# 仅解析 NLU（意图+实体）	❌ 不更新对话状态	❌ 不运行任何 Action
url = "http://localhost:5005/model/parse"

payload = json.dumps({
    "text": "你可以办业务吗"
})
headers = {
    'Content-Type': 'application/json'
}

response = requests.request("POST", url, headers=headers, data=payload)
response.encoding = "utf-8"
print(response.json())
