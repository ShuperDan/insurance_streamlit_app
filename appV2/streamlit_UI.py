import streamlit as st
from streamlit_option_menu import option_menu

# 初始化布局
def initial_settings():
    st.set_page_config(layout = 'wide',
                       page_title = '寿险计划书分析助手APP',
                       page_icon = '📈',
                       initial_sidebar_state = 'expanded')

# 主标题
def main_title():
    # 主页标题
    st.markdown(
        """
        <style>
        /* 移除顶部间距 */
        .main-title {
            margin-top: -60px;  /* 通过负值减少顶部间距 */
        }
        </style>
        <h1 class='main-title' style='text-align: center; color: #F5F7F8;'>
        寿险计划书 <span style='color: #379777;'>分析工具</span>
        </h1>
        """,
        unsafe_allow_html = True
    )
# 菜单
def menu():
    menu_option = option_menu(
        menu_title ='Welcome',
        options = ["上传数据", "保单分析", "了解更多"],
        icons = ["folder", "bar-chart", "globe"],
        menu_icon = "house",
        default_index = 0,
        orientation = "horizontal",
        styles = {
            "container": {"padding": "5px"},  # 仅设置容器的内边距
            "icon": {"font-size": "20px"},  # 图标的大小
            "nav-link": {
                "font-size": "18px",  # 设置未选中项的字体大小
                "font-weight": "bold",  # 设置未选中项的字体粗细
                "color": "#F7F7F8",  # 未选中项的字体颜色
                "text-align": "center",  # 文本居中
                "margin": "0px",  # 去掉外边距
            },
            "nav-link-selected": {
                "font-size": "18px",  # 设置选中项的字体大小
                "font-weight": "bold",  # 设置选中项的字体粗细
                "color": "#F7F7F8",  # 选中项的字体颜色
                "text-align": "center",  # 文本居中
            }
        }
    )

    return menu_option

# 按钮
def radio(updated_index = 0):
    st.markdown(
        """<style>
        div[class*="stRadio"] > label > div[data-testid="stMarkdownContainer"] > p {
        font-size: 24px;
        }</style>""", unsafe_allow_html=True)

    bottom_option = st.radio(label = '您打算分析几个计划书？',
                             options = ("1", "2"),
                             index = updated_index,
                             help = '由于版本限制，最多支持同时分析两个计划书。',
                             horizontal = True,
                             captions = ['专注分析单个计划书', '分析对比两个计划书'],
                             label_visibility = 'visible')

    return bottom_option

# 文件输入
def upload_signal_file():
    file = st.file_uploader(label = "请上传您的计划书表格文件",
                            type = ["xlsx"],
                            accept_multiple_files = False,
                            help = '您只能上传一个文件',
                            label_visibility = 'visible')

    return file

def upload_two_files():
    files = st.file_uploader(label = "请上传您的计划书表格文件",
                             type = ["xlsx"],
                             accept_multiple_files = True,
                             help = '您可以上传两个文件',
                             label_visibility = 'visible')

    if len(files) == 2:
        return files[0], files[1]
    if len(files) > 2:
        st.warning('只能上传两个文件，请重新选择。')
        return None, None
    else:
        return None, None

def select_year():
    select_year = st.sidebar.slider(
        label = '请选择保单年度范围',
        min_value = 1,
        max_value = 68,
        value = 20,
        step = 1,
        format = "%d年",
        key = "select_year",
    )

    return select_year

def signal_selectbox(data):

    product = st.sidebar.selectbox(label = '选择保险产品',
                                   options = data.info.loc[0, '保险产品'],
                                   disabled = True,
                                   label_visibility = "visible")

    withdrawal_value = st.sidebar.selectbox(label = '选择保单价值类型',
                                          options = ['无提取', '提取'],
                                          disabled = False,
                                          label_visibility = "visible")

    value_type = st.sidebar.selectbox(label = '选择保单价值类型',
                                       options = ['退保价值', '身故赔偿'],
                                       disabled = False,
                                       label_visibility = "visible")

    is_withdrawal = withdrawal_value == '提取'
    is_surrender = value_type == '退保价值'

    return product, is_withdrawal, is_surrender

def two_selectbox(data1, data2):
    product = st.sidebar.selectbox(label = '选择保险产品',
                                   options = [data1.info.loc[0, '保险产品'], data2.info.loc[0, '保险产品']],
                                   disabled = False,
                                   label_visibility = "visible")

    withdrawal_value = st.sidebar.selectbox(label = '选择保单价值类型',
                                             options = ['无提取', '提取'],
                                             disabled = False,
                                             label_visibility = "visible")

    value_type = st.sidebar.selectbox(label = '选择保单价值类型',
                                       options = ['退保价值', '身故赔偿'],
                                       disabled = False,
                                       label_visibility = "visible")

    is_withdrawal = withdrawal_value == '提取'
    is_surrender = value_type == '退保价值'

    return product, is_withdrawal, is_surrender















