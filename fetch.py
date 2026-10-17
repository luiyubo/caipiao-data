import json
import requests
from datetime import datetime
import pandas as pd
import time

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"
}

def fetch_data(url, kind):
    try:
        time.sleep(1)
        # Pandas 直接读取网页中的表格，无视反爬和乱码
        dfs = pd.read_html(url, encoding='gb2312')
        df = dfs[0]
        data = []
        for _, row in df.head(10).iterrows():
            issue = str(row[0]) # 期号
            if kind == 'ssq':
                data.append({
                    "issue": issue,
                    "red": [int(row[i]) for i in range(1, 7)],
                    "blue": int(row[7])
                })
            elif kind == 'dlt':
                data.append({
                    "issue": issue,
                    "front": [int(row[i]) for i in range(1, 6)],
                    "back": [int(row[i]) for i in range(6, 8)]
                })
            elif kind in ['d3', 'p3']:
                # 3D 和排三，取后面3位开奖号
                data.append({
                    "issue": issue,
                    "digits": [int(row[1]), int(row[2]), int(row[3])]
                })
            elif kind == 'p5':
                # 排五，取后面5位开奖号
                data.append({
                    "issue": issue,
                    "digits": [int(row[i]) for i in range(1, 6)]
                })
        return data
    except Exception as e:
        print(f"{kind} 抓取失败: {e}")
        return []

def main():
    data = {"updateTime": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    
    # ★ 这里把网址后缀全改成了正确的 3d, p3, p5
    urls = {
        "ssq": "https://datachart.500.com/ssq/history/newinc/history.php?limit=10&sort=1",
        "dlt": "https://datachart.500.com/dlt/history/newinc/history.php?limit=10&sort=1",
        "d3":  "https://datachart.500.com/3d/history/newinc/history.php?limit=10&sort=1",
        "p3":  "https://datachart.500.com/p3/history/newinc/history.php?limit=10&sort=1",
        "p5":  "https://datachart.500.com/p5/history/newinc/history.php?limit=10&sort=1",
    }
    
    for key, url in urls.items():
        print(f"正在抓取 {key}...")
        data[key] = fetch_data(url, key)
        print(f"{key}: 成功获取 {len(data[key])} 条")
            
    with open("data.js", "w", encoding="utf-8") as f:
        f.write("window.caipiaoData = " + json.dumps(data, ensure_ascii=False, indent=2) + ";")
    print("全部完成")

if __name__ == "__main__":
    main()
