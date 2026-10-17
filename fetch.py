import json
import requests
from datetime import datetime

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Referer": "https://www.cwl.gov.cn/"
}

def fetch_ssq():
    """抓取双色球官方 API"""
    url = "https://www.cwl.gov.cn/cwl_admin/front/cwlkj/search/kjxx/findDrawNotice?name=ssq&issueCount=10"
    r = requests.get(url, headers=HEADERS, timeout=15)
    json_data = r.json()
    data = []
    if json_data.get('result'):
        for item in json_data['result']:
            data.append({
                "issue": item['code'],
                "red": [int(x) for x in item['red'].split(',')],
                "blue": int(item['blue'])
            })
    return data

def fetch_d3():
    """抓取福彩3D官方 API"""
    url = "https://www.cwl.gov.cn/cwl_admin/front/cwlkj/search/kjxx/findDrawNotice?name=3d&issueCount=10"
    r = requests.get(url, headers=HEADERS, timeout=15)
    json_data = r.json()
    data = []
    if json_data.get('result'):
        for item in json_data['result']:
            data.append({
                "issue": item['code'],
                "digits": [int(x) for x in item['red'].split(',')]
            })
    return data

def fetch_sporttery(game_no, is_dlt=False):
    """抓取体彩官方 API (大乐透/排三/排五)"""
    url = f"https://webapi.sporttery.cn/gateway/lottery/getHistoryPageListV1.qry?gameNo={game_no}&provinceId=0&pageSize=10&isVerify=1&pageNo=1"
    headers = {"User-Agent": "Mozilla/5.0", "Referer": "https://www.sporttery.cn/"}
    r = requests.get(url, headers=headers, timeout=15)
    json_data = r.json()
    data = []
    if json_data.get('value') and json_data['value'].get('list'):
        for item in json_data['value']['list']:
            issue = item['lotteryDrawNum']
            res_str = item['lotteryDrawResult'].strip()
            nums = [int(x) for x in res_str.split()]
            if is_dlt:
                data.append({"issue": issue, "front": nums[:5], "back": nums[5:]})
            else:
                data.append({"issue": issue, "digits": nums})
    return data

def main():
    data = {"updateTime": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    
    fetchers = [
        ("ssq", fetch_ssq),
        ("d3",  fetch_d3),
        ("dlt", lambda: fetch_sporttery("85", is_dlt=True)),
        ("p3",  lambda: fetch_sporttery("35", is_dlt=False)),
        ("p5",  lambda: fetch_sporttery("350133", is_dlt=False)),
    ]
    
    for key, fetcher in fetchers:
        try:
            data[key] = fetcher()
            print(f"{key}: 成功获取 {len(data[key])} 条")
        except Exception as e:
            data[key] = []
            data[key + "_error"] = str(e)
            print(f"{key} 失败: {e}")
            
    with open("data.js", "w", encoding="utf-8") as f:
        f.write("window.caipiaoData = " + json.dumps(data, ensure_ascii=False, indent=2) + ";")
    print("完成")

if __name__ == "__main__":
    main()
