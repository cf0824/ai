

def main():
    value = '01000004C20050010000'

    print(f"实际值: {value}, 类型: {type(value)}")

    # 根据类型处理：
    if isinstance(value, int):
        # 如果已经是整数，直接使用
        result = value
    elif isinstance(value, str):
        # 如果是字符串，尝试按十六进制解析
        result = int(value, 16)
    else:
        # 其他情况
        result = int(str(value))
    print(result)

if __name__ == '__main__':
    main()

