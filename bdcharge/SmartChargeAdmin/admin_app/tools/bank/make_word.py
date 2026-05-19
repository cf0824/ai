from docxtpl import DocxTemplate, InlineImage
from docx.shared import Mm
from . import make_chart
from admin_app.sys import public
import copy


CONTEXT = {
    'e_name':'企业名称',
    'per_no':'2021-07',#期号
    'total_quota_score':97,#企业总分
    'market_credit_score':11,#市场信用得分
    'trade_real_score':41,#贸易真实性得分
    'cus_stable':27,#客户稳定性得分
    'market_expand':18,#市场拓展力得分
    'industry':'金融行业',#行业
    'industry_num':12,#行业总数
    'ranking':6,#行业排名

    #近两年企业总分发展趋势折线图
    'chart_zx':
        {
        'x': ['2021.01', '2021.02', '2021.03', '2021.04', '2021.05'],
        'data': {
                '市场信用状况': [18, 15, 11, 10, 11],
                '贸易真实性': [30, 25, 15, 14, 25],
                '客户稳定性': [20, 12, 11, 15, 11],
                '市场拓展力': [12, 15, 13, 14, 12]
            }
        },

    #当月分数对比雷达图
    'chart_ld':{
        '市场信用状况': 18,
        '客户稳定性': 30,
        '市场拓展力': 20,
        '贸易真实性': 15
    },

    #贸易真实性对应二级指标的当期数据及合理阈值
    'tabledata': [
        {
            'quota_name': '总量差额率',
            'yz': '浮动小于等于50%时',
            'value': '-56.88%',
            'score':10
        },
        {
            'quota_name': '资金货物比',
            'yz': '浮动小于等于30%时',
            'value': '27.48%',
            'score':10
        },
        {
            'quota_name': '出口收汇率',
            'yz': '[75%,125%]范围内',
            'value': '27.48%',
            'score':10
        },
        {
            'quota_name': '进口付汇率',
            'yz': '[95%,125%]范围内',
            'value': '没有进口',
            'score':10
        }
    ],
    #贸易真实性对应二级指标的近两年变动趋势
    'chart_zx1':
    {
        'x': ['一月', '二月', '三月', '四月', '五月'],
        'data': {
                    '总量差额率': [18, 15, 11, 10, 11],
                    '资金货物比': [30, 25, 15, 14, 25],
                    '出口收汇率': [20, 12, 11, 15, 11],
                    '进口付汇率': [12, 15, 13, 14, 12]
                }
    },
    #贸易真实性所处段位
    'tran_real_total_score':'贸易真实性总分%s分，其中，得分%s-%s分为A段，得分 %s-%s分为B段，得分%s-%s分为C段，该企业贸易真实性得分%s分，位于%s段。'%(34,25,34,15,24,0,14,25,'A'),

    #客户稳定性对应二级指标变动趋势折线图
    'chart_zx2':{

        'x': ['2021.01', '2021.02', '2021.03', '2021.04', '2021.05'],
        'data': {
            '单一最大客户销量占比': [18, 15, 11, 10, 11],
            '销售额前三及最多客户占比': [30, 25, 15, 14, 25],
            '单一最大客户增长同比': [20, 12, 11, 15, 11],
            '销售额同比': [12, 15, 13, 14, 12],
            '企业一年以上老客户占比':[12,12,1,12,12]
            }

    },

    #客户稳定性对应二级指标当期数值表格
    'tabledata1': [
        {
            'quota_name': '单一最大客户销售量占比小于50%',
            'zb_data': 15,
            'score': 5
        },
        {
            'quota_name': '销售额前三占比及最多客户占比小于50%',
            'zb_data': 15,
            'score':  5
        },
        {
            'quota_name': '单一最大客户销售增长同比大于等于10%',
            'zb_data': 15,
            'score': 5
        },
        {
            'quota_name': '销售额同比增长大于等于10%',
            'zb_data': 15,
            'score':  5
        },
        {
            'quota_name': '企业一年以上老客户占比',
            'zb_data': 15,
            'score':  5
        },
        {
            'quota_name': '总分',
            'zb_data': '',
            'score':  5
        }
    ],

    #客户稳定性总分所处段位
    'cus_stable_total_score':'客户稳定性总分%s分，其中，得分%s-%s分为A段，得分 %s-%s分为B段，得分%s-%s分为C段，该企业贸易真实性得分%s分，位于%s段。'%(28,20,28,10,19,0,9,17,'B'),


#市场信用状况及市场拓展力表格
'tabledata2': [
        {
            'quota_name': '企业收付款中，福费延、出口保理、出口押汇、出口贴现等方式有几种',
            'zb_data': 15,
            'score': 5
        },
        {
            'quota_name': '企业结算方式中，托收、票汇、信用证、信汇、保函等方式有几种',
            'zb_data': 15,
            'score':  5
        },
        {
            'quota_name': '企业付汇方式中货到付款占比是否大于5%',
            'zb_data': 15,
            'score': 5
        },
        {
            'quota_name': '企业收汇方式中，预收货款占比是否大于5%',
            'zb_data': 15,
            'score':  5
        },
        {
            'quota_name': '总分',
            'zb_data': '',
            'score':  5
        }
    ],
'tabledata3': [
        {
            'quota_name': '企业经营年限',
            'zb_data': 15,
            'score': 5
        },
        {
            'quota_name': '同行业地区排名',
            'zb_data': 15,
            'score':  5
        },
        {
            'quota_name': '企业对外贸易进出口业务主要分布国家和地区是否大于等于3个',
            'zb_data': 15,
            'score': 5
        },
        {
            'quota_name': '最大出口国年限（1年，1-3年，3年以上）',
            'zb_data': 15,
            'score':  5
        },
        {
            'quota_name': '企业是否有新增客户',
            'zb_data': '有',
            'score':  5
        },
        {
            'quota_name': '总分',
            'zb_data': '',
            'score':  5
        }
    ],
    #市场信用状况总分所处段位
    'market_credit_total_score':'市场信用状况总分%s分，其中，得分%s-%s分为A段，得分 %s-%s分为B段，得分%s-%s分为C段，该企业贸易真实性得分%s分，位于%s段。'%(20,20,13,12,6,0,5,6,'B'),

    #市场拓展力总分所处段位
    'market_expend_total_score':'市场拓展力总分%s分，其中，得分%s-%s分为A段，得分 %s-%s分为B段，得分%s-%s分为C段，该企业贸易真实性得分%s分，位于%s段。'%(18,18,12,11,6,0,5,6,'B'),

    #总结
    'summary':'当月来看，该企业四个一级指标中，有%s个位于A段，有%s位于B段，有%s个位于C段。近三个月，该企业四个一级指标中，有 %s个均处于A段，有   %s个跨阶段上涨，有 %s个跨阶段下跌。'%(2,2,0,2,2,2)

}


def make_word(filename,context):
    context = copy.deepcopy(context)
    temp_path = public.localhome+"admin_app/tools/bank/bank_temp.docx"
    tpl = DocxTemplate(temp_path)
    chart1 = make_chart.make_leida()
    chart2 = make_chart.make_zhexian()
    # context = {
    #     'e_name': '测试企业',
    #     'per_no': '2021.03',
    #     'chart1': InlineImage(tpl, chart1, width=Mm(120), height=Mm(82.5)),
    #     'chart2': InlineImage(tpl, chart2, width=Mm(120), height=Mm(82.5)),
    #     'tabledata': [
    #         {
    #             'quota_name': '总量差额率',
    #             'yz': '浮动小于等于50%时',
    #             'value': '-56.88%'
    #         },
    #         {
    #             'quota_name': '资金货物比',
    #             'yz': '浮动小于等于30%时',
    #             'value': '27.48%'
    #         },
    #         {
    #             'quota_name': '出口收汇率',
    #             'yz': '[75%,125%]范围内',
    #             'value': '27.48%'
    #         },
    #         {
    #             'quota_name': '进口付汇率',
    #             'yz': '[95%,125%]范围内',
    #             'value': '没有进口'
    #         },
    #     ]
    # }
    # context = CONTEXT
    context['chart_zx'] = InlineImage(tpl, make_chart.make_zhexian(context['chart_zx']))
    context['chart_ld'] = InlineImage(tpl, make_chart.make_leida(context['chart_ld']))
    context['chart_zx1'] = InlineImage(tpl, make_chart.make_zhexian(context['chart_zx1']))
    context['chart_zx2'] = InlineImage(tpl, make_chart.make_zhexian(context['chart_zx2']))
    tpl.render(context=context)
    filepath = public.localhome+"rmbank/%s"%filename
    tpl.save(filepath)