import json
import requests
from datetime import datetime
import pandas as pd
import time
import re

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

def fetch_ssq_dlt(url, kind):
    """双色球和大乐透的专用逻辑"""
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
        print(f"{kind} 抓取失败: {e}")
        return []

def fetch_digit_lottery(url, kind):
    """3D/排三/排五的真实接口与解析逻辑"""
    try:
        time.sleep(1)
        # 直接请求真实的数据接口
        r = requests.get(url, headers=HEADERS, timeout=15)
        r.encoding = 'gb2312'
        
        # 用 pandas 直接读取网页中的表格
        dfs = pd.read_html(r.text)
        if not dfs: return []
        df = dfs[0]
        
        data = []
        for _, row in df.head(10).iterrows():
            # 3D/排三/排五的第 0 列是期号，第 1 列是开奖号码
            issue = str(row[0])
            if not issue.isdigit(): continue
            
            code_str = str(row[1])
            nums = [int(x) for x in re.findall(r'\d', code_str)]
            
            if kind == 'd3' and len(nums) >= 3:
                data.append({"issue": issue, "digits": nums[:3]})
            elif kind == 'p3' and len(nums) >= 3:
                data.append({"issue": issue, "digits": nums[:3]})
            elif kind == 'p5' and len(nums) >= 5:
                data.append({"issue": issue, "digits": nums[:5]})
        return data
    except Exception as e:
        print(f"{kind} 抓取失败: {e}")
        return []

def main():
    data = {"updateTime": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    
    # 双色球、大乐透（保持不变）
    print("正在抓取 ssq...")
    data["ssq"] = fetch_ssq_dlt("https://datachart.500.com/ssq/history/newinc/history.php?limit=10&sort=1", "ssq")
    print(f"ssq: 成功 {len(data['ssq'])} 条")
    
    print("正在抓取 dlt...")
    data["dlt"] = fetch_ssq_dlt("https://datachart.500.com/dlt/history/newinc/history.php?limit=10&sort=1", "dlt")
    print(f"dlt: 成功 {len(data['dlt'])} 条")

    # ★ 3D、排三、排五：使用真实的 500 彩票网路径和后缀
    print("正在抓取 d3...")
    data["d3"] = fetch_digit_lottery("https://datachart.500.com/sd/history/newinc/history.php?limit=10&sort=1", "d3")
    print(f"d3: 成功 {len(data['d3'])} 条")
    
    print("正在抓取 p3...")
    data["p3"] = fetch_digit_lottery("https://datachart.500.com/pls/history/newinc/history.php?limit=10&sort=1", "p3")
    print(f"p3: 成功 {len(data['p3'])} 条")
    
    print("正在抓取 p5...")
    data["p5"] = fetch_digit_lottery("https://datachart.500.com/plw/history/newinc/history.php?limit=10&sort=1", "p5")
    print(f"p5: 成功 {len(data['p5'])} 条")
            
    with open("data.js", "w", encoding="utf-8") as f:
        f.write("window.caipiaoData = " + json.dumps(data, ensure_ascii=False, indent=2) + ";")
    print("全部完成")

if __name__ == "__main__":
    main()
