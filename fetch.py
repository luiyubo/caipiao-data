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
    # 500彩票网的表格通常放在 id="tdata" 的 tbody 里
    tbody = soup.find('tbody', id='tdata')
    trs = tbody.find_all('tr') if tbody else soup.find_all('tr', class_='t_tr1')
    
    data = []
    for tr in trs[:limit]:
        tds = tr.find_all('td')
        if not tds: continue
        # 提取所有列的文字，并去掉前后空格
        cells = [td.text.strip() for td in tds]
        if cells and cells[0].isdigit(): # 确保第一列是纯数字期号
            data.append(cells)
    return data

def fetch_ssq():
    html = fetch_page("https://datachart.500.com/ssq/history/newinc/history.php?limit=10&sort=1")
    rows = parse_500(html, 10)
    data = []
    for cells in rows:
        data.append({
            "issue": cells[0],
            "red": [int(cells[i]) for i in range(1, 7)],
            "blue": int(cells[7])
        })
    return data

def fetch_dlt():
    html = fetch_page("https://datachart.500.com/dlt/history/newinc/history.php?limit=10&sort=1")
    rows = parse_500(html, 10)
    data = []
    for cells in rows:
        data.append({
            "issue": cells[0],
            "front": [int(cells[i]) for i in range(1, 6)],
            "back": [int(cells[i]) for i in range(6, 8)]
        })
    return data

def fetch_d3():
    html = fetch_page("https://datachart.500.com/sd/history/newinc/history.php?limit=10&sort=1")
    rows = parse_500(html, 10)
    data = []
    for cells in rows:
        # 3D 的列：期号 | 试机号1 | 试机号2 | 试机号3 | 开奖号1 | 开奖号2 | 开奖号3 ...
        # 所以开奖号通常在 4,5,6 列 (索引)
        data.append({
            "issue": cells[0],
            "digits": [int(cells[4]), int(cells[5]), int(cells[6])]
        })
    return data

def fetch_p3():
    html = fetch_page("https://datachart.500.com/pls/history/newinc/history.php?limit=10&sort=1")
    rows = parse_500(html, 10)
    data = []
    for cells in rows:
        data.append({
            "issue": cells[0],
            "digits": [int(cells[1]), int(cells[2]), int(cells[3])]
        })
    return data

def fetch_p5():
    html = fetch_page("https://datachart.500.com/plw/history/newinc/history.php?limit=10&sort=1")
    rows = parse_500(html, 10)
    data = []
    for cells in rows:
        data.append({
            "issue": cells[0],
            "digits": [int(cells[i]) for i in range(1, 6)]
        })
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
