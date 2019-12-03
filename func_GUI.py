import os
import re
import sys
import time
from collections import OrderedDict
from itertools import permutations
from tkinter import *
from tkinter import colorchooser, filedialog, messagebox, simpledialog, ttk

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from func_X import Xyy

class App():
    def __init__(self, window):
        self.window = window
        self.initWidgets()

        self.pdf_path = tuple()
        self.el = 1
        self.ael = 180
        self.phi12 = 0
        self.phi23 =0
        self.data = []
        self.title = []
        self.cal_rsl = []  # 保存计算总结果的list，其元素为每张卡片的结果(格式为pandas.DataFrame)
        self.rgb = ('#000000', 'black')
        
    def initWidgets(self):
        # 初始化菜单、工具条用到的图标
        self.init_icons()
        # 调用init_menu初始化菜单
        self.init_menu()
        #----------------------------------------------------------------------------------
        # 创建第一个容器
        fm1 = Frame(self.window)
        # 该容器放在左边排列
        fm1.pack(side=TOP, fill=BOTH, expand=NO)

        ttk.Label(fm1, text='File Path:', font=('StSong', 20, 'bold')).pack(side=LEFT, ipadx=5, ipady=5, padx= 10)
        # 创建字符串变量，用于传递PDF卡片地址
        self.pdf_adr = StringVar()
        # 创建Entry组件，将其textvariable绑定到self.pdf_adr变量
        ttk.Entry(fm1, textvariable=self.pdf_adr,
            width=24,
            font=('StSong', 20, 'bold'),
            foreground='#8080c0').pack(side=LEFT, ipadx=5, ipady=5)#fill=BOTH, expand=YES)
        ttk.Button(fm1, text='...',
            command=self.open_filenames # 绑定open_filenames方法
            ).pack(side=LEFT, ipadx=1, ipady=5)
        #----------------------------------------------------------------------------------
        # 创建Labelframe容器
        lf = ttk.Labelframe(self.window, text='|d1> + |d3> = |d2>',
            padding=10)
        lf.pack(side=TOP, fill=BOTH, expand=NO, padx=10, pady=10)
        books = ['d1(Å):', 'd2(Å):', 'd3(Å):']
        self.d1, self.d2, self.d3 = DoubleVar(), DoubleVar(), DoubleVar()
        dis = [self.d1, self.d2, self.d3]
        # 使用循环创建多个Label和Entry，并放入Labelframe中,用于输入晶面距信息
        for book, d in zip(books, dis):
            Label(lf, font=('StSong', 20, 'bold'), text=book).pack(side=LEFT, padx=5, pady=10)
            ttk.Entry(lf, textvariable=d,
                width=3,
                font=('StSong', 20, 'bold'),
                foreground='#8080c0').pack(side=LEFT, ipadx=5, ipady=5, padx=15, pady=10)
        #-----------------------------------------------------------------------------------
        # 创建第二个容器
        fm2 = Frame(self.window)
        fm2.pack(side=TOP, fill=BOTH, expand=YES)
        # 创建第二个容器的子容器----------------------------
        fm2_0 = Frame(fm2)
        fm2_0.pack(side=LEFT, fill=BOTH, expand=YES)
        self.result = Text(fm2_0, 
            width=44,
            height=10,
            font=('StSong', 14),
            foreground='gray')
        self.result.pack(side=LEFT, fill=BOTH, expand=YES)
        # 创建Scrollbar组件，设置该组件与result的纵向滚动关联
        scroll_y = Scrollbar(fm2_0, command=self.result.yview)
        scroll_y.pack(side=RIGHT, fill=Y)
        # 设置result的纵向滚动影响scroll滚动条
        self.result.configure(yscrollcommand=scroll_y.set)
        # 创建第二个容器的子容器----------------------------
        fm2_1 = Frame(fm2)
        fm2_1.pack(side=LEFT, fill=BOTH, expand=YES)
        work_button = Button(fm2_1, text = 'Start work', 
            bd=3, width = 10, height = 1, 
            command = self.start_work, 
            activebackground='black', activeforeground='white')
        work_button.pack(side=TOP, ipadx=1, ipady=5, pady=10)
        export_button = Button(fm2_1, text = 'Export data', 
            bd=3, width = 10, height = 1, 
            command = self.save_as_csv, 
            activebackground='black', activeforeground='white')
        export_button.pack(side=TOP, ipadx=1, ipady=5, pady=10)
        new_button = Button(fm2_1, text = 'New project', 
            bd=3, width = 10, height = 1, 
            command = self.new_path, 
            activebackground='black', activeforeground='white')
        new_button.pack(side=TOP, ipadx=1, ipady=5, pady=10)

    # 创建menubar
    def init_menu(self):
        # '初始化菜单的方法'
        # 定义菜单条所包含的3个菜单
        menus = ('文件', '编辑', '帮助')
        # 定义菜单数据
        items = (OrderedDict([
                # 每项对应一个菜单项，后面元组第一个元素是菜单图标，
                # 第二个元素是菜单对应的事件处理函数
                ('新建', (None, self.new_project)),
                ('打开', (None, self.open_filenames)),
                ('打开文件夹', (None, self.open_dir)),
                ('另存为', OrderedDict([('CSV',(None, self.save_as_csv)),
                        ('Excel',(None, self.save_as_excel))])),
                ('-1', (None, None)),
                ('退出', (None, self.window.quit)),
                ]),
            OrderedDict([('φ12(degree)',(None, self.set_phi12)), 
                ('φ23(degree)',(None, self.set_phi23)),
                ('-1',(None, None)),
                ('晶面距误差限',(None, self.distance_error_limit)),
                ('角度误差限',(None, self.angle_error_limit)),
                ('-2',(None, None)),
                # 二级菜单
                ('更多', OrderedDict([
                    ('显示图谱',(None, self.plot_card)),
                    ('选择颜色',(None, self.select_color))
                    ]))
                ]),
            OrderedDict([('帮助主题',(None, None)),
                ('-1',(None, None)),
                ('关于', (None, None))]))
        # 使用Menu创建菜单条
        menubar = Menu(self.window)
        # 为窗口配置菜单条，也就是添加菜单条
        self.window['menu'] = menubar
        # 遍历menus元组
        for i, m_title in enumerate(menus):
            # 创建菜单
            m = Menu(menubar, tearoff=0)
            # 添加菜单
            menubar.add_cascade(label=m_title, menu=m)
            # 将当前正在处理的菜单数据赋值给tm
            tm = items[i]
            # 遍历OrderedDict,默认只遍历它的key
            for label in tm:
                print(label)
                # 如果value又是OrderedDict，说明是二级菜单
                if isinstance(tm[label], OrderedDict):
                    # 创建子菜单、并添加子菜单
                    sm = Menu(m, tearoff=0)
                    m.add_cascade(label=label, menu=sm)
                    sub_dict = tm[label]
                    # 再次遍历子菜单对应的OrderedDict，默认只遍历它的key
                    for sub_label in sub_dict:
                        if sub_label.startswith('-'):
                            # 添加分隔条
                            sm.add_separator()
                        else:
                            # 添加菜单项
                            sm.add_command(label=sub_label,image=None,
                                command=sub_dict[sub_label][1], compound=LEFT)
                elif label.startswith('-'):
                    # 添加分隔条
                    m.add_separator()
                else:
                    # 添加菜单项
                    m.add_command(label=label,image=None,
                        command=tm[label][1], compound=LEFT)
    # 生成所有需要的图标
    def init_icons(self):
        self.window.filenew_icon = PhotoImage(name='D:/pyfold/重构/app/images/filenew.png')
        self.window.fileopen_icon = PhotoImage(name='D:/pyfold/重构/app/images/fileopen.png')
        self.window.save_icon = PhotoImage(name='D:/pyfold/重构/app/images/save.png')
        self.window.saveas_icon = PhotoImage(name='D:/pyfold/重构/app/images/saveas.png')
        self.window.signout_icon = PhotoImage(name='D:/pyfold/重构/app/images/signout.png')
    # 新建项目
    def new_project(self):
        self.pdf_path = tuple()
        self.el = 1
        self.ael = 180
        self.phi12 = 0
        self.phi23 =0
        self.data = []
        self.title = []
        self.cal_rsl = []
        self.pdf_adr.set('')
        self.d1.set(0.0)
        self.d2.set(0.0)
        self.d3.set(0.0)
        self.result.delete(0.0, 'end')
    # 新建路径
    def new_path(self):
        self.pdf_path = tuple()
        self.data = []
        self.title = []
        self.cal_rsl = []
        self.pdf_adr.set('')
        self.result.delete(0.0, 'end')

    def open_filenames(self):
        # 调用askopenfile方法获取多个打开的文件名
        # pdf_path为一个tuple
        self.pdf_path = filedialog.askopenfilenames(title='打开多个文件',
            filetypes=[("文本文件", "*.txt"), ('Python源文件', '*.py')], # 只处理的文件类型
            initialdir='d:/') # 初始目录
        self.pdf_adr.set(self.pdf_path)

    def open_dir(self):
            # 调用askdirectory方法打开目录
        self.pdf_path = filedialog.askdirectory(title='打开目录',
            initialdir='d:/') # 初始目录
        self.pdf_adr.set(self.pdf_path)
        # print(type(self.pdf_path))
        
    def distance_error_limit(self):
        # 调用askfloat函数生成一个让用户输入浮点数的对话框
        self.el = simpledialog.askfloat("晶面距误差限", "输入晶面距误差限(Å):",
            initialvalue=0.3, minvalue=0.001, maxvalue=10)
    
    def angle_error_limit(self):
        self.ael = simpledialog.askfloat("晶面距误差限", "输入晶面距误差限(degree):",
            initialvalue=5, minvalue=0.001, maxvalue=180)

    def set_phi12(self):
        self.phi12 = simpledialog.askfloat("<d1, d2>", "输入测得的d1与d2的夹角(degree):",
            initialvalue=0)

    def set_phi23(self):
        self.phi23 = simpledialog.askfloat("<d2, d3>", "输入测得的d2与d3的夹角(degree):",
            initialvalue=0)

    def start_work(self):
        if self.pdf_path:
            if isinstance(self.pdf_path, str):
                os.chdir(self.pdf_path)
                start = time.time()
                for pdf_path in os.listdir():
                    example = Xyy(pdf_path, self.el, self.ael, self.d1.get(), self.d2.get(), self.d3.get(), self.phi12, self.phi23)
                    try:
                        example.getPdfInfo()
                        self.data.append(example.data)
                        self.title.append(example.title)
                        rsl = example.fit()
                        self.cal_rsl.append(rsl)
                        if rsl.empty:
                            self.result.insert('end', 'No resolution in Card: {}'.format(example.title))
                        elif rsl.empty == False:
                            self.result.insert('end', rsl)
                    except UnboundLocalError:
                        self.result.insert('end', 'Invalid Card: {}'.format(example.title))
                end = time.time()
                self.result.insert('end', '计算结果用时：{} s'.format(end-start))
            elif isinstance(self.pdf_path, tuple):
                start = time.time()
                for pdf_path in self.pdf_path:
                    example = Xyy(pdf_path, self.el, self.ael, self.d1.get(), self.d2.get(), self.d3.get(), self.phi12, self.phi23)
                    try:
                        example.getPdfInfo()
                        self.data.append(example.data)
                        self.title.append(example.title)
                        rsl = example.fit()
                        self.cal_rsl.append(rsl)
                        if rsl.empty:
                            self.result.insert('end', 'No resolution in Card: {}'.format(example.title))
                        elif rsl.empty == False:
                            self.result.insert('end', rsl)
                    except UnboundLocalError:
                        self.result.insert('end', 'Invalid Card: {}'.format(example.title))
                end = time.time()
                self.result.insert('end', '计算结果用时：{} s'.format(end-start))
        else:
            messagebox.showinfo(title='警告',message='请选择有效文件！')

    def save_as_csv(self):
        if len(self.cal_rsl) > 0:
            save_path = filedialog.asksaveasfilename(title='保存文件', 
            filetypes=[("逗号分隔符文件", "*.csv")], # 只处理的文件类型
            initialdir='d:/')
            for rsl, tit in zip(self.cal_rsl, self.title):
                if rsl.empty == False:
                    rsl.to_csv(save_path+tit[:11]+'.csv')
        else:
            messagebox.showinfo(title='警告',message='结果为空，请重新选择源文件！')

    def save_as_excel(self):
        if len(self.cal_rsl) > 0:
            messagebox.showinfo(title='提醒',message='该功能未完善')
        else:
            messagebox.showinfo(title='警告',message='结果为空，请重新选择源文件！')

    def select_color(self):

        self.rgb = colorchooser.askcolor(parent=self.window, title='选择线条颜色',
            color = 'black')
        self.result.insert('end', self.rgb)

    def plot_card(self):
        if self.data[0].empty == False:
            self.data[0].plot(kind = 'bar', x='2-Theta', y='I(f)',
            yticks = range(0,150,20), rot=60, fontsize=10, 
            label =self.title[0], color = self.rgb[1])
            plt.show()
        else:
            messagebox.showinfo(title='警告',message='结果为空，请重新选择源文件！')
