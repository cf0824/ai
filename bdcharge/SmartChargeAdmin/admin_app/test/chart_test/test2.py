a=[0.8,1.2,1.5,1.7,1.8,2.3,2.8,3.1,3.7,4.2,4.5,5.2]


def get_index(_list,value,size=1):
    if len(_list)<=0:
        return None
    min_abs=abs(_list[0]-value)
    min_index=0
    for i,item in enumerate(_list):
        if abs(item-value)<min_abs:
            min_abs=abs(item-value)
            min_index=i
    if min_abs>size:
        return None
    return min_index

for item in range(10):
    index=get_index(a,item)
    print(item,a[index],index)

