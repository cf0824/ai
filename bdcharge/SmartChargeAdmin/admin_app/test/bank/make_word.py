from docxtpl import DocxTemplate, InlineImage
from docx.shared import Mm
import make_chart

tpl = DocxTemplate('bank_temp.docx')
chart1 = make_chart.make_leida()
chart2 = make_chart.make_zhexian()
context = {
    'e_name': '测试企业',
    'per_no': '2021.03',
    'chart1': InlineImage(tpl, chart1,width=Mm(120), height=Mm(82.5)),
    'chart2': InlineImage(tpl, chart2,width=Mm(120), height=Mm(82.5)),
    'tabledata': [
        {
            'quota_name': '总量差额率',
            'yz': '浮动小于等于50%时',
            'value': '-56.88%'
        },
        {
            'quota_name': '资金货物比',
            'yz': '浮动小于等于30%时',
            'value': '27.48%'
        },
        {
            'quota_name': '出口收汇率',
            'yz': '[75%,125%]范围内',
            'value': '27.48%'
        },
        {
            'quota_name': '进口付汇率',
            'yz': '[95%,125%]范围内',
            'value': '没有进口'
        },
    ]
}
tpl.render(context=context)
tpl.save('res.docx')


chart1_data = {
    'x': ['2021.01', '2021.02', '2021.03', '2021.04', '2021.05'],
    'data': {
        '市场信用状况': [18, 15, 11, 10, 11],
        '贸易真实性': [30, 25, 15, 14, 25],
        '客户稳定性': [20, 12, 11, 15, 11],
        '市场拓展力': [12, 15, 13, 14, 12]
    }
}