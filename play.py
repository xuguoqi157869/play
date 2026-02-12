import streamlit as st
import random

# 页面基础设置
st.set_page_config(page_title="Streamlit猜数字游戏", page_icon="🎮", layout="centered")
st.title("🎮 猜数字小游戏")
st.subheader("系统随机生成 1-100 的数字，快来猜猜看！")

# 初始化会话状态（保存游戏数据，刷新页面不重置）
if "target_num" not in st.session_state:
    st.session_state.target_num = random.randint(1, 100)  # 随机目标数字
if "guess_times" not in st.session_state:
    st.session_state.guess_times = 0  # 猜的次数
if "game_over" not in st.session_state:
    st.session_state.game_over = False  # 游戏是否结束

# 重置游戏函数
def reset_game():
    st.session_state.target_num = random.randint(1, 100)
    st.session_state.guess_times = 0
    st.session_state.game_over = False

# 游戏核心逻辑
with st.form(key="guess_form"):
    # 输入框：只能输入数字，范围1-100
    user_guess = st.number_input(
        "请输入你猜的数字（1-100）：",
        min_value=1,
        max_value=100,
        step=1,
        disabled=st.session_state.game_over  # 猜对后禁用输入
    )
    # 提交按钮
    submit_btn = st.form_submit_button("提交猜测", disabled=st.session_state.game_over)

# 处理猜测结果
if submit_btn:
    st.session_state.guess_times += 1  # 次数+1
    # 对比用户输入和目标数字
    if user_guess < st.session_state.target_num:
        st.warning(f"❌ 猜小啦！再往大了猜猜～（已猜 {st.session_state.guess_times} 次）")
    elif user_guess > st.session_state.target_num:
        st.warning(f"❌ 猜大啦！再往小了猜猜～（已猜 {st.session_state.guess_times} 次）")
    else:
        st.success(f"🎉 恭喜猜对啦！目标数字就是 {st.session_state.target_num}～")
        st.info(f"你一共猜了 {st.session_state.guess_times} 次，真棒！")
        st.session_state.game_over = True  # 游戏结束

# 游戏结束后显示重置按钮
if st.session_state.game_over:
    st.button("🔄 重新开始游戏", on_click=reset_game)

# 侧边栏：游戏说明
with st.sidebar:
    st.header("📖 游戏规则")
    st.write("1. 系统随机生成 1-100 的整数")
    st.write("2. 输入你猜测的数字，点击提交")
    st.write("3. 页面会提示「大了/小了」，直到猜对")
    st.write("4. 猜对后可点击「重新开始」玩下一局")
    st.divider()
    st.caption("💡 小技巧：先猜50，再根据提示缩小范围～")