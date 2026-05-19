import matplotlib.pyplot as plt
import numpy as np
from io import BytesIO


def make_leida(data=None):
    plt.figure()
    # 用来正常显示中文标签
    plt.rcParams['font.sans-serif'] = ['SimHei']
    # 用来正常显示负号
    plt.rcParams['axes.unicode_minus'] = False
    datakv = {
        '市场信用状况': 18,
        '客户稳定性': 30,
        '市场拓展力': 20,
        '贸易真实性': 15
    }
    if data:
        datakv = data
    data = np.array([i for i in datakv.values()])
    label = np.array([i for i in datakv.keys()])
    # 1行1列第一个
    ax = plt.subplot(111, polar=True)
    # data里有几个数据，就把整圆360°分成几份
    angle = np.linspace(0, 2 * np.pi, len(data), endpoint=False)
    # 增加第一个angle到所有angle里，以实现闭合
    angles = np.concatenate((angle, [angle[0]]))
    # 增加第一个data到所有的data里，以实现闭合
    data = np.concatenate((data, [data[0]]))
    # 设置网格标签
    ax.set_thetagrids(angles * 180 / np.pi, label)
    # 绘制数据
    ax.plot(angles, data)
    # 设置0度位置
    ax.set_theta_zero_location('N')
    # 设置显示的极径范围
    ax.set_rlim(0, 50)
    # 设置极径标签位置
    ax.set_rlabel_position(0)
    # # 设置标题
    # ax.set_title('abc')

    # 绘制刻度线
    for j in np.arange(0, 50 + 10, 10):
        ax.plot(angles, 5 * [j], '-.', lw=0.5, color='black')
    # 绘制中间线
    for j in range(4):
        ax.plot([angles[j], angles[j]], [0, 100], '-', lw=0.5, color='black')
    # 隐藏最外圈的圆
    ax.spines['polar'].set_visible(False)
    # 隐藏圆形网格线
    ax.grid(False)
    bio = BytesIO()
    plt.savefig(bio)
    # plt.show()
    return bio


def make_zhexian(data=None):
    plt.figure()
    datakv = {
        'x': ['2021.01', '2021.02', '2021.03', '2021.04', '2021.05'],
        'data': {
            '市场信用状况': [18, 15, 11, 10, 11],
            '贸易真实性': [30, 25, 15, 14, 25],
            '客户稳定性': [20, 12, 11, 15, 11],
            '市场拓展力': [12, 15, 13, 14, 12]
        }
    }
    if data:
        datakv=data
    # 用来正常显示中文标签
    plt.rcParams['font.sans-serif'] = ['SimHei']
    # 用来正常显示负号
    plt.rcParams['axes.unicode_minus'] = False
    ax = plt.subplot(111)
    keys = list(datakv['data'].keys())
    values = datakv['data'].values()
    x = datakv['x']
    color = ['r', 'g', 'b', 'y']
    for i, value in enumerate(values):
        # ax.plot(x, value, color=color[i],label=keys[i],lw=1)
        ax.plot(x, value, label=keys[i],lw=1)
    # y轴取值范围
    plt.ylim((0,50))
    # 显示legend并配置位置为右上角https://blog.csdn.net/lanluyug/article/details/80002273
    plt.legend(loc=1)
    # 坐标轴标签
    plt.xlabel('时间')
    plt.ylabel('评分')
    # plt.show()
    bio = BytesIO()
    plt.savefig(bio)
    return bio


if __name__ == "__main__":
    # make_leida()
    make_zhexian()
