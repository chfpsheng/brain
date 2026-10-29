# -*- coding: utf-8 -*-
"""
BRAIN API 批量回测 + 指标抓取（day1.py 的扩展版）
在 day1 的基础上：
  1) 批量跑 alphas/ 下的多个表达式
  2) 每个回测结束后 GET /alphas/{id} 拉取并打印指标
依赖：pip install requests
凭据：同 day1，需 brain_credentials_copy.txt（["邮箱","密码"]）放在运行目录
"""
import json
import time
import requests
from os.path import expanduser, join, dirname
from requests.auth import HTTPBasicAuth

BASE = 'https://api.worldquantbrain.com'

# ---------- 认证 ----------
with open(expanduser('brain_credentials_copy.txt')) as f:
    username, password = json.load(f)

sess = requests.Session()
sess.auth = HTTPBasicAuth(username, password)
resp = sess.post(f'{BASE}/authentication')
print('auth:', resp.status_code, resp.json())

# ---------- 回测设置（与 day1 一致，可改）----------
SIM_SETTINGS = {
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
}


def run_simulation(expression):
    """提交一次回测，轮询直到完成，返回 alpha_id"""
    data = {'type': 'REGULAR', 'settings': SIM_SETTINGS, 'regular': expression}
    r = sess.post(f'{BASE}/simulations', json=data)
    r.raise_for_status()
    url = r.headers['Location']
    while True:
        p = sess.get(url)
        ra = float(p.headers.get('Retry-After', 0))
        if ra == 0:
            break
        time.sleep(ra)
    return p.json()['alpha']


def get_alpha(alpha_id):
    """拉取 alpha 详情（含 IS/OS 指标与各项检查）"""
    r = sess.get(f'{BASE}/alphas/{alpha_id}')
    r.raise_for_status()
    return r.json()


def print_metrics(info):
    is_m = info.get('is', {})
    for k in ['sharpe', 'fitness', 'turnover', 'returns', 'drawdown', 'margin']:
        if k in is_m:
            print(f'    IS {k:<10}: {is_m[k]}')
    print('    self_correlation :', info.get('self_correlation'))
    print('    prod_correlation :', info.get('prod_correlation'))
    # 各项提交检查结果（check 是列表，元素含 name/status）
    checks = info.get('check') or info.get('checks')
    if isinstance(checks, list):
        print('    checks:')
        for c in checks:
            if isinstance(c, dict):
                print(f"      - {c.get('name', c.get('check', '?'))}: {c.get('status', c.get('state', ''))}")


# ---------- 批量跑 alphas/ 下的示例表达式 ----------
HERE = dirname(__file__)
EXPRESSIONS = [
    ('momentum', 'alphas/momentum.txt'),
    ('reversal', 'alphas/reversal.txt'),
    ('quality',  'alphas/quality.txt'),
]

for name, rel in EXPRESSIONS:
    with open(join(HERE, rel)) as fh:
        expr = fh.read().strip()
    print(f'\n=== {name}: {expr} ===')
    aid = run_simulation(expr)
    print('    alpha_id =', aid)
    print_metrics(get_alpha(aid))
