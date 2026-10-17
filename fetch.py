import json
import re
import requests
from datetime import datetime

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
}

def fetch_page(url):
    r = requests.get(url, headers=HEADERS, timeout=20)
    r.encoding = "gb2312"
    return r.text

def parse_rows(html, limit=10):
    rows = re.findall(r'<tr class="t_tr1">(.*?)</tr>', html, re.S)
    result = []
    for row in rows[:limit]:
        cells = re.findall(r'<td[^>]*>(.*?)</td>', row, re.S)
        cells = [re.sub(r'<[^>]+>', '', c).strip() for c in cells]
        result.append(cells)
    return result

def fetch_ssq():
    html = fetch_page("https://datachart.500.com/ssq/history/newinc/history.php?limit=10&sort=1")
    data = []
    for cells in parse_rows(html, 10):
        if len(cells) < 8: continue
        data.append({
            "issue": cells[0],
            "red": [int(cells[i]) for i in range(1, 7)],
            "blue": int(cells[7])
        })
    return data

def fetch_dlt():
    html = fetch_page("https://datachart.500.com/dlt/history/newinc/history.php?limit=10&sort=1")
    data = []
    for cells in parse_rows(html, 10):
        if len(cells) < 8: continue
        data.append({
            "issue": cells[0],
            "front": [int(cells[i]) for i in range(1, 6)],
            "back": [int(cells[i]) for i in range(6, 8)]
        })
    return data

def fetch_d3():
    html = fetch_page("https://datachart.500.com/sd/history/newinc/history.php?limit=10&sort=1")
    data = []
    for cells in parse_rows(html, 10):
        if len(cells) < 4: continue
        data.append({
            "issue": cells[0],
            "digits": [int(cells[i]) for i in range(1, 4)]
        })
    return data

def fetch_p3():
    html = fetch_page("https://datachart.500.com/pls/history/newinc/history.php?limit=10&sort=1")
    data = []
    for cells in parse_rows(html, 10):
        if len(cells) < 4: continue
        data.append({
            "issue": cells[0],
            "digits": [int(cells[i]) for i in range(1, 4)]
        })
    return data

def fetch_p5():
    html = fetch_page("https://datachart.500.com/plw/history/newinc/history.php?limit=10&sort=1")
    data = []
    for cells in parse_rows(html, 10):
        if len(cells) < 6: continue
        data.append({
            "issue": cells[0],
            "digits": [int(cells[i]) for i in range(1, 6)]
        })
    return data

def main():
    data = {"updateTime": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    
    for key, fetcher in [
        ("ssq", fetch_ssq),
        ("dlt", fetch_dlt),
        ("d3",  fetch_d3),
        ("p3",  fetch_p3),
        ("p5",  fetch_p5),
    ]:
        try:
            data[key] = fetcher()
            print(f"{key}: {len(data[key])} 条")
        except Exception as e:
            data[key] = []
            data[key + "_error"] = str(e)
            print(f"{key} 失败: {e}")
    with open("data.js", "w", encoding="utf-8") as f:
    f.write("window.caipiaoData = " + json.dumps(data, ensure_ascii=False, indent=2) + ";")
    print("完成")

if __name__ == "__main__":
    main()
