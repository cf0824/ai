import pysnooper


@pysnooper.snoop()
def main():
    a = 1
    for i in range(5):
        a += i


@pysnooper.snoop(depth=5)
def main2():
    class Test:
        a = 0
        def __init__(self):
            self.a = 1 + 2

        def test(self):
            self.a = 2 + 3

    t = Test()
    t.test()
    t.a = 3 + 5


# main()
main2()
