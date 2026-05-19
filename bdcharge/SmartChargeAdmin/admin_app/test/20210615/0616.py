
# x = '1'
# a = float(x) if x is not None else x
# print(x)

bak_float = float

def myfloat(x):
    return bak_float(x) if x is not None else x

float = myfloat

x = None

print(float(x))
print(float('1'))

float = bak_float

float(None)