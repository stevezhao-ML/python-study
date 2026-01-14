def testnumber(tester):
    while True:
        input1 = input(tester)
        try:
            number = float(input1)
            return number
        except ValueError:
            print("你输入的不是数字哦，请输入数字：")
print("你好，这是一个只能进行对两个数做加减乘除运算的计算器")
a = testnumber(("请输入第1个数字："))
b = testnumber("请输入第2个数字：")
while True:
        cc = input("请输入你要做的运算,请输入‘+ - * /’中的一种： ")
        if cc in ['+','-','*','/']:
            break
        print("你输入的不是加减乘除哦，请输入你要的运算“+ - * /”：")




if cc == "+":
    print("加法运算结果是：", a + b)
elif cc == "-":
    print("减法运算结果是：", a - b)
elif cc == "*":
    print("乘法运算结果是：", a * b)
elif cc == "/":
    print("除法运算结果是：", a / b)

        
                    