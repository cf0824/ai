import time


# 两个列表取交集


a = [item for item in range(1000000)]
b = [item for item in range(1000000)]
start = time.time()

# c = []

# 效率最低
# for i in a:
#     for j in b:
#         if i==j:
#             c.append(i)

# 效率一般
# for i in a:
#     if i in b:
#         c.append(i)

# 效率最高
c = list(set(a).intersection(set(b)))

print(len(c))

end = time.time()

print(end-start)
