import json
import requests
from datetime import datetime
import pandas as pd
import time
import re
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"
}

def fetch_newinc(url, kind):
    """专门抓双色球和大乐透"""
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

def fetch_500_html(url, kind):
    """专门抓 3D、排三、排五，用 BS4 强解"""
    try:
        time.sleep(1)
        r = requests.get(url, headers=HEADERS, timeout=15)
        r.encoding = 'gb2312'
        soup = BeautifulSoup(r.text, 'html.parser')
        
        # 500网的表格一般在 tbody id="tdata" 里
        tbody = soup.find('tbody', id='tdata')
        if not tbody:
            # 备用：直接找所有的 tr
            trs = soup.find_all('tr')
        else:
            trs = tbody.find_all('tr')
            
        data = []
        for tr in trs:
            tds = tr.find_all('td')
            if len(tds) < 3: continue
            
            issue = tds[0].text.strip()
            if not issue.isdigit(): continue
            
            if kind == 'd3':
                # 3D 的表格：期号, 试机号, 开奖号
                code_str = tds[2].text.strip() if len(tds) > 2 else ""
                nums = [int(x) for x in re.findall(r'\d', code_str)]
                if len(nums) == 3:
                    data.append({"issue": issue, "digits": nums})
            elif kind == 'p3':
                # 排三的表格：期号, 开奖号
                code_str = tds[1].text.strip()
                nums = [int(x) for x in re.findall(r'\d', code_str)]
                if len(nums) >= 3:
                    data.append({"issue": issue, "digits": nums[:3]})
            elif kind == 'p5':
                # 排五的表格：期号, 开奖号
                code_str = tds[1].text.strip()
                nums = [int(x) for x in re.findall(r'\d', code_str)]
                if len(nums) >= 5:
                    data.append({"issue": issue, "digits": nums[:5]})
                    
            if len(data) >= 10: break
            
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
    
    # 3D 用 sd 路径，排三用 pls 路径，排五用 plw 路径
    print("正在抓取 d3...")
    data["d3"] = fetch_500_html("https://datachart.500.com/sd/history/history.shtml", "d3")
    print(f"d3: 成功 {len(data['d3'])} 条")
    
    print("正在抓取 p3...")
    data["p3"] = fetch_500_html("https://datachart.500.com/pls/history/history.shtml", "p3")
    print(f"p3: 成功 {len(data['p3'])} 条")
    
    print("正在抓取 p5...")
    data["p5"] = fetch_500_html("https://datachart.500.com/plw/history/history.shtml", "p5")
    print(f"p5: 成功 {len(data['p5'])} 条")
            
    with open("data.js", "w", encoding="utf-8") as f:
        f.write("window.caipiaoData = " + json.dumps(data, ensure_ascii=False, indent=2) + ";")
    print("全部完成")

if __name__ == "__main__":
    main()
