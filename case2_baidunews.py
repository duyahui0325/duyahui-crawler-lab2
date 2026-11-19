# -*- coding: utf-8 -*-
"""
案例2：百度新闻热点要闻爬取（教材 4.3 节，P77）

实现思路：
    1）用 requests 请求百度新闻首页，设置编码并捕获网络异常；
    2）用 BeautifulSoup（lxml 解析器）解析网页，版面由两部分组成：
       · “热点要闻”放在 class="hotnews" 的 div 中，条目在 ul>li>a 里；
       · “焦点新闻”放在 class="focuslistnews" 的 ul 中，条目在 li>a 里；
    3）每条新闻取出“标题 + 详情页链接”，写入 CSV 文件。
       部分 li 里有多个 <a>（例如“专题”链接）或占位链接 href="#"，需要过滤。

重构要点：请求、解析、存储分别封装为 get_html()、parser()、save_csv()，
main() 只负责流程控制，函数可独立复用。
"""

import csv
from pathlib import Path

import requests
from bs4 import BeautifulSoup

from spider_utils import default_headers, ensure_dir

# ==================== (1) 定义请求信息 ====================
URL = "http://www.bspider.top/baidunews/"    # 目标网页地址（教材 4.3 节）
HEADERS = default_headers()                  # 请求头（User-Agent 伪装浏览器）
TIMEOUT = 10                                 # 超时时间（秒）

BASE_DIR = Path(__file__).resolve().parent   # 当前脚本所在目录
CSV_PATH = BASE_DIR / "output" / "news.csv"      # 存储路径
CSV_HEADER = ["标题", "链接"]


# ==================== (2) 发送请求并获得响应 ====================
def get_html(url, headers, timeout=TIMEOUT):
    """发送 GET 请求，返回网页文本；编码按页面实际内容处理，异常时返回 None。"""
    try:
        resp = requests.get(url, headers=headers, timeout=timeout)
        resp.encoding = resp.apparent_encoding   # 设置编码，避免中文乱码
        resp.raise_for_status()                  # 状态码非 200 时抛出异常
        print(f"请求成功：{url}（HTTP {resp.status_code}，编码 {resp.encoding}）")
        return resp.text                         # 返回网页的文本内容
    except requests.RequestException as err:     # 超时、断网、4xx/5xx 统一捕获
        print(f"请求失败：{url} -> {err}")
        return None


# ==================== (3) 将响应数据解析并存储到本地 CSV ====================
def parse_li_list(li_list):
    """解析一组 li 条目：取每条新闻的标题和链接，跳过占位链接与重复项。"""
    rows = []
    for li in li_list:
        for a in li.select("a[href]"):           # 一个 li 里可能有多个链接
            href = a.get("href", "").strip()
            title = " ".join(a.get_text(" ", strip=True).split())  # 合并换行/多空格
            if not href or href.startswith("#") or not title:
                continue                         # 跳过 href="#" 的占位链接
            rows.append([title, href])
            break                                # 每条只取第一个有效链接
    return rows


def parser(html):
    """解析百度新闻首页，返回 [标题, 链接] 的列表。"""
    soup = BeautifulSoup(html, "lxml")           # HTML 转换为 soup 对象
    # 热点要闻：class="hotnews" 的 div 中的 ul>li>a
    hot_rows = parse_li_list(soup.select(".hotnews ul li"))
    # 焦点新闻：class="focuslistnews" 的 ul，页面里按频道有多个同名列表，
    # 只取第一个（首屏“焦点新闻”栏目），避免把其它频道的列表重复抓下来
    focus_ul = soup.select("ul.focuslistnews")
    focus_rows = parse_li_list(focus_ul[0].select("li")) if focus_ul else []

    rows, seen = [], set()
    for row in hot_rows + focus_rows:
        key = (row[0], row[1])
        if key in seen:
            continue
        seen.add(key)
        rows.append(row)
    print(f"其中热点要闻 {len(hot_rows)} 条，焦点新闻 {len(focus_rows)} 条")
    return rows


def save_csv(item, path, header=None):
    """把二维列表写入 CSV 文件；utf-8-sig 带 BOM，Excel 打开中文不乱码。"""
    path = Path(path)
    ensure_dir(path.parent)
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        csv_write = csv.writer(f)
        if header:
            csv_write.writerow(header)           # 写入表头
        csv_write.writerows(item)                # 一次性写入多行
    return path


def main():
    """主函数：整合“取网页 -> 解析 -> 存储”三个步骤。"""
    html = get_html(URL, HEADERS)                # (2) 发送请求并获得响应
    if html is None:
        return
    out_list = parser(html)                      # (3) 解析网页，得到列表数据
    if not out_list:
        print("未解析到数据，请检查页面结构是否发生变化。")
        return
    save_csv(out_list, CSV_PATH, CSV_HEADER)     # (3) 数据存储到本地 CSV

    print(f"共解析到 {len(out_list)} 条热点新闻")
    print(f"已保存：{CSV_PATH}")
    print("-" * 78)
    for i, row in enumerate(out_list[:5], start=1):
        print(f"{i}. {row[0]}")
        print(f"   {row[1]}")
    print("-" * 78)


if __name__ == "__main__":
    main()
