
# 传地址演示
def ts1():
    class Number:
        value = None

        def __init__(self, value):
            self.value = value

        def add(self, n):
            return self.value + n.value

        def reduce(self, n):
            return self.value - n.value

    def P(w, x, y, z):
        y.value = y.value * w.value
        z.value = z.value + x.value

    a = Number(5)
    b = Number(3)
    P(Number(a.add(b)), Number(a.reduce(b)), a, a)
    print(a.value)


def ts2():
    class Number:
        value = None

        def __init__(self, value):
            self.value = value

        def add(self, n):
            self.value = self.value + n.value

    # def P(w, x, y, z):
    #     y = Number(y.add(w))
    #     z =


ts1()