import json
import requests
from datetime import datetime
import urllib.parse
import time

def get_via_proxy(url):
    """使用国内/免费中转代理请求，绕过海外 IP 限制"""
    # 使用 allorigins 和 corsproxy 两个中转站
    proxies = [
        f"https://api.allorigins.win/raw?url={urllib.parse.quote(url)}",
        f"https://corsproxy.io/?{urllib.parse.quote(url)}"
    ]
    for p in proxies:
        try:
            r = requests.get(p, timeout=15)
            if r.status_code == 200 and r.text.startswith('{'):
                return r.json()
        except:
            continue
    return None

def fetch_ssq():
    url = "https://www.cwl.gov.cn/cwl_admin/front/cwlkj/search/kjxx/findDrawNotice?name=ssq&issueCount=10"
    res = get_via_proxy(url)
    data = []
    if res and 'result' in res:
        for item in res['result']:
            data.append({
                "issue": item['code'],
                "red": [int(x) for x in item['red'].split(',')],
                "blue": int(item['blue'])
            })
    return data

def fetch_dlt():
    url = "https://webapi.sporttery.cn/gateway/lottery/getHistoryPageListV1.qry?gameNo=85&provinceId=0&pageSize=10&isVerify=1&pageNo=1"
    res = get_via_proxy(url)
    data = []
    if res and 'value' in res and 'list' in res['value']:
        for item in res['value']['list']:
            nums = [int(x) for x in item['lotteryDrawResult'].strip().split()]
            data.append({
                "issue": item['lotteryDrawNum'],
                "front": nums[:5],
                "back": nums[5:]
            })
    return data

def fetch_d3():
    url = "https://www.cwl.gov.cn/cwl_admin/front/cwlkj/search/kjxx/findDrawNotice?name=3d&issueCount=10"
    res = get_via_proxy(url)
    data = []
    if res and 'result' in res:
        for item in res['result']:
            data.append({
                "issue": item['code'],
                "digits": [int(x) for x in item['red'].split(',')]
            })
    return data

def fetch_p3():
    url = "https://webapi.sporttery.cn/gateway/lottery/getHistoryPageListV1.qry?gameNo=35&provinceId=0&pageSize=10&isVerify=1&pageNo=1"
    res = get_via_proxy(url)
    data = []
    if res and 'value' in res and 'list' in res['value']:
        for item in res['value']['list']:
            data.append({
                "issue": item['lotteryDrawNum'],
                "digits": [int(x) for x in item['lotteryDrawResult'].strip().split()]
            })
    return data

def fetch_p5():
    url = "https://webapi.sporttery.cn/gateway/lottery/getHistoryPageListV1.qry?gameNo=350133&provinceId=0&pageSize=10&isVerify=1&pageNo=1"
    res = get_via_proxy(url)
    data = []
    if res and 'value' in res and 'list' in res['value']:
        for item in res['value']['list']:
            data.append({
                "issue": item['lotteryDrawNum'],
                "digits": [int(x) for x in item['lotteryDrawResult'].strip().split()]
            })
    return data

def main():
    data = {"updateTime": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    
    fetchers = [
        ("ssq", fetch_ssq),
        ("dlt", fetch_dlt),
        ("d3",  fetch_d3),
        ("p3",  fetch_p3),
        ("p5",  fetch_p5),
    ]
    
    for key, fetcher in fetchers:
        try:
            time.sleep(1) # 间隔一下
            res = fetcher()
            data[key] = res
            print(f"{key}: 成功获取 {len(res)} 条")
        except Exception as e:
            data[key] = []
            print(f"{key} 失败: {e}")
            
    with open("data.js", "w", encoding="utf-8") as f:
        f.write("window.caipiaoData = " + json.dumps(data, ensure_ascii=False, indent=2) + ";")
    print("完成")

if __name__ == "__main__":
    main()
