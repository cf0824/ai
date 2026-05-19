from docxtpl import DocxTemplate, InlineImage
from docx.shared import Mm


img = open('a_1.png', 'rb')
tpl = DocxTemplate('temp.docx')
context = {
    'e_name': '测试企业',
    'pro_no': '2021.03',
    'chart1': InlineImage(tpl, img,width=Mm(120), height=Mm(82.5)),
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
tpl.save('tmp_res.docx')
