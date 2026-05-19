#-*- coding: utf-8 -*-

# https://zhuanlan.zhihu.com/p/351424074


import numpy as np
import matplotlib.pyplot as plt

plt.rcParams['font.sans-serif']=['SimHei'] #用来正常显示中文标签
plt.rcParams['axes.unicode_minus']=False #用来正常显示负号

results = {"大学英语": 87, "高等数学": 79, "体育": 95, "计算机基础": 92, "程序设计": 85}
data_length = len(results)
angles = np.linspace(0, 2*np.pi, data_length, endpoint=False)
print('angles=',angles)
labels = [key for key in results.keys()]
score = [v for v in results.values()]
score_a = np.concatenate((score, [score[0]]))
angles = np.concatenate((angles, [angles[0]]))
labels = np.concatenate((labels, [labels[0]]))
fig = plt.figure(figsize=(10, 6), dpi=100)
fig.suptitle("计算机专业大一（上）")
ax = plt.subplot(121, polar=True)
for j in np.arange(0, 100+20, 20):
    ax.plot(angles, 6*[j], '-.', lw=0.5, color='black')
for j in range(5):
    ax.plot([angles[j], angles[j]], [0, 100], '-.', lw=0.5, color='black')
ax.spines['polar'].set_visible(False)
ax.grid(False)
for a, b in zip(angles, score_a):
    ax.text(a, b+5, '%.00f' % b, ha='center', va='center', fontsize=12, color='b')


ax.set_thetagrids(angles*180/np.pi, labels)
ax.set_theta_zero_location('N')
ax.set_rlim(0, 100)
ax.set_rlabel_position(0)
ax.set_title('啦啦啦')


# ax2 = plt.subplot(122, polar=True)
# ax, data, name = [ax1, ax2], [score_a, score_b], ["弓长张", "口天吴"]
# for i in range(2):
#     for j in np.arange(0, 100+20, 20):
#         ax[i].plot(angles, 6*[j], '-.', lw=0.5, color='black')
#     for j in range(5):
#         ax[i].plot([angles[j], angles[j]], [0, 100], '-.', lw=0.5, color='black')
#     ax[i].plot(angles, data[i], color='b')
#     # 隐藏最外圈的圆
#     ax[i].spines['polar'].set_visible(False)
#     # 隐藏圆形网格线
#     ax[i].grid(False)
#     for a, b in zip(angles, data[i]):
#         ax[i].text(a, b+5, '%.00f' % b, ha='center', va='center', fontsize=12, color='b')
#     ax[i].set_thetagrids(angles*180/np.pi, labels)
#     ax[i].set_theta_zero_location('N')
#     ax[i].set_rlim(0, 100)
#     ax[i].set_rlabel_position(0)
#     ax[i].set_title(name[i])
plt.show()