# -*- coding: utf-8 -*-
"""
案例1：中国大学排名爬取存储（教材 4.2 节，P73）

实现思路：
    1）用 requests 请求“高三网”中国大学排名页，设置编码并捕获网络异常；
    2）用 BeautifulSoup（lxml 解析器）解析网页，CSS 选择器
       “table>tbody>tr” 定位表格行，再在每行内二次查找 td 单元格；
    3）按“学校名称、总分、全国排名、星级排名、办学层次”的顺序取出数据，
       去掉表头行，保存为逗号分隔的 CSV 文件（Excel 可直接打开）。

重构要点：请求、解析、存储分别封装为 get_html()、parser()、save_csv()，
main() 只负责流程控制，函数可独立复用。
"""

import csv
from pathlib import Path

import requests
from bs4 import BeautifulSoup

from spider_utils import default_headers, ensure_dir

# ==================== (1) 定义请求信息 ====================
URL = "http://www.bspider.top/gaosan/"       # 目标网页地址（教材 4.2 节）
HEADERS = default_headers()                  # 请求头（User-Agent 伪装浏览器）
TIMEOUT = 10                                 # 超时时间（秒）

BASE_DIR = Path(__file__).resolve().parent   # 当前脚本所在目录
CSV_PATH = BASE_DIR / "output" / "school.csv"   # 存储路径
CSV_HEADER = ["学校名称", "总分", "全国排名", "星级排名", "办学层次"]


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
def parser(html):
    """解析排名表格，返回 [学校名称, 总分, 全国排名, 星级排名, 办学层次] 列表。"""
    soup = BeautifulSoup(html, "lxml")           # HTML 转换为 soup 对象
    out_list = []
    for row in soup.select("table>tbody>tr"):    # 循环遍历表格的每一行
        td_html = row.select("td")               # 在行内二次查找单元格
        if len(td_html) < 6:                     # 列数不足的行直接跳过
            continue
        if not td_html[0].text.strip().isdigit():   # 跳过第一行表头（“名次”）
            continue
        row_data = [
            td_html[1].text.strip(),             # 学校名称
            td_html[2].text.strip(),             # 总分
            td_html[3].text.strip(),             # 全国排名
            td_html[4].text.strip(),             # 星级排名
            td_html[5].text.strip(),             # 办学层次
        ]
        out_list.append(row_data)                # 每行数据插入输出列表
    return out_list


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

    print(f"共解析到 {len(out_list)} 条高校排名数据")
    print(f"已保存：{CSV_PATH}")
    print("-" * 78)
    print(" | ".join(CSV_HEADER))
    for row in out_list[:5]:
        print(" | ".join(row))
    print("-" * 78)


if __name__ == "__main__":
    main()
