import json
import requests
from datetime import datetime

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def fetch_from_api(api_type):
    """使用第三方公开 API 接口获取数据"""
    url = f"https://api.vvhan.com/api/lottery?type={api_type}"
    r = requests.get(url, headers=HEADERS, timeout=15)
    res = r.json()
    if not res.get('success'):
        raise Exception("接口返回失败")
    
    d = res.get('data', {})
    data = []
    
    # 接口通常只返回最新一期，我们将其转换成我们的格式
    if api_type == 'ssq':
        data.append({
            "issue": d.get('issue'),
            "red": [int(x) for x in str(d.get('red', '')).split(',') if x],
            "blue": int(d.get('blue', 0))
        })
    elif api_type == 'dlt':
        data.append({
            "issue": d.get('issue'),
            "front": [int(x) for x in str(d.get('front', '')).split(',') if x],
            "back": [int(x) for x in str(d.get('back', '')).split(',') if x]
        })
    elif api_type in ['d3', 'p3', 'p5']:
        res_str = str(d.get('code', ''))
        digits = []
        if ',' in res_str:
            digits = [int(x) for x in res_str.split(',')]
        else:
            digits = [int(x) for x in res_str]
        data.append({
            "issue": d.get('issue'),
            "digits": digits
        })
    return data

def main():
    data = {"updateTime": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    
    # 对应接口的类型参数
    fetchers = [
        ("ssq", "ssq"),
        ("dlt", "dlt"),
        ("d3",  "d3"),
        ("p3",  "p3"),
        ("p5",  "p5"),
    ]
    
    for key, api_type in fetchers:
        try:
            import time; time.sleep(1) # 防止请求过快
            data[key] = fetch_from_api(api_type)
            print(f"{key}: 成功获取 {len(data[key])} 条")
        except Exception as e:
            data[key] = []
            print(f"{key} 失败: {e}")
            
    with open("data.js", "w", encoding="utf-8") as f:
        f.write("window.caipiaoData = " + json.dumps(data, ensure_ascii=False, indent=2) + ";")
    print("完成")

if __name__ == "__main__":
    main()
import json
import requests
from datetime import datetime
import time

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Referer": "https://www.cwl.gov.cn/"
}

def fetch_ssq():
    url = "https://www.cwl.gov.cn/cwl_admin/front/cwlkj/search/kjxx/findDrawNotice?name=ssq&issueCount=10"
    r = requests.get(url, headers=HEADERS, timeout=10)
    data = []
    if r.status_code == 200 and r.text.startswith('{'):
        res = r.json()
        for item in res.get('result', []):
            data.append({
                "issue": item['code'],
                "red": [int(x) for x in item['red'].split(',')],
                "blue": int(item['blue'])
            })
    return data

def fetch_d3():
    url = "https://www.cwl.gov.cn/cwl_admin/front/cwlkj/search/kjxx/findDrawNotice?name=3d&issueCount=10"
    r = requests.get(url, headers=HEADERS, timeout=10)
    data = []
    if r.status_code == 200 and r.text.startswith('{'):
        res = r.json()
        for item in res.get('result', []):
            data.append({
                "issue": item['code'],
                "digits": [int(x) for x in item['red'].split(',')]
            })
    return data

def fetch_tiyu(game_no, is_dlt=False):
    url = f"https://webapi.sporttery.cn/gateway/lottery/getHistoryPageListV1.qry?gameNo={game_no}&provinceId=0&pageSize=10&isVerify=1&pageNo=1"
    headers = {"User-Agent": HEADERS["User-Agent"], "Referer": "https://static.sporttery.cn/"}
    r = requests.get(url, headers=headers, timeout=10)
    data = []
    if r.status_code == 200 and r.text.startswith('{'):
        res = r.json()
        for item in res.get('value', {}).get('list', []):
            issue = item['lotteryDrawNum']
            nums = [int(x) for x in item['lotteryDrawResult'].strip().split()]
            if is_dlt:
                data.append({"issue": issue, "front": nums[:5], "back": nums[5:]})
            else:
                data.append({"issue": issue, "digits": nums})
    return data

def main():
    data = {"updateTime": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    
    fetchers = [
        ("ssq", fetch_ssq),
        ("d3", fetch_d3),
        ("dlt", lambda: fetch_tiyu("85", True)),
        ("p3", lambda: fetch_tiyu("35", False)),
        ("p5", lambda: fetch_tiyu("350133", False)),
    ]
    
    for key, fetcher in fetchers:
        for attempt in range(3): # 失败重试3次
            try:
                time.sleep(2) # 防止请求过快
                res = fetcher()
                if res:
                    data[key] = res
                    print(f"{key} 成功: {len(res)}条")
                    break
            except Exception as e:
                print(f"{key} 尝试 {attempt+1} 失败: {e}")
        else:
            data[key] = []
            
    with open("data.js", "w", encoding="utf-8") as f:
        f.write("window.caipiaoData = " + json.dumps(data, ensure_ascii=False, indent=2) + ";")
    print("完成")

if __name__ == "__main__":
    main()
