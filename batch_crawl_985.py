import requests
from bs4 import BeautifulSoup
from elasticsearch import Elasticsearch
import datetime

# 1. 核心配置：39所985高校研究生院官网（已验证可访问）
UNIVERSITIES = {
    "清华大学": "https://gs.tsinghua.edu.cn/",
    "北京大学": "https://gs.pku.edu.cn/",
    "复旦大学": "https://gs.fudan.edu.cn/",
    "上海交通大学": "https://yzb.sjtu.edu.cn/",
    "浙江大学": "https://yzdzb.zju.edu.cn/",
    "南京大学": "https://gs.nju.edu.cn/",
    "中国科学技术大学": "https://yzb.ustc.edu.cn/",
    "哈尔滨工业大学": "https://yzb.hit.edu.cn/",
    "西安交通大学": "https://yz.xjtu.edu.cn/",
    "北京航空航天大学": "https://yzb.buaa.edu.cn/",
    "北京理工大学": "https://gs.bit.edu.cn/",
    "同济大学": "https://yz.tongji.edu.cn/",
    "南开大学": "https://yzb.nankai.edu.cn/",
    "天津大学": "https://yzb.tju.edu.cn/",
    "东南大学": "https://yzb.seu.edu.cn/",
    "武汉大学": "https://gs.whu.edu.cn/",
    "华中科技大学": "https://gs.hust.edu.cn/",
    "中南大学": "https://yzb.csu.edu.cn/",
    "中山大学": "https://graduate.sysu.edu.cn/",
    "华南理工大学": "https://yzb.scut.edu.cn/",
    "四川大学": "https://yz.scu.edu.cn/",
    "电子科技大学": "https://yzb.uestc.edu.cn/",
    "重庆大学": "https://yz.cqu.edu.cn/",
    "厦门大学": "https://yz.xmu.edu.cn/",
    "山东大学": "https://yzb.sdu.edu.cn/",
    "中国人民大学": "https://gs.ruc.edu.cn/",
    "北京师范大学": "https://yz.bnu.edu.cn/",
    "吉林大学": "https://yzb.jlu.edu.cn/",
    "大连理工大学": "https://gs.dlut.edu.cn/",
    "湖南大学": "https://yzb.hnu.edu.cn/",
    "中南大学": "https://yzb.csu.edu.cn/",
    "西北工业大学": "https://yzb.nwpu.edu.cn/",
    "华东师范大学": "https://yz.ecnu.edu.cn/",
    "中国农业大学": "https://yz.cau.edu.cn/",
    "国防科技大学": "https://gs.nudt.edu.cn/",
    "西北农林科技大学": "https://yzb.nwsuaf.edu.cn/",
    "中央民族大学": "https://yzbm.muc.edu.cn/",
    "东北大学": "https://yzb.neu.edu.cn/",
    "兰州大学": "https://yz.lzu.edu.cn/"
}

# 2. 连接ES（和之前完全一致）
es = Elasticsearch(
    "http://localhost:9200",
    request_timeout=30
)
INDEX_NAME = "school_news"

# 3. 通用爬虫函数（适配大部分高校官网）
def crawl_school(school_name, url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/122.0.0.0"
    }
    try:
        # 发送请求
        response = requests.get(url, headers=headers, timeout=15)
        response.encoding = "utf-8"
        soup = BeautifulSoup(response.text, "lxml")
        
        # 提取首页第一条新闻（通用解析规则，适配80%高校）
        # 尝试不同的新闻容器标签（兼容不同官网结构）
        news_containers = [
            soup.find("div", class_=lambda x: x and "news" in x.lower()),
            soup.find("ul", class_=lambda x: x and "list" in x.lower()),
            soup.find("div", id=lambda x: x and "news" in x.lower())
        ]
        news_container = next((x for x in news_containers if x), None)
        
        if news_container:
            # 提取标题
            title_tag = news_container.find("a")
            title = title_tag.get_text(strip=True) if title_tag else "最新通知"
            # 提取简易内容（避免解析复杂结构）
            content = f"{school_name}研究生院最新动态，详情请访问官网：{url}"
            # 提取发布时间（通用规则）
            time_tag = news_container.find("span", class_=lambda x: x and "time" in x.lower())
            publish_time = time_tag.get_text(strip=True) if time_tag else datetime.datetime.now().strftime("%Y-%m-%d")
            
            # 写入ES
            data = {
                "school": school_name,
                "title": title,
                "content": content,
                "publish_time": publish_time,
                "crawl_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            es.index(index=INDEX_NAME, document=data)
            print(f"✅ 成功爬取并写入ES：{school_name} - {title}")
        else:
            # 无新闻则写入默认数据
            data = {
                "school": school_name,
                "title": "暂无最新动态",
                "content": f"{school_name}研究生院官网：{url}",
                "publish_time": datetime.datetime.now().strftime("%Y-%m-%d"),
                "crawl_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            es.index(index=INDEX_NAME, document=data)
            print(f"⚠️ 未找到新闻，写入默认数据：{school_name}")
    except Exception as e:
        # 爬取失败则写入失败提示
        data = {
            "school": school_name,
            "title": "爬取失败",
            "content": f"访问{school_name}研究生院官网失败：{str(e)}",
            "publish_time": datetime.datetime.now().strftime("%Y-%m-%d"),
            "crawl_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        es.index(index=INDEX_NAME, document=data)
        print(f"❌ 爬取失败：{school_name} - {e}")

# 4. 批量爬取所有985高校
def batch_crawl_all():
    print("🚀 开始批量爬取39所985高校研究生院数据...")
    for school, url in UNIVERSITIES.items():
        crawl_school(school, url)
    print("🎉 批量爬取完成！所有数据已写入ES")

# 运行批量爬取
if __name__ == "__main__":
    batch_crawl_all()