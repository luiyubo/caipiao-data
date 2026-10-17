import json
import requests
from datetime import datetime
import time
import re

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"
}

def fetch_by_regex(url, kind):
    """暴力正则解析，直接抓取 500 网的真实源码，绝不报错"""
    try:
        time.sleep(1)
        r = requests.get(url, headers=HEADERS, timeout=15)
        r.encoding = 'gb2312'
        html = r.text
        
        # 提取网页中所有的表格行 <tr>
        trs = re.findall(r'<tr[^>]*>(.*?)</tr>', html, re.S)
        data = []
        
        for tr in trs:
            # 提取每一行里的单元格 <td>
            tds = re.findall(r'<td[^>]*>(.*?)</td>', tr, re.S)
            if len(tds) < 4: continue
            
            # 清洗掉 HTML 标签
            cells = [re.sub(r'<[^>]+>', '', td).strip() for td in tds]
            issue = cells[0]
            if not issue.isdigit(): continue
            
            try:
                if kind == 'ssq':
                    data.append({
                        "issue": issue, 
                        "red": [int(cells[i]) for i in range(1, 7)], 
                        "blue": int(cells[7])
                    })
                elif kind == 'dlt':
                    data.append({
                        "issue": issue, 
                        "front": [int(cells[i]) for i in range(1, 6)], 
                        "back": [int(cells[i]) for i in range(6, 8)]
                    })
                elif kind == 'd3':
                    # 3D表格：第1列是期号，第2列是试机号，第3列是开奖号
                    nums = [int(x) for x in re.findall(r'\d', cells[2])]
                    if len(nums) >= 3:
                        data.append({"issue": issue, "digits": nums[:3]})
                elif kind == 'p3':
                    # 排三表格：第1列期号，第2列开奖号
                    nums = [int(x) for x in re.findall(r'\d', cells[1])]
                    if len(nums) >= 3:
                        data.append({"issue": issue, "digits": nums[:3]})
                elif kind == 'p5':
                    # 排五表格：第1列期号，第2列开奖号
                    nums = [int(x) for x in re.findall(r'\d', cells[1])]
                    if len(nums) >= 5:
                        data.append({"issue": issue, "digits": nums[:5]})
            except:
                pass
                
            if len(data) >= 10: break
            
        return data
    except Exception as e:
        print(f"{kind} 抓取异常: {e}")
        return []

def main():
    data = {"updateTime": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    
    # 直接去 500 网真实的 newinc 接口拿数据
    urls = {
        "ssq": "https://datachart.500.com/ssq/history/newinc/history.php?limit=10&sort=1",
        "dlt": "https://datachart.500.com/dlt/history/newinc/history.php?limit=10&sort=1",
        "d3":  "https://datachart.500.com/sd/history/newinc/history.php?limit=10&sort=1",
        "p3":  "https://datachart.500.com/pls/history/newinc/history.php?limit=10&sort=1",
        "p5":  "https://datachart.500.com/plw/history/newinc/history.php?limit=10&sort=1",
    }
    
    for key, url in urls.items():
        print(f"正在抓取 {key}...")
        data[key] = fetch_by_regex(url, key)
        print(f"{key}: 成功 {len(data[key])} 条")
            
    with open("data.js", "w", encoding="utf-8") as f:
        f.write("window.caipiaoData = " + json.dumps(data, ensure_ascii=False, indent=2) + ";")
    print("全部完成")

if __name__ == "__main__":
    main()
