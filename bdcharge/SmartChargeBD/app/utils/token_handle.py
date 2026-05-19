import jwt
import time
from SmartChargeBD.settings import SECRET_KEY

secret = SECRET_KEY


def create_token(data, vaild_time=24 * 60 * 60):
    payload = {
        'exp': int(time.time()) + vaild_time,
        'iat': int(time.time()),
        'data': data
    }
    s = jwt.encode(payload, secret, algorithm='HS256')
    return s


def verify_token(token):
    data = {}
    try:
        payload = jwt.decode(token, secret, algorithms=['HS256'])
    except:
        return False, data
    data = payload['data']
    print(payload)
    return True, data


if __name__ == '__main__':
    token = create_token({'user_id': 2}, 24 * 60 * 60)
    print('token=', token, type(token))
    # token = b'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHAiOjE2MjQ2OTc0MTcsImlhdCI6MTYyNDYxMTAxNywiZGF0YSI6eyJ1c2VyX2lkIjoyLCJ0b2tlbl90eXBlIjoiZ3JhbnQifX0.UBuofqdjLeCBJJqmiLlbkribXDxyX8x49UukXLXlkvo'
    token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3MjkwNDMwNTgsImlhdCI6MTcyODk1NjY1OCwiZGF0YSI6eyJ1c2VyX2lkIjoyfX0.vV1Vr0S5GwbBf2-M2V2-Mgcszy83mVSXbCscEbMjFPM'
    success, data = verify_token(token)
    print(success, data)

    # token=b'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHAiOjE1OTcyMTg0MjEsImlhdCI6MTU5NzEzMjAyMSwiZGF0YSI6eyJ1c2VyX2lkIjoxfX0.vELQy93q5o-yy_EBWUdOJ3gxTiqMQVnRrpTxL2qEFZI'
    # print(str(token,encoding='utf-8'))
