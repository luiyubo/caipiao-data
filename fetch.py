import json
import requests
from datetime import datetime
import time
import re

# 加上重试机制的请求头
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
    "Connection": "keep-alive"
}

def fetch_with_retry(url, kind, max_retries=3):
    """带重试机制的抓取函数，专治超时"""
    for attempt in range(max_retries):
        try:
            # 每次请求前睡 3 秒，防止被拉黑
            time.sleep(3) 
            r = requests.get(url, headers=HEADERS, timeout=20)
            r.encoding = 'gb2312'
            html = r.text
            
            trs = re.findall(r'<tr[^>]*>(.*?)</tr>', html, re.S)
            data = []
            
            for tr in trs:
                tds = re.findall(r'<td[^>]*>(.*?)</td>', tr, re.S)
                if len(tds) < 4: continue
                
                cells = [re.sub(r'<[^>]+>', '', td).strip() for td in tds]
                issue = cells[0]
                if not issue.isdigit(): continue
                
                try:
                    if kind == 'ssq':
                        data.append({"issue": issue, "red": [int(cells[i]) for i in range(1, 7)], "blue": int(cells[7])})
                    elif kind == 'dlt':
                        data.append({"issue": issue, "front": [int(cells[i]) for i in range(1, 6)], "back": [int(cells[i]) for i in range(6, 8)]})
                    elif kind == 'd3':
                        nums = [int(x) for x in re.findall(r'\d', cells[2])]
                        if len(nums) >= 3: data.append({"issue": issue, "digits": nums[:3]})
                    elif kind == 'p3':
                        nums = [int(x) for x in re.findall(r'\d', cells[1])]
                        if len(nums) >= 3: data.append({"issue": issue, "digits": nums[:3]})
                    elif kind == 'p5':
                        nums = [int(x) for x in re.findall(r'\d', cells[1])]
                        if len(nums) >= 5: data.append({"issue": issue, "digits": nums[:5]})
                except:
                    pass
                    
                if len(data) >= 10: break
                
            if len(data) > 0:
                return data # 抓到数据了，直接返回
            else:
                print(f"{kind} 第 {attempt+1} 次尝试未找到数据，准备重试...")
                
        except Exception as e:
            print(f"{kind} 第 {attempt+1} 次超时/失败: {e}")
            time.sleep(5) # 超时了多等一会儿
            
    print(f"{kind} 连续 {max_retries} 次失败，放弃抓取。")
    return []

def main():
    data = {"updateTime": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    
    urls = {
        "ssq": "https://datachart.500.com/ssq/history/newinc/history.php?limit=10&sort=1",
        "dlt": "https://datachart.500.com/dlt/history/newinc/history.php?limit=10&sort=1",
        "d3":  "https://datachart.500.com/sd/history/newinc/history.php?limit=10&sort=1",
        "p3":  "https://datachart.500.com/pls/history/newinc/history.php?limit=10&sort=1",
        "p5":  "https://datachart.500.com/plw/history/newinc/history.php?limit=10&sort=1",
    }
    
    for key, url in urls.items():
        print(f"正在抓取 {key}...")
        data[key] = fetch_with_retry(url, key)
        print(f"{key}: 最终成功 {len(data[key])} 条")
            
    with open("data.js", "w", encoding="utf-8") as f:
        f.write("window.caipiaoData = " + json.dumps(data, ensure_ascii=False, indent=2) + ";")
    print("全部完成")

if __name__ == "__main__":
    main()
