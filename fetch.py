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
    """双色球、大乐透专用（因为它们的接口很稳定）"""
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
        return []

def fetch_html_brute(url, kind):
    """3D、排三、排五专用：暴力扫描网页所有表格行"""
    try:
        time.sleep(1)
        r = requests.get(url, headers=HEADERS, timeout=15)
        r.encoding = 'gb2312'
        soup = BeautifulSoup(r.text, 'html.parser')
        
        # 不管三七二十一，把网页里所有的 tr (行) 全找出来
        trs = soup.find_all('tr')
        data = []
        
        for tr in trs:
            tds = tr.find_all('td')
            if len(tds) < 4: continue # 列数太少，跳过
            
            # 第 0 列通常是期号
            issue_text = tds[0].text.strip()
            if not issue_text.isdigit(): continue
            
            issue = issue_text
            
            # 提取这一行所有的文本
            cells = [td.text.strip() for td in tds]
            
            if kind == 'd3':
                # 3D 的格式：期号，日期，试机号，开奖号...
                # 我们把带有数字的列拼起来找
                for cell in cells[1:]:
                    nums = [int(x) for x in re.findall(r'\d', cell)]
                    if len(nums) == 3:
                        data.append({"issue": issue, "digits": nums})
                        break
            elif kind in ['p3', 'p5']:
                # 排三/排五：通常第 1 列或者第 2 列就是开奖号
                for cell in cells[1:]:
                    nums = [int(x) for x in re.findall(r'\d', cell)]
                    if kind == 'p3' and len(nums) == 3:
                        data.append({"issue": issue, "digits": nums})
                        break
                    if kind == 'p5' and len(nums) == 5:
                        data.append({"issue": issue, "digits": nums})
                        break
                        
            if len(data) >= 10: break
            
        return data
    except Exception as e:
        print(f"{kind} 解析异常: {e}")
        return []

def main():
    data = {"updateTime": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    
    print("正在抓取 ssq...")
    data["ssq"] = fetch_newinc("https://datachart.500.com/ssq/history/newinc/history.php?limit=10&sort=1", "ssq")
    print(f"ssq: 成功 {len(data['ssq'])} 条")
    
    print("正在抓取 dlt...")
    data["dlt"] = fetch_newinc("https://datachart.500.com/dlt/history/newinc/history.php?limit=10&sort=1", "dlt")
    print(f"dlt: 成功 {len(data['dlt'])} 条")
    
    # 3D、排三、排五，使用历史页面，暴力抓取
    print("正在抓取 d3...")
    data["d3"] = fetch_html_brute("https://datachart.500.com/sd/history/history.shtml", "d3")
    print(f"d3: 成功 {len(data['d3'])} 条")
    
    print("正在抓取 p3...")
    data["p3"] = fetch_html_brute("https://datachart.500.com/pls/history/history.shtml", "p3")
    print(f"p3: 成功 {len(data['p3'])} 条")
    
    print("正在抓取 p5...")
    data["p5"] = fetch_html_brute("https://datachart.500.com/plw/history/history.shtml", "p5")
    print(f"p5: 成功 {len(data['p5'])} 条")
            
    with open("data.js", "w", encoding="utf-8") as f:
        f.write("window.caipiaoData = " + json.dumps(data, ensure_ascii=False, indent=2) + ";")
    print("全部完成")

if __name__ == "__main__":
    main()
