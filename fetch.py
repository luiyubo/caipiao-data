import json
import requests
from datetime import datetime
import pandas as pd
import time
import re

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"
}

def fetch_500(url, kind):
    """双色球、大乐透专用（500网稳定接口）"""
    try:
        time.sleep(1)
        dfs = pd.read_html(url, encoding='gb2312')
        df = dfs[0]
        data = []
        for _, row in df.head(10).iterrows():
            issue = str(row[0])
            if not issue.isdigit(): continue
            if kind == 'ssq':
                data.append({"issue": issue, "red": [int(row[i]) for i in range(1, 7)], "blue": int(row[7])})
            elif kind == 'dlt':
                data.append({"issue": issue, "front": [int(row[i]) for i in range(1, 6)], "back": [int(row[i]) for i in range(6, 8)]})
        return data
    except Exception as e:
        print(f"500接口 {kind} 失败: {e}")
        return []

def fetch_sina(api_type, kind):
    """3D、排三、排五专用（新浪彩票稳定接口）"""
    try:
        time.sleep(1)
        url = f"https://match.lottery.sina.com.cn/api/v1/lottery/history?type={api_type}&num=10"
        headers = {
            "User-Agent": HEADERS["User-Agent"],
            "Referer": "https://match.lottery.sina.com.cn/"
        }
        r = requests.get(url, headers=headers, timeout=15)
        res = r.json()
        data = []
        # 解析新浪返回的 JSON
        if res.get('result') and res['result'].get('status', {}).get('code') == 0:
            for item in res['result'].get('data', []):
                issue = item['issue']
                # openCode 比如 "1 2 3" 或 "1,2,3"
                code_str = item['openCode']
                nums = [int(x) for x in re.findall(r'\d+', code_str)]
                
                if kind == 'd3' and len(nums) >= 3:
                    data.append({"issue": issue, "digits": nums[:3]})
                elif kind == 'p3' and len(nums) >= 3:
                    data.append({"issue": issue, "digits": nums[:3]})
                elif kind == 'p5' and len(nums) >= 5:
                    data.append({"issue": issue, "digits": nums[:5]})
        return data
    except Exception as e:
        print(f"新浪接口 {kind} 失败: {e}")
        return []

def main():
    data = {"updateTime": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    
    print("正在抓取 ssq...")
    data["ssq"] = fetch_500("https://datachart.500.com/ssq/history/newinc/history.php?limit=10&sort=1", "ssq")
    print(f"ssq: 成功 {len(data['ssq'])} 条")
    
    print("正在抓取 dlt...")
    data["dlt"] = fetch_500("https://datachart.500.com/dlt/history/newinc/history.php?limit=10&sort=1", "dlt")
    print(f"dlt: 成功 {len(data['dlt'])} 条")
    
    print("正在抓取 d3...")
    data["d3"] = fetch_sina("fc3d", "d3")
    print(f"d3: 成功 {len(data['d3'])} 条")
    
    print("正在抓取 p3...")
    data["p3"] = fetch_sina("pl3", "p3")
    print(f"p3: 成功 {len(data['p3'])} 条")
    
    print("正在抓取 p5...")
    data["p5"] = fetch_sina("pl5", "p5")
    print(f"p5: 成功 {len(data['p5'])} 条")
            
    with open("data.js", "w", encoding="utf-8") as f:
        f.write("window.caipiaoData = " + json.dumps(data, ensure_ascii=False, indent=2) + ";")
    print("全部完成")

if __name__ == "__main__":
    main()
