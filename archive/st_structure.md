```markdown
# Streamlit (st) 结构树

st
├── 全局配置
│   └── st.set_page_config(page_title="", layout="centered")
│
├── 显示元素
│   ├── st.title("大标题")
│   ├── st.header("中标题")
│   ├── st.caption("灰色小字")
│   ├── st.markdown("支持Markdown的文本")
│   ├── st.write("通用显示")
│   ├── st.success("绿色成功提示")
│   ├── st.warning("黄色警告提示")
│   ├── st.error("红色错误提示")
│   └── st.info("蓝色信息提示")
│
├── 容器与布局 (with 使用)
│   ├── st.sidebar
│   │   ├── st.sidebar.header("标题")
│   │   ├── st.sidebar.file_uploader("上传")
│   │   └── st.sidebar.success("提示")
│   ├── st.chat_message("user" / "assistant")
│   │   └── st.markdown("气泡内容")
│   ├── st.container()
│   ├── st.columns(n)
│   └── st.expander("点击展开")
│
├── 交互控件 (有返回值)
│   ├── st.chat_input("提示词")        返回 字符串 / None
│   ├── st.file_uploader("提示词", type=["pdf"])  返回 文件对象 / None
│   ├── st.text_input("提示词")        返回 字符串
│   ├── st.button("按钮文字")          返回 True / False
│   ├── st.selectbox("提示", options)  返回 选中项
│   ├── st.slider("提示", 0, 100)      返回 数值
│   └── st.checkbox("提示")            返回 True / False
│
├── 状态存储与缓存
│   ├── st.session_state              类字典对象，跨刷新保存
│   │   ├── st.session_state.messages         自定义键
│   │   ├── st.session_state.rag_chain        自定义键
│   │   └── st.session_state.processed_file   自定义键
│   ├── @st.cache_resource            缓存资源(模型)，只加载一次
│   └── @st.cache_data                缓存数据
│
└── 加载与反馈
    ├── st.spinner("加载中...")       with 使用
    ├── st.progress(50)              进度条
    └── st.balloons()                气球动画
```