import requests
import json
# 完整对话处理（NLU + 对话策略 + Actions）	✅ 更新对话状态	✅ 运行 Actions

url = "http://localhost:5005/webhooks/rest/webhook"

payload = json.dumps({
    "message": "你好，我想办个残疾证，该咋办啊"
})
headers = {
    'Content-Type': 'application/json'
}

response = requests.request("POST", url, headers=headers, data=payload)

print(response.json())
