#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2020/5/3 12：00
# @Author : wizard
# @OS : Ubuntu 18.04
# @File : yqtb.py
# @Enviroment : Anaconda 3, chrome, chromedriver
# @Software : jupyter notebook
# @Packages : time, selenium, smtplib, email, schedule, re


# 引包
import time

# 调用selenium库，访问翱翔门户体温填报链接
from selenium import webdriver  # 从selenium库中调用webdriver模块
from selenium.webdriver.chrome.options import Options  # 从options模块中调用 Options类

# 发邮件提醒填报结果
import smtplib
from email.mime.text import MIMEText
from email.header import Header

import schedule  # 引入schedule,定时执行

import re  # 正则表达式分割字符

class Yqtb:
    # 变量初始化
    def __init__(self, name, passwd, send_QQ, passwds):
        # 翱翔门户账号及密码
        self.name = name
        self.passwd = passwd
        # QQ邮箱的账号及授权码(在邮箱设置中可以查到)
        self.send_QQ = send_QQ
        self.passwds = passwds
        # driver作为类的属性调用
        self.driver = self.chrome_drive()

    def chrome_drive(self):  # 设置chrome浏览器
        chrome_options = Options()
        chrome_options.add_argument('--headless')  # 静默模式
        # 不使用GPU
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument("window-size=1024,768")
        chrome_options.add_argument("--no-sandbox")  # 无图形界面
        # 明确调用的是chrome浏览器，并调用库中的相关函数
        driver = webdriver.Chrome(options=chrome_options)
        return driver

    def login_nwpu(self):  # 登陆翱翔门户
        # 访问翱翔门户，并等待加载完毕
        URL = 'https://uis.nwpu.edu.cn/cas/login? service=https%3A%2F%2Fecampus.nwpu.edu.cn%2Fportal- web%2Fj_spring_cas_security_check'
        self.driver.get(URL)
        time.sleep(5)
        # 登陆操作
        username = self.driver.find_element_by_id('username')
        username.clear()
        username.send_keys(f'{name}')
        password = self.driver.find_element_by_id('password')
        password.clear()
        password.send_keys(f'{passwd}')
        # 抓取登录按钮并点击，等待加载完毕
        self.driver.find_element_by_name('submit').click()
        time.sleep(5)

    def yqtb_nwpu(self):  # 疫情填报
        # 找到疫情填报的链接，并加载
        butt = self.driver.find_element_by_name('疫情每日填报')
        self.driver.execute_script("arguments[0].click();", butt)
        time.sleep(5)
        # 由于疫情每日填报会跳出子窗口，所以切换到子窗口操作
        all_handles = self.driver.window_handles
        self.driver.switch_to.window(all_handles[1])
        # 抓取“健康登记”位置，加载链接
        self.driver.find_element_by_class_name('icon-shangbao1').click()
        time.sleep(5)

        # 由于填报系统自带保留上次结果，所以直接选择上次结果上报
        # 抓取提交按钮，选择提交
        self.driver.find_element_by_class_name('weui-btn_primary').click()
        # 勾选本人承诺，并提交
        sub2 = self.driver.find_element_by_id('brcn')
        self.driver.execute_script("arguments[0].click();", sub2)
        self.driver.find_element_by_id('save_div').click()

        # 退出浏览器，以免占用内存
        self.driver.quit()

    def tianbao(self):  # 尝试填报，并给出反馈
        try:
            self.yqtb_nwpu()
            return '填报成功'
        except Exception as e:
            return f'填报失败，报错如下：\n{e}'

    def send_mail(self):  # 通过QQ邮箱发送邮件，提醒填报是否成功
        from_addr = f'{send_QQ}@qq.com'
        password = str(passwds)

        # 收信方邮箱
        to_addrs = [f'{from_addr}']

        # 发信服务器
        SMTP_SERVER = 'smtp.qq.com'

        # 邮箱正文内容，第一个参数为内容，第二个参数为格式(plain为纯文本)，第三个参数为编码
        text = self.tianbao()
        msg = MIMEText(text, 'plain', 'utf-8')

        # 邮件头信息
        msg['From'] = Header(from_addr)
        msg['To'] = Header(",".join(to_addrs))
        msg['Subject'] = Header('疫情填报')

        # 开启发信服务，这里使用的是加密传输
        server = smtplib.SMTP_SSL(SMTP_SERVER)
        server.connect(SMTP_SERVER, 465)

        # 登录发信邮箱
        server.login(from_addr, password)

        # 发送邮件
        try:
            server.sendmail(from_addr, to_addrs, msg.as_string())
        except:
            send_mail(send_QQ, passwd)  # 如果不成功，就再来一次
        finally:
            # 关闭服务器
            server.quit()

    def start(self):
        self.login_nwpu()
        self.send_mail()
        

def shuru():  # 封装输入过程
    # 确定执行时间
    print("请指定填报时间")
    while True:
        tim = input("请以06:30的形式输入时间")
        hour = re.findall(r"[\w']+", tim)[0]
        second = re.findall(r"[\w']+", tim)[1]
        if int(hour) > 24 or int(second) >= 60:
            print("时间格式错误，请重新输入！")
        else:
            break

    # 确定执行账号
    print("请输入翱翔门户账号")
    name, passwd = 'abc', '123'
    if name != 'abc' and passwd != '123':
        print("已经输入账号，按该账号执行。")
    else:
        name = input("请输入学号：")
        passwd = input("请输入翱翔门户密码：")

    # 确定使用的QQ邮箱
    print("请输入收发邮箱（默认为同一邮箱）")
    send_QQ, passwds = '123', '123'
    if send_QQ != '123' and passwds != '123':
        print("已有QQ邮箱，将以此邮箱发送报告。")
    else:
        send_QQ = input("请输入要使用的QQ邮箱，仅需输入QQ号即可： ")
        passwds = input("请输入QQ邮箱的授权码： ")
    return tim, name, passwd, send_QQ, passwds
    
   
if __name__ == '__main__':
    tim, name, passwd, send_QQ, passwds = shuru()

    # 部署在每天的tim时刻执行job()函数的任务
    job = Yqtb(name, passwd, send_QQ, passwds)
    schedule.every().day.at(tim).do(job.start)

    # 检查部署的情况，如果任务准备就绪，就开始执行任务。
    while True:
        schedule.run_pending()
        time.sleep(5)
