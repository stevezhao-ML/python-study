def get_number(prompt):
    while True:
        user_input = input(prompt)
        try:
            # 尝试把输入转成浮点数
            number = float(user_input)
            return number  # 成功就返回
        except ValueError:
            # 如果转换失败，说明不是数字
            print("输入错误，请输入一个数字哦！")

# 使用函数获取两个数字
a = get_number("请输入第一个数字吧：")
b = get_number("再输入一个吧：")


while True:
    cc = input("你想做什么样的运算呢（+-*/）")
    if cc in ['+','-','*','/']:
        break
    print("输入错误，请重新输入“+，-，*，、”")
    
if cc == "+":
    print("保留小数点后2位的结果是：", round((a + b), 2))
          
elif cc == "-":
    print("保留小数点后2位的结果是：", round((a - b), 2))
elif cc == "*":
    print("保留小数点后2位的结果是：", round((a * b), 2))
    
elif cc == "/":
    print("保留小数点后2位的结果是：", round((a / b), 2))