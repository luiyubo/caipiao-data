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
