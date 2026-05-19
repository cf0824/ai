import pysnooper


@pysnooper.snoop(depth=5)
def main():
    # def foo(arg):
    #     arg = 5
    #     print(arg)
    #
    # x = 1
    # foo(x)  # 输出5
    # print(x)  # 输出1

    def foo(arg):
        arg.append(3)

    x = [1, 2]
    print(x)  # 输出[1, 2]
    foo(x)
    print(x)  # 输出[1, 2, 3]


# main()
#
# exit(0)
#
#
# def P(w, x, y, z):
#     y = y * w
#     z = z + w
#
#
# a = 5
# b = 3
# P(a + b, a - b, a, a)
# print(a)



