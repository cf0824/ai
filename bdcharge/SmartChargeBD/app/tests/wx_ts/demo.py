from WXBizDataCrypt import WXBizDataCrypt

def main():
    appId = 'wx74cec1a81fb0cc01'
    sessionKey = 'zdvPI6fUbLXNF0U/MSpmgA=='
    encryptedData = 'b4mBa62U2vnbpfT29DMxQAO/f7/pdr72bzYvdXG/5kGgrAFH8hfV5VZkMj3kbT39TSpcmTvOMuvfk3U3cMIC7nH8CqLCMNAQRwF4DYyAV5WMfh7MVtsGjs7as3AO4J/Cyh4C8weO57+/59UifS8ZBgLJucDXCYX+WntUjbsZFfQ6GJZ6szwRZB91spNUKz0BwNoAht1khGzdxXrYhpB7dMnCqFwl+lw/Bofhm5j2Hyjp8Wf7YCvEf11ggQqNJSDiGPbaX4yzrUQGv7GtJ4kO95Eq7EJ2HOzJVH4EPjNVdmHlTXxDILZJYrHEmupaMnXzMxNciRWV/iDoT0yAjohmwFuAaB4sdtwN6gMrwuiAcJ+hJUz1cB5xYfL2PyPYhVtz0f8XRmOHUU4EsvAMZCSKIQ=='
    iv = '7GWEUByTV88GKfUGU781pw=='

    pc = WXBizDataCrypt(appId, sessionKey)

    print(pc.decrypt(encryptedData, iv))

if __name__ == '__main__':
    main()
