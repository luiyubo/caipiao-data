import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
}

def fetch_page(url):
    r = requests.get(url, headers=HEADERS, timeout=20)
    r.encoding = "gb2312"
    return r.text

def parse_500(html, limit=10):
    soup = BeautifulSoup(html, 'html.parser')
    tbody = soup.find('tbody', id='tdata')
    trs = tbody.find_all('tr') if tbody else soup.find_all('tr', class_='t_tr1')
    
    data = []
    for tr in trs[:limit]:
        tds = tr.find_all('td')
        if not tds: continue
        cells = [td.text.strip() for td in tds]
        if len(cells) > 2: # 确保不是空行
            data.append(cells)
    return data

def fetch_ssq():
    html = fetch_page("https://datachart.500.com/ssq/history/newinc/history.php?limit=10&sort=1")
    rows = parse_500(html, 10)
    data = []
    for cells in rows:
        try:
            # 500网: 第0列是序号，第1列是期号，第2-7列是红球，第8列是蓝球
            data.append({
                "issue": cells[1],
                "red": [int(cells[i]) for i in range(2, 8)],
                "blue": int(cells[8])
            })
        except: pass
    return data

def fetch_dlt():
    html = fetch_page("https://datachart.500.com/dlt/history/newinc/history.php?limit=10&sort=1")
    rows = parse_500(html, 10)
    data = []
    for cells in rows:
        try:
            # 500网大乐透: 第1列是期号，第2-6列是前区，第7-8列是后区
            data.append({
                "issue": cells[1],
                "front": [int(cells[i]) for i in range(2, 7)],
                "back": [int(cells[i]) for i in range(7, 9)]
            })
        except: pass
    return data

def fetch_d3():
    html = fetch_page("https://datachart.500.com/sd/history/newinc/history.php?limit=10&sort=1")
    rows = parse_500(html, 10)
    data = []
    for cells in rows:
        try:
            # 500网3D: 第1列期号，第2,3,4列是开奖号
            data.append({
                "issue": cells[1],
                "digits": [int(cells[2]), int(cells[3]), int(cells[4])]
            })
        except: pass
    return data

def fetch_p3():
    html = fetch_page("https://datachart.500.com/pls/history/newinc/history.php?limit=10&sort=1")
    rows = parse_500(html, 10)
    data = []
    for cells in rows:
        try:
            data.append({
                "issue": cells[1],
                "digits": [int(cells[2]), int(cells[3]), int(cells[4])]
            })
        except: pass
    return data

def fetch_p5():
    html = fetch_page("https://datachart.500.com/plw/history/newinc/history.php?limit=10&sort=1")
    rows = parse_500(html, 10)
    data = []
    for cells in rows:
        try:
            data.append({
                "issue": cells[1],
                "digits": [int(cells[i]) for i in range(2, 7)]
            })
        except: pass
    return data

def main():
    data = {"updateTime": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    
    fetchers = [
        ("ssq", fetch_ssq),
        ("dlt", fetch_dlt),
        ("d3",  fetch_d3),
        ("p3",  fetch_p3),
        ("p5",  fetch_p5),
    ]
    
    for key, fetcher in fetchers:
        try:
            data[key] = fetcher()
            print(f"{key}: 成功获取 {len(data[key])} 条")
        except Exception as e:
            data[key] = []
            data[key + "_error"] = str(e)
            print(f"{key} 失败: {e}")
            
    with open("data.js", "w", encoding="utf-8") as f:
        f.write("window.caipiaoData = " + json.dumps(data, ensure_ascii=False, indent=2) + ";")
    print("完成")

if __name__ == "__main__":
    main()
