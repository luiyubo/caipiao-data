import json
import requests
from datetime import datetime
import time
import re

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"
}

def fetch_with_retry(url, kind, max_retries=3):
    for attempt in range(max_retries):
        try:
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
                
                # ★ 智能识别期号：遍历这行所有单元格，找到第一个长度 >= 5 的纯数字
                issue_idx = -1
                issue = ""
                for i, cell in enumerate(cells):
                    if cell.isdigit() and len(cell) >= 5:
                        issue = cell
                        issue_idx = i
                        break
                        
                if issue_idx == -1: continue # 没找到期号，跳过这行
                
                try:
                    # 以找到的期号为基准，往后顺延提取号码
                    if kind == 'ssq':
                        data.append({"issue": issue, "red": [int(cells[issue_idx+i]) for i in range(1, 7)], "blue": int(cells[issue_idx+7])})
                    elif kind == 'dlt':
                        data.append({"issue": issue, "front": [int(cells[issue_idx+i]) for i in range(1, 6)], "back": [int(cells[issue_idx+i]) for i in range(6, 8)]})
                    elif kind in ['d3', 'p3', 'p5']:
                        # 3D/排三/排五：直接全篇搜对应长度的数字
                        target_len = 5 if kind == 'p5' else 3
                        nums = []
                        for cell in cells:
                            found = [int(x) for x in re.findall(r'\d', cell)]
                            if len(found) == target_len:
                                nums = found
                                break
                        if len(nums) == target_len:
                            data.append({"issue": issue, "digits": nums})
                except Exception as e:
                    pass
                    
                if len(data) >= 10: break
                
            if len(data) > 0:
                return data
            else:
                print(f"{kind} 第 {attempt+1} 次尝试未找到数据，准备重试...")
                
        except Exception as e:
            print(f"{kind} 第 {attempt+1} 次超时/失败: {e}")
            time.sleep(5)
            
    return []

def main():
    data = {"updateTime": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    
    urls = {
        "ssq": "https://datachart.500.com/ssq/history/newinc/history.php?limit=10&sort=1",
        "dlt": "https://datachart.500.com/dlt/history/newinc/history.php?limit=10&sort=1",
        "d3":  "https://datachart.500.com/sd/history/inc/history.php?limit=10",
        "p3":  "https://datachart.500.com/pls/history/inc/history.php?limit=10",
        "p5":  "https://datachart.500.com/plw/history/inc/history.php?limit=10",
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
