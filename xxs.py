import streamlit as st
from pathlib import Path
import pandas as pd
import re

# 初始化状态变量
if "in_main" not in st.session_state:
    st.session_state.in_main = False  # 是否在主页面
if "sidebar_hidden" not in st.session_state:
    st.session_state.sidebar_hidden = False  # 侧边栏是否隐藏
# 初始化用户输入数据字典（保存姓名等信息）
if "user_inputs" not in st.session_state:
    st.session_state.user_inputs = {"name": "", "sex": "男"}  # 初始值

BASE_DIR = Path().parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)  # 确保数据目录存在

# 根据状态动态设置侧边栏显示模式
if st.session_state.sidebar_hidden:
    st.set_page_config(initial_sidebar_state="collapsed")
else:
    st.set_page_config(initial_sidebar_state="expanded")

# 侧边栏内容（仅在未隐藏时显示）
if not st.session_state.sidebar_hidden:
    st.sidebar.title("用户信息")
    # 姓名输入（作为用户唯一标识基础）
    name = st.sidebar.text_input("请输入您的姓名（用于区分数据）：",value=st.session_state.user_inputs["name"])
    st.session_state.user_inputs["name"] = name  # 实时更新姓名

    # 性别选择
    sex = st.sidebar.selectbox("性别",["男", "女"],index=["男", "女"].index(st.session_state.user_inputs["sex"]))
    st.session_state.user_inputs["sex"] = sex

    # 进入主页面按钮（添加姓名非空校验）
    if st.sidebar.button("进入您的信息系统", key="enter_main"):
        if not name.strip():  # 检查姓名是否为空
            st.sidebar.error("您的姓名不能为空")
        else:
            st.session_state.in_main = True
            st.session_state.sidebar_hidden = True
            st.rerun()

# 主页面内容
if st.session_state.in_main:
    # 获取当前用户名（作为数据文件标识）
    current_user = st.session_state.user_inputs["name"].strip()
    # 处理用户名中的特殊字符（避免文件名错误）
    safe_username = re.sub(r'[^\w\-_.]', '_', current_user)  # 替换特殊字符为下划线
    # 为当前用户创建独立的数据文件路径
    USER_CSV = DATA_DIR / f"{safe_username}_records.csv"

    st.title(f"欢迎进入 {current_user} 的信息系统")
    st.caption(f"您的数据将独立保存在：{USER_CSV.name}")

    # 定义数据列（增加创建时间）
    COLUMNS = ["id", "title", "category", "notes", "created_at"]
    # 读取当前用户的数据（如果文件存在）
    if USER_CSV.exists():
        df = pd.read_csv(USER_CSV)
    else:
        df = pd.DataFrame(columns=COLUMNS)


    # 保存数据到当前用户的文件
    def save_data(df: pd.DataFrame):
        df.to_csv(USER_CSV, index=False)


    # 添加新记录的表单
    with st.form("add_form", clear_on_submit=True):
        new_record = {}
        # 自动生成ID（最大ID+1，空表则为1）
        new_record['id'] = 1 if df.empty else int(df["id"].max()) + 1
        new_record['title'] = st.text_input("标题 *", placeholder="例如：三好学生")
        CATEGORIES = ["荣誉", "教育经历", "竞赛", "证书", "账号", "其他"]
        new_record['category'] = st.selectbox("类别", CATEGORIES, index=0)
        new_record['notes'] = st.text_area("备注（可选）",placeholder="关键信息、链接或行动项…",height=100)
        submitted = st.form_submit_button("保存", type="primary", use_container_width=True)

    # 处理表单提交
    if submitted:
        if not new_record['title'].strip():  # 校验标题不为空
            st.error("标题为必填项，请填写")
        else:
            # 添加创建时间
            new_record["created_at"] = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
            # 合并新记录到数据框
            df = pd.concat([df, pd.DataFrame([new_record])], ignore_index=True)
            save_data(df)
            st.success("记录已保存！")

    # 显示当前用户的所有记录
    if not df.empty:
        st.subheader("您的记录")
        # 展示时隐藏id列（用户无需关心），按创建时间倒序
        st.dataframe(
            df.drop(columns=["id"]).sort_values(by="created_at", ascending=False),
            use_container_width=True
        )
    else:
        st.info("暂无记录")

    # 返回原始页面按钮
    if st.button("返回用户信息页", key="back_original"):
        st.session_state.in_main = False
        st.session_state.sidebar_hidden = False
        st.rerun()
else:
    # 原始页面提示
    st.info("请从侧边栏输入您的姓名并进入信息系统")