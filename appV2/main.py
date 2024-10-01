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
            'url': 'https://www.manulife.com.hk/zh-hk/individual.html',
            'logo': 'https://cdn.worldvectorlogo.com/logos/manulife.svg'
            # 宏利的 logo 链接
        },
        '永明': {
            'url': 'https://www.sunlife.com.hk/zh-hans/',
            'logo': 'https://www.sunlife.com.hk/content/dam/sunlife/legacy/assets/hk/images/SLF-HK_Blue-on-yellow_1200x1200.png'
            # 永明的 logo 链接
        }
    }

    st.markdown(
        f"""
        <div style="text-align: center; margin-top: 120px;">
            <a href="{site_dict[company_name]['url']}" target="_blank" style="text-decoration: none; font-weight: bold;">
                <img src="{site_dict[company_name]['logo']}" alt="{company_name} logo" style="width: 100px; vertical-align: middle; margin-right: 20px;">
                <span style="font-size: 30px; color: white;">点击这里跳转到 </span>
                <span style="font-size: 60px; color: #ff4500;">{company_name}</span>
                <span style="font-size: 30px; color: white;"> 中文官方网站</span>
            </a>
        </div>
        """,
        unsafe_allow_html=True
    )














































