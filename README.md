# 实验2 网页解析（requests + BeautifulSoup）

> 代码仓库：<https://github.com/duyahui0325/duyahui-crawler-lab2>

用 `requests` 获取网页源码，再用 `BeautifulSoup(lxml)` 和 CSS 选择器解析网页，
完成教材 4.2 节“中国大学排名爬取”和 4.3 节“百度新闻爬取”两个案例，结果保存为 CSV 文件。

## 一、实验内容

| 案例 | 目标网页 | 提取内容 | 结果文件 |
| --- | --- | --- | --- |
| 案例1 中国大学排名爬取 | http://www.bspider.top/gaosan/ | 学校名称、总分、全国排名、星级排名、办学层次 | `output/school.csv` |
| 案例2 百度新闻爬取 | http://www.bspider.top/baidunews/ | “热点要闻”的新闻标题、详情页链接 | `output/news.csv` |

## 二、目录结构

```
网页解析/
├── case1_gaosan.py        # 案例1：中国大学排名爬取
├── case2_baidunews.py     # 案例2：百度新闻爬取
├── spider_utils.py        # 公共工具：请求头、目录创建
├── requirements.txt       # 依赖清单
├── output/
│   ├── school.csv         # 案例1 结果（1 行表头 + 820 行数据）
│   └── news.csv           # 案例2 结果（1 行表头 + 10 行数据）
└── README.md
```

## 三、运行方法

```bash
# 1. 创建并激活虚拟环境（Windows）
python -m venv .venv
.venv\Scripts\activate

# 2. 安装依赖
pip install -r requirements.txt

# 3. 运行两个案例
python case1_gaosan.py
python case2_baidunews.py
```

两个脚本都会自动创建 `output` 目录，运行结束后在控制台打印前 5 条结果。

## 四、运行结果

案例1：

```
请求成功: http://www.bspider.top/gaosan/ (HTTP 200, 编码 utf-8)
共解析到 820 条高校排名数据
已保存: ...\output\school.csv
```

案例2：

```
请求成功: http://www.bspider.top/baidunews/ (HTTP 200, 编码 utf-8)
其中热点要闻 4 条, 焦点新闻 6 条
共解析到 10 条热点新闻
已保存: ...\output\news.csv
```

## 五、关键实现

1. **请求网页**：`requests.get()` 发送 GET 请求，`resp.encoding = resp.apparent_encoding`
   按页面真实编码解码，`resp.raise_for_status()` 检查状态码，`try…except requests.RequestException`
   捕获超时、断网等网络访问异常。
2. **解析表格（二次查找）**：先用 `soup.select("table>tbody>tr")` 取出全部数据行，
   再在每一行内用 `row.select("td")` 取单元格，跳过列数不足的行和第一行表头。
3. **解析新闻列表**：`div.hotnews` 下取热点新闻，第一个 `ul.focuslistnews` 下取焦点新闻；
   过滤 `href="#"` 的占位链接，每条只取第一个有效链接，并按（标题，链接）去重。
4. **存储 CSV**：`csv.writer` 逐行写入，`open(..., newline="", encoding="utf-8-sig")`
   防止 Windows 下多出空行，并让 Excel 双击打开时中文不乱码。

## 六、实验报告

实验报告位于 `../工作区/大数据采集与处理实验报告-2-杜亚辉-112404150221-软件1242.docx`，
PDF 版本为 `../工作区/报告final.pdf`。
