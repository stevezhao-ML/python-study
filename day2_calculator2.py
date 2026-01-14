def testnumber(tester):
    while True:
        input1 = input(tester)
        try:
            number = float(input1)
            return number
        except ValueError:
            print("你输入的不是数字哦，请输入数字：")
def calcu(c, d, e) :          
    if e == "+":
        return c + d
    elif e == "-":
        return c - d
    elif e == "*":
        return c * d
    elif e == "/":
        return c / d
        
            
print("你好，这是一个只能进行对两个数做加减乘除运算的计算器")
while True:
    a = testnumber(("请输入第1个数字："))
    b = testnumber("请输入第2个数字：")
    while True:
        cc = input("请输入你要做的运算,请输入‘+ - * /’中的一种： ")
        if cc in ['+','-','*','/']:
            break
        print("你输入的不是加减乘除哦，请输入你要的运算“+ - * /”：")
    print(cc, "法运算结果是：", round(calcu(a, b, cc),2))
    tryagain = input("是否要再算一次？是的话请输入‘y’,按任意键退出：")
    if tryagain.lower() != "y":
        break
