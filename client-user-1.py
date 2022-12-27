import os
import time
import socket
import threading
import json  # json.dumps(some)打包   json.loads(some)解包

import tkinter
import ttkbootstrap as ttk
import tkinter.messagebox
from ttkbootstrap.constants import *
from tkinter.scrolledtext import ScrolledText  # 导入多行文本框用到的包
from playsound import playsound
from tkinter import filedialog

import requests
IntIP = requests.get('http://ifconfig.me/ip', timeout=1).text.strip()
print('get Internet IP:',IntIP)

version = 'v5.0'

IP = ''
PORT = ''
user = ''
Password = ''
listbox1 = ''  # 用于显示在线用户的列表框
ii = 0  # 用于判断是开还是关闭列表框
users = []  # 在线用户列表
chat = '【群发】'  # 聊天对象, 默认为群聊

#文件选择函数
def select_file():
    # 单个文件选择
    selected_file_path = filedialog.askopenfilename()  # 使用askopenfilename函数选择单个文件
    select_path.set(selected_file_path)
def select_files():
    # 多个文件选择
    selected_files_path = filedialog.askopenfilenames()  # askopenfilenames函数选择多个文件
    select_path.set('\n'.join(selected_files_path))  # 多个文件的路径用换行符隔开
def select_folder():
    # 文件夹选择
    selected_folder = filedialog.askdirectory()  # 使用askdirectory函数选择文件夹
    select_path.set(selected_folder)


# 登陆窗口
loginRoot = ttk.Window()
loginRoot.title('聊天室')
loginRoot['height'] = 240
loginRoot['width'] = 395
loginRoot.resizable(0, 0)  # 限制窗口大小

select_path = ttk.StringVar()

IP1 = ttk.StringVar()
IP1.set('43.249.193.233:64243')  # 默认显示的ip和端口
User = ttk.StringVar()
User.set('')
Password = ttk.StringVar()
Password.set('P^$$W0rd')

# 服务器标签
labelIP = ttk.Label(loginRoot, text='地址:端口')
labelIP.place(x=20, y=10, width=200, height=40)

entryIP = ttk.Entry(loginRoot, width=80, textvariable=IP1)
entryIP.place(x=120, y=10, width=260, height=40)

# 用户名标签
labelUser = ttk.Label(loginRoot, text='昵称')
labelUser.place(x=30, y=50, width=160, height=40)

entryUser = ttk.Entry(loginRoot, width=80, textvariable=User)
entryUser.place(x=120, y=50, width=260, height=40)

# 密码标签
labelPassword = ttk.Label(loginRoot, text='密码')
labelPassword.place(x=30, y=90, width=160, height=40)

entryPassword = ttk.Entry(loginRoot, width=80, textvariable=Password)
entryPassword.place(x=120, y=90, width=260, height=40)



# 登录按钮
def login(*args):
    global IP, PORT, user,Password
    IP, PORT = entryIP.get().split(':')  # 获取IP和端口号
    Password = entryPassword.get() #获取密码
    PORT = int(PORT)                     # 端口号需要为int类型
    user = entryUser.get()
    if not user:
        tkinter.messagebox.showerror('温馨提示', message='请输入任意的用户名！')
    else:
        loginRoot.destroy()                  # 关闭窗口

loginRoot.bind('<Return>', login)            # 回车绑定登录功能
but = ttk.Button(loginRoot, text='登录', command=login)
but.place(x=10, y=150, width=70, height=30)

loginRoot.mainloop()

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((IP, PORT))
if user:
    senddata = user
else:
    senddata = 'no'# 没有输入用户名则标记no
s.send(Password.encode())  # 发送密码
result_data = s.recv(1024) #接收密码的信息
result_data = result_data.decode() #解码密码
print('服务器返回密码信息为：' + result_data)
if not result_data == 'True':
    print('服务器返回密码信息错误，正在停止....')
    tkinter.messagebox.showerror('密码错误',message='请联系服务器管理员获取密码')
    exit()
# 如果没有用户名则将ip和端口号设置为用户名
s.send(senddata.encode()) # 发送用户名
addr = s.getsockname()  # 获取客户端ip和端口号
addr = addr[0] + ':' + str(addr[1])
if user == '':
    user = addr

# 聊天窗口
# 创建图形界面
root = ttk.Window()
root.title(version)  # 窗口命名为版本号
root['height'] = 400
root['width'] = 580
root.resizable(0, 0)  # 限制窗口大小

# 创建多行文本框
listbox = ScrolledText(root)
listbox.place(x=5, y=0, width=570, height=320)
# 文本框使用的字体颜色
listbox.tag_config('red', foreground='red')
listbox.tag_config('blue', foreground='blue')
listbox.tag_config('green', foreground='green')
listbox.tag_config('pink', foreground='pink')
listbox.insert(ttk.END, '欢迎 ！', 'red')
listbox.insert(ttk.END, str('软件版本：' + version), 'red')

# 表情功能代码部分
# 四个按钮, 使用全局变量, 方便创建和销毁
b1 = ''
b2 = ''
b3 = ''
b4 = ''
b5 = ''
b6 = ''
# 将图片打开存入变量中
p1 = ttk.PhotoImage(file='./emoji/facepalm.png')
p2 = ttk.PhotoImage(file='./emoji/smirk.png')
p3 = ttk.PhotoImage(file='./emoji/concerned.png')
p4 = ttk.PhotoImage(file='./emoji/smart.png')
p5 = ttk.PhotoImage(file='./emoji/poop.png')
p6 = ttk.PhotoImage(file='./emoji/smiling-with-sweat.png')
# 用字典将标记与表情图片一一对应, 用于后面接收标记判断表情贴图
dic = {'aa**': p1, 'bb**': p2, 'cc**': p3, 'dd**': p4, 'ee**': p5, 'ff**': p6}
ee = 0  # 判断表情面板开关的标志


# 发送表情图标记的函数, 在按钮点击事件中调用
def mark(exp):  # 参数是发的表情图标记, 发送后将按钮销毁
    global ee
    mes = exp + ':;' + user + ':;' + chat
    s.send(mes.encode())
    b1.destroy()
    b2.destroy()
    b3.destroy()
    b4.destroy()
    b5.destroy()
    b6.destroy()
    ee = 0

def mark_custom(exp):
    global ee
    mes = exp + ':;' + user + ':;' + chat
    s.send(mes.encode())

# 四个对应的函数
def bb1():
    mark('aa**')

def bb2():
    mark('bb**')

def bb3():
    mark('cc**')

def bb4():
    mark('dd**')

def bb5():
    mark('ee**')

def bb6():
    mark('ff**')


def express():
    global b1, b2, b3, b4, b5, b6, ee
    if ee == 0:
        ee = 1
        b1 = tkinter.Button(root, command=bb1, image=p1,
                            relief=ttk.FLAT, bd=0)
        b2 = tkinter.Button(root, command=bb2, image=p2,
                            relief=ttk.FLAT, bd=0)
        b3 = tkinter.Button(root, command=bb3, image=p3,
                            relief=ttk.FLAT, bd=0)
        b4 = tkinter.Button(root, command=bb4, image=p4,
                            relief=ttk.FLAT, bd=0)
        b5 = tkinter.Button(root, command=bb5, image=p5,
                            relief=ttk.FLAT, bd=0)
        b6 = tkinter.Button(root, command=bb6, image=p6,
                            relief=ttk.FLAT, bd=0)

        b1.place(x=5, y=248)
        b2.place(x=75, y=248)
        b3.place(x=145, y=248)
        b4.place(x=215, y=248)
        b5.place(x=285, y=248)
        b6.place(x=355, y=248)
    else:
        ee = 0
        b1.destroy()
        b2.destroy()
        b3.destroy()
        b4.destroy()
        b5.destroy()
        b6.destroy()


# 创建表情按钮
eBut = tkinter.Button(root, text='表情', command=express)
eBut.place(x=5, y=320, width=60, height=30)


'''bottom_1 = tkinter.Button(root, text="选择单个文件", command=select_file)#.grid(row=0, column=2)
bottom_1.place(x=180, y=320, width=120, height=30)
bottom_2 = tkinter.Button(root, text="选择多个文件", command=select_files)#.grid(row=1, column=2)
bottom_2.place(x=300, y=320, width=120, height=30)
bottom_3 = tkinter.Button(root, text="选择文件夹", command=select_folder)#.grid(row=2, column=2)
bottom_3.place(x=420, y=320, width=120, height=30)'''

# 创建多行文本框, 显示在线用户
listbox1 = tkinter.Listbox(root)
listbox1.place(x=445, y=0, width=130, height=320)


def showUsers():
    global listbox1, ii
    if ii == 1:
        listbox1.place(x=445, y=0, width=130, height=320)
        ii = 0
    else:
        listbox1.place_forget()  # 隐藏控件
        ii = 1


# 查看在线用户按钮
button1 = tkinter.Button(root, text='开关用户列表', command=showUsers)
button1.place(x=75, y=320, width=90, height=30)

# 创建输入文本框和关联变量
a = ttk.StringVar()
a.set('')
entry = ttk.Entry(root, width=120, textvariable=a)
entry.place(x=5, y=350, width=570, height=40)


def send(*args):
    # 没有添加的话发送信息时会提示没有聊天对象
    users.append('【群发】')
    print(chat)
    if chat not in users:
        tkinter.messagebox.showerror('错误', message='没有聊天对象!')
        return
    if chat == user:
        tkinter.messagebox.showerror('错误', message='自己不能和自己进行对话!')
        return
    mes = entry.get() + ':;' + user + ':;' + chat  # 添加聊天对象标记
    s.send(mes.encode())
    a.set('')  # 发送后清空文本框


# 创建发送按钮
button = tkinter.Button(root, text='发送', command=send)
button.place(x=515, y=353, width=60, height=30)
root.bind('<Return>', send)  # 绑定回车发送信息


# 私聊功能
def private(*args):
    global chat
    # 获取点击的索引然后得到内容(用户名)
    indexs = listbox1.curselection()
    index = indexs[0]
    if index > 0:
        chat = listbox1.get(index)
        # 修改客户端名称
        if chat == '【群发】':
            root.title(user)
            return
        ti = user + '  -->  ' + chat
        root.title(ti)


# 在显示用户列表框上设置绑定事件
listbox1.bind('<ButtonRelease-1>', private)

Playsound = 0

class MyThread(threading.Thread):
    global Playsound
    def run(self):
        global Playsound
        while True:
            time.sleep(0.01)
            if Playsound == 1:
                print('playsound')
                playsound('mixkit-message-pop-alert-2354.mp3')
                Playsound = 0
        pass

thread = MyThread()
thread.daemon = True
thread.start()

# 用于时刻接收服务端发送的信息并打印
def recv():
    global users,Playsound,Password
    while True:
        try:
            data = s.recv(1024)
            data = data.decode()
        except:
            s.close()
        # 没有捕获到异常则表示接收到的是在线用户列表
        try:
            data = json.loads(data)
            users = data
            listbox1.delete(0, ttk.END)  # 清空列表框
            number = ('   在线用户数: ' + str(len(data)))
            listbox1.insert(ttk.END, number)
            listbox1.itemconfig(ttk.END, fg='green', bg="#f0f0ff")
            listbox1.insert(ttk.END, '【群发】')
            listbox1.itemconfig(ttk.END, fg='green')
            for i in range(len(data)):
                listbox1.insert(ttk.END, (data[i]))
                listbox1.itemconfig(ttk.END, fg='green')
        except:
            data = data.split(':;')
            data1 = data[0].strip()  # 消息
            data2 = data[1]  # 发送信息的用户名
            data3 = data[2]  # 聊天对象
            markk = data1.split('：')[1]
            # 判断是不是图片
            pic = markk.split('#')
            # 判断是不是表情
            # 如果字典里有则贴图
            if (markk in dic) or pic[0] == '``':
                data4 = '\n' + data2 + '：'  # 例:名字-> \n名字：
                if data3 == '【群发】':
                    if data2 == user:  # 如果是自己则将则字体变为蓝色
                        listbox.insert(ttk.END, data4, 'blue')
                    else:
                        listbox.insert(ttk.END, data4, 'green')  # END将信息加在最后一行
                        Playsound = 1
                elif data2 == user or data3 == user:  # 显示私聊
                    listbox.insert(ttk.END, data4, 'red')  # END将信息加在最后一行
                    Playsound = 1
                listbox.image_create(ttk.END, image=dic[markk])
            elif markk[0:1] == '**':
                print('custom image')
                data4 = '\n' + data2 + '：'  # 例:名字-> \n名字：
                if data3 == '【群发】':
                    if data2 == user:  # 如果是自己则将则字体变为蓝色
                        listbox.insert(ttk.END, data4, 'blue')
                    else:
                        listbox.insert(ttk.END, data4, 'green')  # END将信息加在最后一行
                        Playsound = 1
                elif data2 == user or data3 == user:  # 显示私聊
                    listbox.insert(ttk.END, data4, 'red')  # END将信息加在最后一行
                    Playsound = 1
                #listbox.image_create(ttk.END, image=dic[markk])

            else:
                data1 = '\n' + data1
                if data3 == '【群发】':
                    if data2 == user:  # 如果是自己则将则字体变为蓝色
                        listbox.insert(ttk.END, data1, 'blue')
                    else:
                        listbox.insert(ttk.END, data1, 'green')  # END将信息加在最后一行
                        Playsound = 1
                    if len(data) == 4:
                        listbox.insert(ttk.END, '\n' + data[3], 'pink')
                elif data2 == user or data3 == user:  # 显示私聊
                    listbox.insert(ttk.END, data1, 'red')  # END将信息加在最后一行
                    Playsound = 1
            listbox.see(ttk.END)  # 显示在最后

r = threading.Thread(target=recv)
r.start()  # 开始线程接收信息

root.mainloop()
s.close()  # 关闭图形界面后关闭TCP连接
