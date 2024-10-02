from streamlit_UI import *
from global_settings import *
import streamlit as st
import os
import pandas as pd

# 初始化布局
initial_settings()

# 主页标题
main_title()

# 菜单
menu_option = menu()

# 保存变量初始化
if 'data' not in st.session_state:
    st.session_state['data'] = None
if 'data1' not in st.session_state:
    st.session_state['data1'] = None
if 'data2' not in st.session_state:
    st.session_state['data2'] = None
if 'radio_index' not in st.session_state:
    st.session_state['radio_index'] = 0
if 'company_name' not in st.session_state:
    st.session_state['company_name'] = None

# 按钮和文件路径
col1, col2, col3, col4 = st.columns([0.25, 3, 3, 0.25])

if menu_option == '上传数据':
    with col2:
        st.markdown("<br><br>", unsafe_allow_html = True)
        bottom_option = radio(updated_index = st.session_state['radio_index'])
        st.session_state['bottom_option'] = bottom_option
        st.session_state['radio_index'] = ["1", "2"].index(bottom_option)

    with col3:
        st.markdown("<br><br>", unsafe_allow_html = True)
        if st.session_state['bottom_option'] == '1':
            upload_file = upload_signal_file()
            if upload_file is not None:
                data_dict = pd.read_excel(upload_file, sheet_name = None, engine = 'openpyxl')
                st.session_state['data'] = data_dict
                data_loader = st.session_state['data']
                st.success(f"文件 '{upload_file.name[:-5]}' 已上传，请点击'保单分析'页面。")
                st.write(data_dict)

        elif st.session_state['bottom_option'] == '2':
            upload_file_1, upload_file_2 = upload_two_files()
            if upload_file_1 is not None and upload_file_2 is not None:
                data_dict1 = pd.read_excel(upload_file_1, sheet_name = None, engine = 'openpyxl')
                data_dict2 = pd.read_excel(upload_file_2, sheet_name = None, engine = 'openpyxl')
                st.session_state['data1'] = data_dict1
                st.session_state['data2'] = data_dict2
                data_loader1 = st.session_state['data1']
                data_loader2 = st.session_state['data2']
                st.success(f"文件 {upload_file_1.name[:-5]} 和 {upload_file_2.name[:-5]} 已上传，请点击'保单分析'页面。")

elif menu_option == '保单分析':
    # 创建侧边栏
    st.sidebar.title("导航")

    # 滑动条
    selected_year = select_year()

    # 下拉窗口
    if st.session_state['bottom_option'] == '1':
        if st.session_state['data'] is not None:
            data_dict = st.session_state['data']
            data_loader = Data.from_dict(data_dict)
            st.session_state['company_name'] = data_loader.info.loc[0, '保险公司']
            product, is_withdrawal, is_surrender = signal_selectbox(data_loader)

            data_loader.update_year(selected_year)
            data_loader.update_withdrawal(is_withdrawal)
            data_loader.update_surrender(is_surrender)
            data_loader.update_information()
            data_loader.update_value()
            data_loader.payment_periods_func()
            data_loader.premium_amount_func()

            visual = VisualSettings(
                surrender = data_loader.surrender,
                death = data_loader.death,
                withdrawal_surrender = data_loader.withdrawal_surrender,
                withdrawal_death = data_loader.withdrawal_death,
                information = data_loader.information,
                index = data_loader.index,
                is_withdrawal = data_loader.is_withdrawal,
                is_surrender = data_loader.is_surrender,
                special_index = data_loader.special_index,
                payment_periods = data_loader.payment_periods,
                premium_amount = data_loader.premium_amount,)

            visual.info_layout()
            visual.element_layout()

            col1, col2, col3 = st.columns([0.4, 0.2, 0.4])
            with col1:
                visual.adapt_value_component_layout()
            with col2:
                visual.irr_layout()
            with col3:
                visual.bar_layout()
            visual.timeseries_line_layout()

    elif st.session_state['bottom_option'] == '2':
        if st.session_state['data1'] is not None and st.session_state['data2'] is not None:
            data_dict1 = st.session_state['data1']
            data_loader1 = Data.from_dict(data_dict1)
            data_dict2 = st.session_state['data2']
            data_loader2 = Data.from_dict(data_dict2)

            product, is_withdrawal, is_surrender = two_selectbox(data_loader1, data_loader2)

            if product == data_loader1.info.loc[0, '保险产品']:
                data_loader = data_loader1
            elif product == data_loader2.info.loc[0, '保险产品']:
                data_loader = data_loader2
            st.session_state['company_name'] = data_loader.info.loc[0, '保险公司']

            data_loader.update_year(selected_year)
            data_loader.update_withdrawal(is_withdrawal)
            data_loader.update_surrender(is_surrender)
            data_loader.update_information()
            data_loader.update_value()
            data_loader.payment_periods_func()
            data_loader.premium_amount_func()

            visual = VisualSettings(
                surrender=data_loader.surrender,
                death=data_loader.death,
                withdrawal_surrender=data_loader.withdrawal_surrender,
                withdrawal_death=data_loader.withdrawal_death,
                information=data_loader.information,
                index=data_loader.index,
                is_withdrawal=data_loader.is_withdrawal,
                is_surrender=data_loader.is_surrender,
                special_index=data_loader.special_index,
                payment_periods=data_loader.payment_periods,
                premium_amount=data_loader.premium_amount)

            visual.info_layout()
            visual.element_layout()

            col1, col2, col3 = st.columns([0.4, 0.2, 0.4])
            with col1:
                visual.adapt_value_component_layout()
            with col2:
                visual.irr_layout()
            with col3:
                visual.bar_layout()

            visual.timeseries_line_layout()

elif menu_option == '了解更多':
    company_name = st.session_state['company_name']

    site_dict = {
        '宏利': {
            'company_url': 'https://www.manulife.com.hk/zh-hk/individual.html',
            'rate_url': 'https://www.manulife.com.hk/zh-hk/individual/products/understanding-your-participating-policy/fulfillment-ratio.html',
            'history_url': 'https://www.manulife.com.hk/zh-hk/individual/about/our-story/our-business.html',
            'logo': 'https://cdn.worldvectorlogo.com/logos/manulife.svg'
        },

        '永明': {
            'company_url': 'https://www.sunlife.com.hk/zh-hans/',
            'rate_url': 'https://www.sunlife.com.hk/zh-hans/insurance/savings-and-life/fulfillment-ratios-of-respective-products/',
            'history_url': 'https://www.sunlife.com.hk/zh-hans/insurance/savings-and-life/fulfillment-ratios-of-respective-products/',
            'logo': 'https://www.sunlife.com.hk/content/dam/sunlife/legacy/assets/hk/images/SLF-HK_Blue-on-yellow_1200x1200.png'
        }
    }

    visual = VisualSettings()
    html1 = "https://www.ia.org.hk/sc/participating_policy/index.html"

    st.markdown('<br><br>', unsafe_allow_html=True)

    # 使用 HTML 格式对内容进行美化
    st.markdown(
        """
        <div style="
            display: flex; 
            justify-content: center; 
            align-items: center; 
            text-align: center; 
            margin: 20px 0;
        ">
            <img src="https://cdn-icons-png.flaticon.com/512/25/25284.png" style="width: 24px; height: 24px; margin-right: 10px;"/>
            <span style="font-size: 24px; font-weight: bold; font-style: italic;">
                点击下方内容跳转至相应链接
            </span>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown('<br><br>', unsafe_allow_html=True)

    col1, col2, col3, col4, col5, col6 = st.columns([0.1, 0.2, 0.2, 0.2, 0.2, 0.05])
    with col2:
        visual.describe_info('分红保单的定义', html1)
    with col3:
        visual.describe_info(f'{company_name}分红实现率', site_dict[company_name]['rate_url'])
    with col4:
        visual.describe_info(f'{company_name}公司介绍', site_dict[company_name]['history_url'])
    with col5:
        visual.describe_info(f'{company_name}公司官网', site_dict[company_name]['company_url'])














































