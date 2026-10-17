import json
import requests
from datetime import datetime
import pandas as pd
import time
import re

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"
}

def fetch_newinc(url, kind):
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

def fetch_shtml(url, kind):
    try:
        time.sleep(1)
        # 改为请求网页源码
        r = requests.get(url, headers=HEADERS, timeout=15)
        r.encoding = 'gb2312'
        # 提取网页中的所有表格
        dfs = pd.read_html(r.text)
        if not dfs: return []
        df = dfs[0]
        data = []
        for _, row in df.head(10).iterrows():
            issue = str(row[0])
            if not issue.isdigit(): continue
            
            # 提取对应的开奖号码
            if kind == 'd3':
                # 3D 表格：期号(0), 试机号(1), 开奖号(2)
                code_str = str(row[2]) 
                nums = [int(x) for x in re.findall(r'\d', code_str)]
                if len(nums) >= 3:
                    data.append({"issue": issue, "digits": nums[:3]})
            elif kind == 'p3':
                # 排三表格：期号(0), 开奖号(1)
                code_str = str(row[1])
                nums = [int(x) for x in re.findall(r'\d', code_str)]
                if len(nums) >= 3:
                    data.append({"issue": issue, "digits": nums[:3]})
            elif kind == 'p5':
                code_str = str(row[1])
                nums = [int(x) for x in re.findall(r'\d', code_str)]
                if len(nums) >= 5:
                    data.append({"issue": issue, "digits": nums[:5]})
        return data
    except Exception as e:
        print(f"{kind} 网页解析失败: {e}")
        return []

def main():
    data = {"updateTime": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    
    print("正在抓取 ssq...")
    data["ssq"] = fetch_newinc("https://datachart.500.com/ssq/history/newinc/history.php?limit=10&sort=1", "ssq")
    print(f"ssq: 成功 {len(data['ssq'])} 条")
    
    print("正在抓取 dlt...")
    data["dlt"] = fetch_newinc("https://datachart.500.com/dlt/history/newinc/history.php?limit=10&sort=1", "dlt")
    print(f"dlt: 成功 {len(data['dlt'])} 条")
    
    # 3D、排三、排五改用直接抓取历史网页
    print("正在抓取 d3...")
    data["d3"] = fetch_shtml("https://datachart.500.com/3d/history/history.shtml", "d3")
    print(f"d3: 成功 {len(data['d3'])} 条")
    
    print("正在抓取 p3...")
    data["p3"] = fetch_shtml("https://datachart.500.com/pls/history/history.shtml", "p3")
    print(f"p3: 成功 {len(data['p3'])} 条")
    
    print("正在抓取 p5...")
    data["p5"] = fetch_shtml("https://datachart.500.com/plw/history/history.shtml", "p5")
    print(f"p5: 成功 {len(data['p5'])} 条")
            
    with open("data.js", "w", encoding="utf-8") as f:
        f.write("window.caipiaoData = " + json.dumps(data, ensure_ascii=False, indent=2) + ";")
    print("全部完成")

if __name__ == "__main__":
    main()
