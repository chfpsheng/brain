# -*- coding: utf-8 -*-
"""
BRAIN API 入门：认证 + 提交回测（对应课程 day1 笔记本）
运行前准备：
1. pip install requests
2. 把凭据文件 brain_credentials_copy.txt 放到本脚本运行目录，
   内容为 JSON 数组：["你的邮箱", "你的密码"]
"""
import json
import requests
from os.path import expanduser
from requests.auth import HTTPBasicAuth

# ---------- 认证 ----------
# Load credentials
with open(expanduser('brain_credentials_copy.txt')) as f:
    credentials = json.load(f)

# Extract username and password from the list
username, password = credentials

# Create a session object
sess = requests.Session()

# Set up basic authentication
sess.auth = HTTPBasicAuth(username, password)

# Send a POST request to the API for authentication
response = sess.post('https://api.worldquantbrain.com/authentication')

# Print response status and content for debugging
print(response.status_code)
print(response.json())
# 成功应返回 201，包含 user id / token expiry(14400s) / permissions

# ---------- 回测 Alpha ----------
simulation_data = {
    'type': 'REGULAR',
    'settings': {
        'instrumentType': 'EQUITY',
        'region': 'USA',
        'universe': 'TOP3000',
        'delay': 1,
        'decay': 0,
        'neutralization': 'INDUSTRY',
        'truncation': 0.08,
        'pasteurization': 'ON',
        'unitHandling': 'VERIFY',
        'nanHandling': 'OFF',
        'language': 'FASTEXPR',
        'visualization': False,
    },
    'regular': 'liabilities/assets'  # 表达式
}

from time import sleep
sim_resp = sess.post(
    'https://api.worldquantbrain.com/simulations',
    json=simulation_data,
)
sim_progress_url = sim_resp.headers['Location']

# 轮询回测进度：有 Retry-After 就等它指定的秒数再查，没有说明算完
while True:
    sim_progress_resp = sess.get(sim_progress_url)
    retry_after_sec = float(sim_progress_resp.headers.get('Retry-After', 0))
    if retry_after_sec == 0:
        break
    sleep(retry_after_sec)

alpha_id = sim_progress_resp.json()['alpha']  # the final simulation result
print('alpha_id =', alpha_id)
# 拿着 alpha_id 可继续 GET /alphas/{alpha_id} 查看 Sharpe/Turnover 等指标
