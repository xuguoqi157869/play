import streamlit as st
from elasticsearch import Elasticsearch

# 1. 连接ES（和写入端完全一致）
es = Elasticsearch(
    "http://localhost:9200",
    request_timeout=30
)
INDEX_NAME = "school_news"  # 必须和写入端的索引名一致

# 2. 前端页面配置
st.set_page_config(page_title="985研究生院信息系统", layout="wide")
st.title("🎓 985高校研究生院信息展示")
st.divider()

# 3. 核心函数：从ES读取数据
def get_es_data():
    # 查询ES中所有数据
    result = es.search(index=INDEX_NAME, query={"match_all": {}}, size=100)
    # 整理数据为列表
    data_list = []
    for item in result["hits"]["hits"]:
        source = item["_source"]
        data_list.append({
            "高校名称": source.get("school", "未知"),
            "新闻标题": source.get("title", "未知"),
            "新闻内容": source.get("content", "未知"),
            "爬取时间": source.get("crawl_time", "未知")
        })
    return data_list

# 4. 前端展示数据
data = get_es_data()
if data:
    st.table(data)  # 用表格展示ES数据
else:
    st.warning("ES中暂无数据，请先运行写入脚本")

# 5. 可选：添加模糊搜索功能（根据标题检索）
st.sidebar.subheader("🔍 标题搜索")
search_key = st.sidebar.text_input("输入关键词")
if search_key:
    # 按标题模糊检索ES数据
    search_result = es.search(
        index=INDEX_NAME,
        query={"match": {"title": search_key}}
    )
    search_data = []
    for item in search_result["hits"]["hits"]:
        source = item["_source"]
        search_data.append({
            "高校名称": source.get("school", "未知"),
            "新闻标题": source.get("title", "未知"),
            "新闻内容": source.get("content", "未知"),
            "爬取时间": source.get("crawl_time", "未知")
        })
    st.subheader(f"搜索结果（关键词：{search_key}）")
    st.table(search_data)