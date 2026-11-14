# -*- coding: utf-8 -*-
"""
循环扫描 fundamental_fields.txt 里列出的基本面字段，套用模板：
    rank(-(close - open) / open) * rank({field} / enterprise_value)
把每个字段的回测结果（Sharpe / Fitness / Turnover / alpha_id）写入
fundamental_scan_results.csv，方便挑出哪个基本面因子最能补技术反转。

为什么用文件而不是 API 自动列举：
    BRAIN 的 /data-fields 接口在 TUTORIAL 账号下持续返回 400/429，参数无法稳定通过，
    所以改为从本地文件读字段 ID（ID 可在网页「数据」页直接复制 Field ID 得到）。

用法：
    python scan_fundamentals.py                 # 跑文件里全部字段
    python scan_fundamentals.py --max 3         # 只跑前 3 个
    python scan_fundamentals.py --start 2 --max 3   # 断点续跑

注意：
- TUTORIAL 账号 API 限额很低，脚本已加 429 退避与字段间停顿，但整体仍会慢。
- 事件型(Vector)字段做除法会报 event-input 错误，脚本记录错误并跳过，不影响其他字段。
- 结果实时追加写 CSV，中途中断也能保留已跑的部分。
"""
import json
import sys
import time
import csv
import requests
from os.path import expanduser
from requests.auth import HTTPBasicAuth

BASE = 'https://api.worldquantbrain.com'
FIELDS_FILE = 'fundamental_fields.txt'
TECH_LEG = 'rank(-(close - open) / open)'
TEMPLATE = TECH_LEG + ' * rank({field} / enterprise_value)'   # 可改成 rank({field})

SETTINGS = {
    'instrumentType': 'EQUITY',
    'region': 'USA',
    'universe': 'TOP3000',
    'delay': 1,
    'decay': 7,
    'neutralization': 'SUBINDUSTRY',
    'truncation': 0.08,
    'pasteurization': 'ON',
    'unitHandling': 'VERIFY',
    'nanHandling': 'OFF',
    'language': 'FASTEXPR',
    'visualization': False,
}

OUT_CSV = 'fundamental_scan_results.csv'


def parse_args():
    max_fields = 999999
    start = 0
    args = sys.argv[1:]
    i = 0
    while i < len(args):
        if args[i] == '--max' and i + 1 < len(args):
            max_fields = int(args[i + 1]); i += 2
        elif args[i] == '--start' and i + 1 < len(args):
            start = int(args[i + 1]); i += 2
        else:
            i += 1
    return start, max_fields


def load_fields():
    fields = []
    with open(FIELDS_FILE, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            fields.append(line.split()[0])   # 允许行尾加注释
    return fields


def auth_session():
    cred = json.load(open(expanduser('brain_credentials_copy.txt')))
    sess = requests.Session()
    sess.auth = HTTPBasicAuth(cred[0], cred[1])
    r = sess.post(f'{BASE}/authentication')
    print('auth:', r.status_code, r.json().get('user', {}).get('id'))
    return sess


def run_sim(sess, expr):
    data = {'type': 'REGULAR', 'settings': SETTINGS, 'regular': expr}
    r = sess.post(f'{BASE}/simulations', json=data)
    if r.status_code == 429:
        return 'RATE', None, None
    if r.status_code >= 400:
        return 'ERR', r.status_code, r.text[:300]
    url = r.headers['Location']
    while True:
        p = sess.get(url)
        ra = float(p.headers.get('Retry-After', 0))
        if ra == 0:
            break
        time.sleep(min(ra, 30))
    j = p.json()
    if j.get('status') == 'ERROR':
        return 'SIMERR', j.get('message', ''), j
    return 'OK', j.get('alpha'), j


def fetch_metrics(sess, alpha_id):
    for attempt in range(6):
        a = sess.get(f'{BASE}/alphas/{alpha_id}')
        if a.status_code == 200:
            return a.json()
        if a.status_code == 429:
            time.sleep(20 * (attempt + 1))
        else:
            return {'error': a.text[:200]}
    return {'error': 'metrics 429 after retries'}


def write_row(row):
    with open(OUT_CSV, 'a', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(row)


def main():
    start, max_fields = parse_args()
    sess = auth_session()
    fields = load_fields()
    print('字段总数 =', len(fields))
    if not fields:
        return

    write_row(['field_id', 'status', 'sharpe', 'fitness', 'turnover', 'alpha_id', 'message'])

    count = 0
    for idx, fid in enumerate(fields):
        if idx < start:
            continue
        if count >= max_fields:
            break
        if fid == 'enterprise_value':
            continue
        expr = TEMPLATE.format(field=fid)
        print(f'[{idx}/{len(fields)}] {fid} ...', end=' ', flush=True)
        status, val, extra = run_sim(sess, expr)
        if status == 'RATE':
            print('RATE-LIMIT, 休眠 60s 后重试')
            time.sleep(60)
            status, val, extra = run_sim(sess, expr)
        if status in ('ERR', 'SIMERR'):
            print('FAIL:', val)
            write_row([fid, status, '', '', '', '', str(val)[:200]])
            count += 1
            time.sleep(5)
            continue
        alpha_id = val
        m = fetch_metrics(sess, alpha_id)
        sharpe = m.get('sharpe', '')
        fitness = m.get('fitness', '')
        turnover = m.get('turnover', '')
        print(f'OK alpha={alpha_id} sharpe={sharpe} fitness={fitness} turnover={turnover}')
        write_row([fid, 'OK', sharpe, fitness, turnover, alpha_id, ''])
        count += 1
        time.sleep(8)

    print('完成。结果见', OUT_CSV)


if __name__ == '__main__':
    main()
