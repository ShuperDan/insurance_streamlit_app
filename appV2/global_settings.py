from dataclasses import dataclass
from typing import Any, Optional
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
import numpy_financial as npf
from matplotlib.colors import to_rgba


def hex_to_rgba_string(hex_color_code, alpha=1.0):
    rgba_tuple = to_rgba(hex_color_code, alpha)
    rgba_string = f'rgba({int(rgba_tuple[0] * 255)}, {int(rgba_tuple[1] * 255)}, {int(rgba_tuple[2] * 255)}, {rgba_tuple[3]})'

    return rgba_string

# 数据类
@dataclass
class Data:
    surrender: Any = None
    death: Any = None
    withdrawal_surrender: Any = None
    withdrawal_death: Any = None
    info: Any = None
    withdrawal_info: Any = None
    index: int = None
    is_withdrawal: bool = None
    is_surrender: bool = None
    information: Any = None
    special_index: int = None
    withdraw_amount: int = None
    payment_periods: int = None
    premium_amount: int = None
    start_withdraw_year: int = None

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            surrender = data.get("退保价值"),
            death = data.get('身故赔偿'),
            withdrawal_surrender = data.get('提取-退保价值'),
            withdrawal_death = data.get('提取-身故赔偿'),
            info = data.get('保单信息'),
            withdrawal_info = data.get('提取-保单信息')
        )

    def update_year(self, selected_year: int):
        self.index = selected_year - 1

    def update_withdrawal(self, is_withdrawal: bool):
        self.is_withdrawal = is_withdrawal

    def update_surrender(self, is_surrender: bool):
        self.is_surrender = is_surrender

    def update_information(self):
        if self.is_withdrawal:
            self.information = self.withdrawal_info
        else:
            self.information = self.info

    def update_value(self):
        if self.is_withdrawal:
            if self.is_surrender:
                return self.withdrawal_surrender
            else:
                return self.withdrawal_death
        else:
            if self.is_surrender:
                return self.surrender
            else:
                return self.death

    def special_year(self):
        if self.is_withdrawal:
            if not self.is_surrender:
                condition = (self.update_value()['保证现金价值(提取后)'] + self.update_value()['非保证红利(提取后)'])\
                                          >= self.update_value()['保证身故赔偿(提取后)']
                self.special_index = self.update_value()['保单年度'].loc[condition].idxmin() - 1

            else:
                self.special_index = 0
        else:
            if not self.is_surrender:
                condition = (self.update_value()['保证现金价值'] + self.update_value()['非保证红利']) \
                            >= self.update_value()['保证身故赔偿']
                self.special_index = self.update_value()['保单年度'].loc[condition].idxmin() - 1

            else:
                self.special_index = 0

        return self.special_index

    def display_text(self):
        if self.is_withdrawal:
            if self.is_surrender:
                cols = ['保单年度', '缴费总额', '提取金额', '保证现金价值(提取后)', '非保证红利(提取后)', '退保价值总额(提取后)']
                data = self.withdrawal_surrender[cols]
                data['累计提取'] = data['提取金额'].cumsum().squeeze()
                data = data.loc[self.index]
                data = data.loc[data.index != '提取金额']
            else:
                cols = ['保单年度', '缴费总额', '提取金额', '保证现金价值(提取后)', '非保证红利(提取后)', '保证身故赔偿(提取后)', '身故赔偿总额(提取后)']
                data = self.withdrawal_death[cols]
                data['累计提取'] = data['提取金额'].cumsum().squeeze()
                data = data.loc[self.index]
                data = data.loc[data.index != '提取金额']

        else:
            if self.is_surrender:
                cols = ['保单年度', '缴费总额', '保证现金价值', '非保证红利', '退保价值总额']
                data = self.surrender.loc[self.index, cols]
            else:
                cols = ['保单年度', '缴费总额', '保证现金价值', '非保证红利', '保证身故赔偿', '身故赔偿总额']
                data = self.death.loc[self.index, cols]

        return data

    def value_component(self):
        if self.is_withdrawal:
            if self.is_surrender:
                cols = ['保证现金价值(提取后)', '非保证红利(提取后)', '复归红利(提取后)', '终期红利(提取后)']
                data = self.withdrawal_surrender.loc[self.index, cols]

            else:
                cols = ['保证现金价值(提取后)', '非保证红利(提取后)', '复归红利(提取后)', '终期红利(提取后)']
                data = self.withdrawal_death.loc[self.index, cols]

            data = pd.concat([data, pd.Series(self.display_text()['累计提取'], index=['累计提取'])])
            data = data.to_frame(name = 'values')
            data['parents'] = ['总额', '总额', '非保证红利(提取后)', '非保证红利(提取后)', '总额']

        else:
            if self.is_surrender:
                cols = ['保证现金价值', '非保证红利', '复归红利', '终期红利']
                data = self.surrender.loc[self.index, cols]

            else:
                cols = ['保证现金价值', '非保证红利', '复归红利', '终期红利']
                data = self.death.loc[self.index, cols]

            data = data.to_frame(name = 'values')
            data['parents'] = ['总额', '总额', '非保证红利', '非保证红利']

        return data

    def bar_value(self):
        if self.is_withdrawal:
            if self.is_surrender:
                cols = ['缴费总额', '退保价值总额(提取后)']
                data = self.withdrawal_surrender.loc[self.index, cols]
            else:
                cols = ['缴费总额', '身故赔偿总额(提取后)']
                data = self.withdrawal_death.loc[self.index, cols]

            data = pd.concat([data, pd.Series(self.display_text()['累计提取'], index=['累计提取'])])

        else:
            if self.is_surrender:
                cols = ['缴费总额', '退保价值总额']
                data = self.surrender.loc[self.index, cols]
            else:
                cols = ['缴费总额', '身故赔偿总额']
                data = self.death.loc[self.index, cols]

        return data

    def timeseries_data(self):
        if self.is_withdrawal:
            if self.is_surrender:
                cols = ['保单年度', '保证现金价值(提取后)', '非保证红利(提取后)', '提取金额']

            else:
                cols = ['保单年度', '保证现金价值(提取后)', '非保证红利(提取后)', '提取金额', '保证身故赔偿(提取后)']

            data = self.update_value()[cols]
            data['累计提取'] = data['提取金额'].cumsum().squeeze()
            data = data.loc[:self.index]
            data = data.drop('提取金额', axis = 1)

        else:
            if self.is_surrender:
                cols = ['保单年度', '保证现金价值', '非保证红利', '提取金额']
            else:
                cols = ['保单年度', '保证现金价值', '非保证红利', '提取金额', '保证身故赔偿']

            data = self.update_value()[cols]
            data['累计提取'] = data['提取金额'].cumsum().squeeze()
            data = data.loc[:self.index]
            data = data.drop('提取金额', axis = 1)

        return data

    def payment_periods_func(self):
        self.payment_periods = int(self.information['缴费年数'].squeeze()[:-1])

    def premium_amount_func(self):
        self.premium_amount = int(self.information['年缴保费'].squeeze())

    def cal_irr(self):
        if self.is_withdrawal:
            if self.is_surrender:
                col = '退保价值总额(提取后)'
            else:
                col = '身故赔偿总额(提取后)'
        else:
            if self.is_surrender:
                col = '退保价值总额'
            else:
                col = '身故赔偿总额'

        premium_cashflow = np.zeros(self.index + 1)
        premium_cashflow[:self.payment_periods] = -self.premium_amount
        withdraw_cashflow = self.update_value()['提取金额'].iloc[:self.index + 1]
        surrender_cashflow = np.zeros(self.index + 1)
        surrender_cashflow[-1] = self.update_value().loc[self.index, col]

        net_cashflow = premium_cashflow + surrender_cashflow + withdraw_cashflow

        irr = npf.irr(net_cashflow) * 100

        return irr

@dataclass
class VisualSettings(Data):
    def load_icons(self):
        st.markdown("""
                    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css" rel="stylesheet">
                    """, unsafe_allow_html = True)
    def info_layout(self):
        self.load_icons()

        icon_html = '<i class="fas fa-align-left"></i> 保单信息'

        # 显示图标
        st.markdown(f"<div style='text-align: left; font-size: 18px;'>{icon_html}</div>", unsafe_allow_html=True)
        info_transform = self.information.T.squeeze()

        cols = st.columns(len(info_transform))

        if self.information is not None and not self.information.empty:
            for idx, (key, value) in enumerate(info_transform.items()):
                with cols[idx]:
                    st.markdown(
                        f"<div style='color: #FADFA1; text-align: center; font-size: 16px'>"
                        f"{key}</div>",
                        unsafe_allow_html = True)

                    st.markdown(f"<p style='color: #FFF4EA; font-size: 26px; text-align: center;font-weight: bold;'>"
                                f"{value}</p>",
                                unsafe_allow_html = True)
        else:
            st.warning(body = "无可用数据.", icon = "⚠️")

    def element_layout(self):
        self.load_icons()

        icon_html = '<i class="fas fa-align-left"></i> 主要内容'
        # 显示图标
        st.markdown(f"<div style='text-align: left; font-size: 18px;'>{icon_html}</div>", unsafe_allow_html=True)

        # 获取数据的长度
        length = len(self.display_text())

        # 定义颜色
        color_scales = px.colors.qualitative.Set3

        # 创建横排布局的列
        cols = st.columns(length)

        if self.display_text() is not None and not self.display_text().empty:

            # 遍历每个键值对并可视化
            for idx, (key, value) in enumerate(self.display_text().items()):
                # 去除 "(提取后)" 并将其作为注释
                key_cleaned = key.replace("(提取后)", "")

                if key != '保单年度':
                    value = f'${value: ,.0f}'

                with cols[idx]:
                    st.markdown(
                        f"<div style='color: {color_scales[idx]}; text-align: center;'>"
                        f"{key_cleaned}</div>",
                        unsafe_allow_html = True)

                    st.markdown(
                        f"<div style='color: {color_scales[idx]}; text-align: center; font-weight: bold; font-size: 24px'>"
                        f"{value}</div>",
                        unsafe_allow_html = True)

                    if "(提取后)" in key:
                        st.markdown(
                            f"<p style='color: #888; text-align: center; font-size: 12px;'>提取后</p>",
                            unsafe_allow_html = True)

        else:
            st.warning(body = "无可用数据.", icon = "⚠️")

    def value_component_layout(self):

        self.load_icons()

        icon_html = '<i class="fas fa-align-left"></i> 保单价值构成'
        # 显示图标
        st.markdown(f"<div style='text-align: left; font-size: 18px;'>{icon_html}</div>", unsafe_allow_html=True)

        data = self.value_component()

        if '总额' not in data.index:
            data.loc['总额'] = [data[data['parents'] == '总额']['values'].sum(), '']  # 总额节点的父节点为空字符串

        # 创建 Icicle 图
        fig = go.Figure(go.Icicle(
            labels = data.index,
            parents =data['parents'],
            values = data['values'],
            branchvalues = 'total'
        ))

        text_template = np.where(
            data.index == '总额',
            f"总额<br>${data.loc['总额', 'values']:,.0f}",
            '%{label}<br>$%{value}'
        )

        # 更新 traces，设置文本格式和居中显示
        fig.update_traces(
            texttemplate = text_template,
            textposition = 'middle center',
            textfont_size = 16,
            hoverinfo = 'none',
            marker = dict(colorscale = 'Viridis')
        )

        fig.update_layout(
            margin=dict(t=10, l=0, r=30, b=50)
        )

        # 在 Streamlit 中显示图表
        st.plotly_chart(fig, use_container_width = True)

    def signal_value_component_layout(self):

        self.load_icons()

        icon_html = '<i class="fas fa-align-left"></i> 保单价值构成'
        # 显示图标
        st.markdown(f"<div style='text-align: left; font-size: 18px;'>{icon_html}</div>", unsafe_allow_html=True)

        if not self.is_surrender:
            if self.is_withdrawal:
                col = '保证身故赔偿(提取后)'
                data = self.display_text()[col] + self.display_text()['累计提取']
                labels = ['总额', col, '累计提取']
                parents = ['', '总额', '总额']
                values = [data, self.display_text()[col], self.display_text()['累计提取']]
            else:
                col = '保证身故赔偿'
                data = self.display_text()[col]
                labels = ['总额', col]
                parents = ['', '总额']
                values = [data, data]

            fig = go.Figure(
                go.Icicle(
                    labels = labels,
                    parents = parents,
                    values = values,
                    branchvalues = 'total'
                )
            )

            fig.update_traces(
                texttemplate='%{label}<br>$%{value}',
                textposition='middle center',
                textfont_size=16,
                hoverinfo='none',
                marker=dict(colorscale='Viridis')
            )

            fig.update_layout(
                margin=dict(t=10, l=0, r=30, b=50)
            )

            st.plotly_chart(fig, use_container_width=True)

        else:
            self.value_component_layout()

    def adapt_value_component_layout(self):
        if self.index > self.special_year():
            self.value_component_layout()
        else:
            self.signal_value_component_layout()

    def bar_layout(self, color1 = '#FFF1DB', color2 = '#EF5A6F'):
        self.load_icons()

        icon_html = '<i class="fas fa-align-left"></i> 缴费总额 VS 保单价值'
        # 显示图标
        st.markdown(f"<div style='text-align: left; font-size: 18px;'>{icon_html}</div>", unsafe_allow_html=True)

        fig = go.Figure()

        if self.is_withdrawal:
            sums = self.bar_value().iloc[1] + self.bar_value().iloc[2]
            fig.add_trace(
                go.Bar(
                    y=[self.bar_value().index[0]],
                    x=[self.bar_value().iloc[0]],
                    orientation='h',
                    showlegend=False,
                    marker=dict(color=color1),
                    text=[f'缴费总额<br>${self.bar_value().iloc[0]: ,.0f}'],
                    textposition='inside',
                    textfont = dict(size = 18),
                    hoverinfo = 'none',
                )
            )
            if sums > self.bar_value().iloc[0]:
                fig.add_trace(
                    go.Bar(
                        y = ['价值总额'],
                        x = [self.bar_value().iloc[0]],
                        orientation = 'h',
                        showlegend = False,
                        marker = dict(color = color1),
                        hoverinfo = 'none'
                    )
                )

                fig.add_trace(
                    go.Bar(
                        y = ['价值总额'],
                        x = [sums - self.bar_value().iloc[0]],
                        base = self.bar_value().iloc[0],
                        orientation = 'h',
                        showlegend = False,
                        marker = dict(color = color2),
                        text = [f'保单价值<br>${sums: ,.0f}'],
                        textposition='inside',
                        textfont = dict(size = 18, color = 'white'),
                        hoverinfo = 'none'
                    )
                )

                fig.update_layout(
                    barmode = 'stack',
                    margin=dict(t=10, l=30, r=0, b=50),
                    xaxis=dict(showticklabels = False),
                    yaxis=dict(showticklabels=False)
                )

            else:
                fig.add_trace(
                    go.Bar(
                        y = ['价值总额'],
                        x = [self.bar_value().iloc[1] + self.bar_value().iloc[2]],
                        orientation = 'h',
                        showlegend = False,
                        marker = dict(color = color2),
                        text = [f'保单价值<br>${sums: ,.0f}'],
                        textposition = 'inside',
                        textfont = dict(size=18, color = 'white'),
                        hoverinfo = 'none'

                    )
                )

                fig.update_layout(
                    barmode = 'stack',
                    margin=dict(t=10, l=30, r=0, b=50),
                    xaxis=dict(showticklabels = False),
                    yaxis=dict(showticklabels=False)
                )

        else:
            fig.add_trace(
                go.Bar(
                    y=[self.bar_value().index[0]],
                    x=[self.bar_value().iloc[0]],
                    orientation='h',
                    showlegend=False,
                    marker=dict(color=color1),
                    text=[f'缴费总额<br>${self.bar_value().iloc[0]: ,.0f}'],
                    textposition='inside',
                    textfont=dict(size=18),
                    hoverinfo='none',
                )
            )
            if self.bar_value().iloc[1] > self.bar_value().iloc[0]:
                fig.add_trace(
                    go.Bar(
                        y=['价值总额'],
                        x=[self.bar_value().iloc[0]],
                        orientation='h',
                        showlegend=False,
                        marker=dict(color=color1),
                        hoverinfo='none'
                    )
                )

                fig.add_trace(
                    go.Bar(
                        y=['价值总额'],
                        x=[self.bar_value().iloc[1] - self.bar_value().iloc[0]],
                        base=self.bar_value().iloc[0],
                        orientation='h',
                        showlegend=False,
                        marker=dict(color=color2),
                        text=[f'保单价值<br>${self.bar_value().iloc[1]: ,.0f}'],
                        textposition='inside',
                        textfont=dict(size=18, color = 'white'),
                        hoverinfo='none'
                    )
                )

                fig.update_layout(
                    barmode='stack',
                    margin=dict(t=10, l=30, r=0, b=50),
                    xaxis=dict(showticklabels=False),
                    yaxis=dict(showticklabels=False)
                )

            else:
                fig.add_trace(
                    go.Bar(
                        y=['价值总额'],
                        x=[self.bar_value().iloc[1]],
                        orientation='h',
                        showlegend=False,
                        marker=dict(color=color2),
                        text=[f'保单价值<br>${self.bar_value().iloc[1]: ,.0f}'],
                        textposition='inside',
                        textfont=dict(size=18, color = 'white'),
                        hoverinfo='none'

                    )
                )

                fig.update_layout(
                    barmode='stack',
                    margin=dict(t=10, l=30, r=0, b=50),
                    xaxis=dict(showticklabels=False),
                    yaxis=dict(showticklabels=False)
                )

        st.plotly_chart(fig, use_container_width=True)

    def irr_layout(self):

        self.load_icons()

        icon_html = '<i class="fas fa-align-left"></i> 内部收益率'
        # 显示图标
        st.markdown(f"<div style='text-align: left; font-size: 18px;'>{icon_html}</div>", unsafe_allow_html=True)

        irr_value = self.cal_irr()  # 获取 IRR 的值

        # 引入样式
        st.markdown(
            """
            <style>
            @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@900&display=swap');
            .fancy-text {
                font-family: 'Poppins', sans-serif;
                font-size: 40px;
                font-weight: 900;
                text-align: center;
                margin-top: 110px;
                color: #ECFFE6;
            }
            .irr-value {
                font-family: 'Poppins', sans-serif;
                font-size: 50px;
                font-weight: 900;
                text-align: center;
                margin-top: 50px;
                color: #FF7777;  /* 你可以根据需要调整颜色 */
            }
            </style>
            """,
            unsafe_allow_html=True
        )

        # 显示 IRR 和其值
        st.markdown(
            f"""
            <div class="fancy-text">IRR</div>
            <div class="irr-value">{irr_value:.2f}%</div>
            """,
            unsafe_allow_html=True
        )

    def timeseries_line_layout(self):
        # 加载图标
        self.load_icons()
        icon_html = '<i class="fas fa-align-left"></i> 时间序列上的保单价值'
        st.markdown(f"<div style='text-align: left; font-size: 18px;'>{icon_html}</div>", unsafe_allow_html=True)

        # 缓存数据
        years = self.timeseries_data().iloc[:, 0]
        data = self.timeseries_data()

        # 创建 x_values 格式化为 '第几年'
        x_values = [f'第{year}年' for year in years]

        # 创建子图：两行一列
        fig = make_subplots(
            rows=2,
            cols=1,
            subplot_titles=('保单价值', '保单价值分解'),
            vertical_spacing=0.1,
            shared_xaxes=True
        )

        # 计算保单价值
        if self.is_surrender:
            data['保单价值'] = data.iloc[:, 1:3].sum(axis=1) + data['累计提取']
        else:
            col = '保证身故赔偿(提取后)' if self.is_withdrawal else '保证身故赔偿'
            data['保单价值'] = np.maximum(data.iloc[:, 1:3].sum(axis=1), data[col]) + data['累计提取']

        # 创建文本列表，仅显示最后一个点的标签
        formatted_text = [''] * (len(data['保单价值']) - 1) + [f'${data["保单价值"].values[-1]: ,.0f}']

        # 添加折线图到第一个子图
        fig.add_trace(
            go.Scatter(
                x=x_values,  # 使用格式化的 x_values
                y=data['保单价值'].values,
                name='保单价值',
                mode='lines+markers+text',
                text=formatted_text,
                textposition='top center',
                textfont=dict(
                    family='Arial, sans-serif',
                    weight='bold',
                    size=14,
                    color='#FF6600'
                ),
                line=dict(color='#D2E0FB'),
                marker=dict(
                    size=20,
                    color=hex_to_rgba_string('#7CF5FF', 0.9),
                    line=dict(width=10, color=hex_to_rgba_string('#7CF5FF', 0.3))
                ),
                hovertemplate='保单价值<br>$%{y:,.0f}<extra></extra>'
            ),
            row=1, col=1
        )

        # 添加柱状图到第二个子图
        if self.is_surrender:
            columns_to_add = [
                ('保证现金价值', data.iloc[:, 1].values, x_values),
                ('非保证红利', data.iloc[:, 2].values, x_values),
                ('累计提取', data['累计提取'].values, x_values)
            ]
        else:
            special_index = self.special_year() + 1
            columns_to_add = [
                (col, data[col].iloc[:special_index].values, x_values[:special_index]),
                ('累计提取', data['累计提取'].iloc[:special_index].values, x_values[:special_index]),
                ('保证现金价值', data.iloc[special_index:, 1].values, x_values[special_index:]),
                ('非保证红利', data.iloc[special_index:, 2].values, x_values[special_index:]),
                ('累计提取', data['累计提取'].iloc[special_index:].values, x_values[special_index:])
            ]

        colors = px.colors.qualitative.Plotly

        for i, entry in enumerate(columns_to_add):
            name, y_values, x_values_subset = entry

            fig.add_trace(
                go.Bar(
                    x=x_values_subset,  # 使用格式化后的 x_values 子集
                    y=y_values,
                    name=name,
                    text=[f'${value:,.0f}' for value in y_values],  # 格式化文本，将其显示为货币
                    textposition='inside',  # 文本在柱状条内显示
                    textfont=dict(
                        size=14,  # 设置文本字体大小
                        color='white',  # 设置文本颜色
                        family='Arial, sans-serif'  # 设置文本字体类型
                    ),
                    hoverinfo = 'skip',
                    marker=dict(
                        color=colors[i % len(colors)],  # 使用离散颜色来区分不同的柱状条
                        line=dict(
                            width=0,
                            color='rgba(0, 0, 0, 0.8)'  # 设置边框颜色为较深的黑色
                        )
                    ),
                ),
                row=2, col=1
            )

        # 更新布局
        fig.update_layout(
            barmode='stack',
            height=900,
            yaxis=dict(showticklabels=False, showgrid=False),
            yaxis2=dict(showticklabels=False, showgrid=False),
            xaxis2=dict(
                showticklabels=True,
                showgrid=False,
                tickfont=dict(size=14, family='Arial', weight='bold')  # 设置第二个子图的 X 轴标签的字体大小
            ),
            hoverlabel=dict(
                font_size=16,  # 设置悬浮标签的字体大小
                font_family='Arial, sans-serif',  # 设置悬浮标签的字体类型
                font_color='#F5F5F5'  # 设置悬浮标签的字体颜色
            ),
            legend=dict(
                y=1.15,  # 将图例放置在第一个子图的上方
                yanchor='bottom',  # 图例的底部对齐到 y 位置
                x=0.5,  # 水平居中
                xanchor='center',  # 水平方向以中心对齐
                orientation='h'  # 图例水平排列
            )
        )

        # 展示图表
        st.plotly_chart(fig, use_container_width=True)






























































