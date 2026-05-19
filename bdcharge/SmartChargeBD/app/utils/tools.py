from math import radians, cos, sin, asin, sqrt
from urllib.request import urlopen, quote
import json
from urllib import parse

#字符串替换*
def strReplaceStar(str,start,end,rep='*'):
    if not str:
        return str
    str=str[:start-1]+rep*(end-start+1)+str[end:]
    return str


#经纬度距离计算
def haversine(lon1, lat1, lon2, lat2):  # 经度1，纬度1，经度2，纬度2 （十进制度数）
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees)
    """
    # 将十进制度数转化为弧度
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # haversine公式
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))
    r = 6371  # 地球平均半径，单位为公里
    return c * r * 1000


#wgs84坐标转百度坐标
def wgs84tobaidu(x, y):
    data = str(x) + ',' + str(y)
    output = 'json'
    url = 'http://api.map.baidu.com/geoconv/v1/?coords=' + data + '&from=1&to=5&output=' + output + '&ak=BiESdd7BDMsdnj4v7m2G1sb7iwtHej7B'
    req = urlopen(url)
    res = req.read().decode()
    temp = json.loads(res)
    baidu_x = 0
    baidu_y = 0
    if temp['status'] == 0:
        baidu_x = temp['result'][0]['x']
        baidu_y = temp['result'][0]['y']

    return baidu_x, baidu_y


#wgs84坐标转腾讯坐标
def wgs84totx(x,y):
    locations=str(x)+','+str(y)
    key='L54BZ-GIPRS-5XQOQ-6LODC-ANVGT-O3FXE'
    url="https://apis.map.qq.com/ws/coord/v1/translate?locations=%s&type=1&key=%s"%(locations,key)
    req = urlopen(url)
    res = req.read().decode()
    temp = json.loads(res)
    tx_x,tx_y=0,0
    if temp.get('status')==0 and len(temp.get('locations',[]))>0:
        tx_x=temp.get('locations')[0].get('lat')
        tx_y=temp.get('locations')[0].get('lng')
    return tx_x,tx_y


#腾讯坐标解析
def tx_gps_dec(x,y):
    location='%s,%s'%(x,y)
    key='L54BZ-GIPRS-5XQOQ-6LODC-ANVGT-O3FXE'
    url='https://apis.map.qq.com/ws/geocoder/v1/?location=%s&key=%s'%(location,key)
    req = urlopen(url)
    res = req.read().decode()
    temp = json.loads(res)
    address=''
    if temp.get('status')==0:
        result=temp.get('result',{})
        ad_info=result.get('ad_info',{})
        city=ad_info.get('city','')
        district=ad_info.get('district','')
        address_reference=result.get('address_reference',{})
        crossroad=address_reference.get('crossroad',{})
        crossroad_title=crossroad.get('title','')
        address=city+district+crossroad_title
    return address


#url编码
def url_encode(str):
    return parse.quote_plus(str)



if __name__=='__main__':
    pass
    # str='410182199812345678'
    # res=strReplaceStar(str,7,12)
    # print(res)

    # res=haversine(113.86468530474085, 34.03523223194997,113.875227,34.03991)
    # print(res)

    # res=wgs84tobaidu(113.85236,34.030647)
    # print(res)

    # url='https://wx2.qinyushop.com/exposure-table'
    # res=url_encode(url)
    # print(res)

    x,y=wgs84totx('34.030617','113.852516')
    print(x,y)
    tx_gps_dec(x,y)