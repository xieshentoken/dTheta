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
        self.el = 0.1
        self.ael = 5
        self.phi12 = 0
        self.phi23 = 0
        self.order_n = 1
        self.data = []
        self.title = []
        self.cal_rsl = []  # 保存计算总结果的list，其元素为每张卡片的结果(格式为pandas.DataFrame)
        self.rgb = ('blue', '#454365')
        
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
        openfile_s = ttk.Button(fm1, text='...',
            command=self.open_filenames # 绑定open_filenames方法
            )
        openfile_s.pack(side=LEFT, ipadx=1, ipady=5)
            # 不知为何此处绑定双击事件报错："command takes 1 positional argument but 2 were given"
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
            command = self.save_as_excel, 
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
        menus = ('文件', '编辑', '程序', '帮助')
        # 定义菜单数据
        items = (OrderedDict([
                # 每项对应一个菜单项，后面元组第一个元素是菜单图标，
                # 第二个元素是菜单对应的事件处理函数
                ('新建', (None, self.new_project)),
                ('打开', (None, self.open_filenames)),
                ('打开文件夹', (None, self.open_dir)),
                ('另存为', OrderedDict([('CSV',(None, self.save_as_csv)),
                        ('Excel',(None, self.save_as_excel))])),
                ('载入测试参数', (None, self.load_para)),
                ('保存测试参数', (None, self.save_para)),
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
                ('衍射级数n',(None, self.set_n)),
                ('更多', OrderedDict([
                    ('显示图谱',(None, self.plot_card)),
                    ('选择颜色',(None, self.select_color))
                    ]))
                ]),
            OrderedDict([('计算晶面距',(None, self.insertapp)), 
                
                ]),
            OrderedDict([('帮助主题',(None, self.help)),
                ('-1',(None, None)),
                ('关于', (None, self.about))]))
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
                # print(label)
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
        # self.window.filenew_icon = PhotoImage(file=r"E:\pydoc\gittview\image\filenew.png")
        # self.window.fileopen_icon = PhotoImage(name='E:/pydoc/tkinter/images/fileopen.png')
        # self.window.save_icon = PhotoImage(name='E:/pydoc/tkinter/images/save.png')
        # self.window.saveas_icon = PhotoImage(name='E:/pydoc/tkinter/images/saveas.png')
        # self.window.signout_icon = PhotoImage(name='E:/pydoc/tkinter/images/signout.png')
        pass
    # 新建项目
    def new_project(self):
        self.pdf_path = tuple()
        self.el = 0.1
        self.ael = 5
        self.phi12 = 0
        self.phi23 = 0
        self.order_n = 1
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
            initialdir='C:/Users/Administrator/Desktop') # 初始目录
        self.pdf_adr.set(self.pdf_path)

    def open_dir(self):
            # 调用askdirectory方法打开目录
        self.pdf_path = filedialog.askdirectory(title='打开目录',
            initialdir='C:/Users/Administrator/Desktop') # 初始目录
        self.pdf_adr.set(self.pdf_path)
        # print(type(self.pdf_path))
        
    def distance_error_limit(self):
        # 调用askfloat函数生成一个让用户输入浮点数的对话框
        self.el = simpledialog.askfloat("晶面距误差限", "输入晶面距误差限(Å):",
            initialvalue=self.el, minvalue=0.001, maxvalue=10)
    
    def angle_error_limit(self):
        self.ael = simpledialog.askfloat("晶面夹角误差限", "输入晶面夹角误差限(degree):",
            initialvalue=self.ael, minvalue=0.001, maxvalue=180)

    def set_phi12(self):
        self.phi12 = simpledialog.askfloat("<d1, d2>", "输入测得的d1与d2的夹角(degree):",
            initialvalue=self.phi12)

    def set_phi23(self):
        self.phi23 = simpledialog.askfloat("<d2, d3>", "输入测得的d2与d3的夹角(degree):",
            initialvalue=self.phi23)

    def set_n(self):
        self.order_n = simpledialog.askinteger("衍射级数", "输入点阵的衍射级数n:",
            initialvalue=self.order_n)

    def start_work(self):
        if self.pdf_path:
            if isinstance(self.pdf_path, str):
                os.chdir(self.pdf_path)
                start = time.time()
                for pdf_path in os.listdir():
                    example = Xyy(pdf_path, self.el, self.ael, self.d1.get(), self.d2.get(), self.d3.get(), self.phi12, self.phi23, self.order_n)
                    try:
                        example.getPdfInfo()
                        self.data.append(example.data)
                        rsl = example.fit()
                        if rsl.empty:
                            self.result.insert('end', 'No Solution in Card: {}'.format(example.title))
                        elif rsl.empty == False:
                            self.cal_rsl.append(rsl)
                            self.title.append(example.title)
                            self.result.insert('end', 'Possible Card: {}'.format(example.title))
                            self.result.insert('end', rsl)
                    except UnboundLocalError:
                        self.result.insert('end', 'Invalid Card: {}'.format(example.title))
                    except ValueError:
                        self.result.insert('end', 'No Crystal Distance in Card: {}'.format(example.title))
                    except Exception:
                        self.result.insert('end', '晶格常数识别错误\n您可以在PDF卡片{}中手动修改格式以匹配读取模式。'.format(example.title))
                end = time.time()
                self.result.insert('end', '计算结果用时：{} s\n'.format(end-start))
            elif isinstance(self.pdf_path, tuple):
                start = time.time()
                for pdf_path in self.pdf_path:
                    example = Xyy(pdf_path, self.el, self.ael, self.d1.get(), self.d2.get(), self.d3.get(), self.phi12, self.phi23, self.order_n)
                    try:
                        example.getPdfInfo()
                        self.data.append(example.data)
                        rsl = example.fit()
                        if rsl.empty:
                            self.result.insert('end', 'No Solution in Card: {}'.format(example.title))
                        elif rsl.empty == False:
                            self.cal_rsl.append(rsl)
                            self.title.append(example.title)
                            self.result.insert('end', 'Possible Card: {}'.format(example.title))
                            self.result.insert('end', rsl)
                    except UnboundLocalError:
                        self.result.insert('end', 'Invalid Card: {}'.format(example.title))
                    except ValueError:
                        self.result.insert('end', 'No Crystal Distance in Card: {}'.format(example.title))
                    except Exception:
                        self.result.insert('end', '晶格常数识别错误\n您可以在PDF卡片{}中手动修改格式以匹配读取模式。'.format(example.title))
                end = time.time()
                self.result.insert('end', '计算结果用时：{} s\n'.format(end-start))
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
            save_path = filedialog.asksaveasfilename(title='保存文件', 
            filetypes=[("office Excel", "*.xls")], # 只处理的文件类型
            initialdir='/Users/hsh/Desktop/')
            with pd.ExcelWriter(save_path+'.xls') as writer:
                for rsl, tit in zip(self.cal_rsl, self.title):
                    rsl.to_excel(writer, sheet_name=tit[:11])
        else:
            messagebox.showinfo(title='警告',message='结果为空，请重新选择源文件！')

    def select_color(self):

        self.rgb = colorchooser.askcolor(parent=self.window, title='选择线条颜色',
            color = 'black')
        self.result.insert('end', self.rgb)

    def plot_card(self):
        example = Xyy(self.pdf_path[0], self.el, self.ael, self.d1.get(), self.d2.get(), self.d3.get(), self.phi12, self.phi23)
        example.getPdfInfo()
        example.data.plot(kind = 'bar', x='2-Theta', y='I(f)', width=0.05,
            yticks=range(0,150,20), rot=60, fontsize=10, 
            label=example.title, color=self.rgb[1])
        plt.show()

    def load_para(self):
        self.unloadpara_path = filedialog.askopenfilename(title='打开单个文件',
            filetypes=[("文本文件", "*.txt")], 
            initialdir='C:/Users/Administrator/Desktop')
        try:
            with open(self.unloadpara_path) as measurement:
                    unloadpara=[float(y) for y in measurement.readline().split(',')]
            if len(unloadpara) == 5:
                self.d1.set(unloadpara[0])
                self.d2.set(unloadpara[1])
                self.d3.set(unloadpara[2])
                self.phi12 = unloadpara[3]
                self.phi23 = unloadpara[4]
            elif len(unloadpara) == 8:
                self.d1.set(unloadpara[0])
                self.d2.set(unloadpara[1])
                self.d3.set(unloadpara[2])
                self.phi12 = unloadpara[3]
                self.phi23 = unloadpara[4]
                self.el = unloadpara[5]
                self.ael = unloadpara[6]
                self.order_n = int(unloadpara[7])
            else:
                messagebox.showinfo(title='提示',message=
                '所选文件不符合格式，在第一行依次输入d1、d2、d3、phi12和phi23,用英文输入法的逗号分隔(逗号后不加空格)\n晶面距误差限、夹角误差限及衍射级数需全部输入或都不输入')
        except:
            messagebox.showinfo(title='提示',message=
            '所选文件不符合格式，在第一行依次输入d1、d2、d3、phi12和phi23,用英文输入法的逗号分隔(逗号后不加空格)\n晶面距误差限、夹角误差限及衍射级数可选')

    def save_para(self):
        self.parasaving_path = filedialog.asksaveasfilename(title='打开单个文件',
            filetypes=[("文本文件", "*.txt")], 
            initialdir='C:/Users/Administrator/Desktop')
        with open(self.parasaving_path,'a') as f:
            f.write(str(self.d1.get())+','+str(self.d2.get())+','+str(self.d3.get())+','+
            str(self.phi12)+','+str(self.phi23)+','+str(self.el)+','+str(self.ael)+','+str(self.order_n))

    def help(self):
        messagebox.showinfo(title='说明',message='主界面选择一个或多个个PDF卡片(txt格式)；文件下拉菜单中“打开文件夹”也可同时查找多个PDF卡片文件，注意此文件夹内只能包含txt格式的PDF卡片。\nPDF卡片需包含卡片号、物质名、晶体类型、晶格常数及晶面距晶面指数等信息。\n"No solution in the card"代表存在晶面距但夹角偏差大于角度误差限')

    def about(self):
        messagebox.showinfo(title='关于',message='本项目地址：https://github.com/xieshentoken/dTheta\n欢迎提出建议共同完善。\n\t\t\t作者qq:3468502700')

    def insertapp(self):
        Calcu_Special_Distance(self.window, self.pdf_path, self.rgb[1])

    # 自定义对话框类，继承Toplevel------------------------------------------------------------------------------------------
    # 创建弹窗
class Calcu_Special_Distance(Toplevel):
    # 定义构造方法
    def __init__(self, parent, pdf_path, rgb='#8080c0', title = '计算给定晶面的晶面距', modal=False):
        Toplevel.__init__(self, parent)
        self.transient(parent)
        # 设置标题
        if title: self.title(title)
        self.parent = parent
        self.pdf_path = pdf_path
        self.rgb = rgb
        # 创建对话框的主体内容
        frame = Frame(self)
        # 调用init_widgets方法来初始化对话框界面
        self.initial_focus = self.init_widgets(frame)
        frame.pack(padx=5, pady=5)
        # 根据modal选项设置是否为模式对话框
        if modal: self.grab_set()
        if not self.initial_focus:
            self.initial_focus = self
        # 为"WM_DELETE_WINDOW"协议使用self.cancel_click事件处理方法
        self.protocol("WM_DELETE_WINDOW", self.cancel_click)
        # 根据父窗口来设置对话框的位置
        self.geometry("+%d+%d" % (parent.winfo_rootx()+50,
            parent.winfo_rooty()+50))
        print( self.initial_focus)
        # 让对话框获取焦点
        self.initial_focus.focus_set()
        self.wait_window(self)

    def init_var(self):
        self.a, self.b, self.c = DoubleVar(), DoubleVar(), DoubleVar()
        self.alpha, self.beta, self.gamma = DoubleVar(), DoubleVar(), DoubleVar()
        self.h1, self.k1, self.l1 = DoubleVar(), DoubleVar(), DoubleVar()
        self.h2, self.k2, self.l2 = DoubleVar(), DoubleVar(), DoubleVar()

    # 通过该方法来创建自定义对话框的内容
    def init_widgets(self, master):
        self.init_var()
        if isinstance(self.pdf_path, tuple)and(len(self.pdf_path) == 1):
            example2 = Xyy(self.pdf_path[0])
            try:
                example2.getPdfInfo()
                self.a.set(example2.cellPara[0][0])
                self.b.set(example2.cellPara[0][1])
                self.c.set(example2.cellPara[0][2])
                self.alpha.set(example2.cellPara[1][0])
                self.beta.set(example2.cellPara[1][1])
                self.gamma.set(example2.cellPara[1][2])
            except:
                pass
        else:
            pass
        
        fm0 = Frame(master)
        fm0.pack(side=TOP, fill=BOTH, expand=YES)
        # 创建Labelframe容器
        lf1 = ttk.Labelframe(fm0, text='晶格常数',
            padding=10)
        lf1.pack(side=LEFT, fill=BOTH, expand=NO, padx=10, pady=10)
        # 创建2个容器, 输入或读取晶格常数==================================================================================
        fm1 = Frame(lf1)
        fm1.pack(side=TOP, fill=BOTH, expand=NO)
        for lab, val in zip(['a:', 'b:', 'c:'], [self.a, self.b, self.c]):
            Label(fm1, font=('StSong', 15, 'bold'), text=lab).pack(side=LEFT, padx=15, pady=10)
            ttk.Entry(fm1, textvariable=val,
                width=3,
                font=('StSong', 15, 'bold'),
                foreground=self.rgb).pack(side=LEFT, ipadx=5, ipady=5, padx=5, pady=10)

        fm2 = Frame(lf1)
        fm2.pack(side=TOP, fill=BOTH, expand=NO)
        for lab, val in zip(['α:', 'β:', 'γ:'], [self.alpha, self.beta, self.gamma]):
            Label(fm2, font=('StSong', 15, 'bold'), text=lab).pack(side=LEFT, padx=15, pady=10)
            ttk.Entry(fm2, textvariable=val,
                width=3,
                font=('StSong', 15, 'bold'),
                foreground=self.rgb).pack(side=LEFT, ipadx=5, ipady=5, padx=5, pady=10)
        # 创建指定晶面的密勒指数输入框============================================================================================
        lf2 = ttk.Labelframe(fm0, text='密勒指数',
            padding=10)
        lf2.pack(side=LEFT, fill=BOTH, expand=NO, padx=10, pady=10)
        fm3 = Frame(lf2)
        fm3.pack(side=TOP, fill=BOTH, expand=NO)
        for lab, val in zip(['h1:', 'k1:', 'l1:'], [self.h1, self.k1, self.l1]):
            Label(fm3, font=('StSong', 15, 'bold'), text=lab).pack(side=LEFT, padx=15, pady=10)
            ttk.Entry(fm3, textvariable=val,
                width=3,
                font=('StSong', 15, 'bold'),
                foreground=self.rgb).pack(side=LEFT, ipadx=5, ipady=5, padx=5, pady=10)
        fm4 = Frame(lf2)
        fm4.pack(side=TOP, fill=BOTH, expand=NO)
        for lab, val in zip(['h2:', 'k2:', 'l2:'], [self.h2, self.k2, self.l2]):
            Label(fm4, font=('StSong', 15, 'bold'), text=lab).pack(side=LEFT, padx=15, pady=10)
            ttk.Entry(fm4, textvariable=val,
                width=3,
                font=('StSong', 15, 'bold'),
                foreground=self.rgb).pack(side=LEFT, ipadx=5, ipady=5, padx=5, pady=10)
        # 创建按钮================================================================================================================
        # 创建第二个容器
        fm00 = Frame(master)
        fm00.pack(side=TOP, fill=BOTH, expand=YES)
        # 创建第二个容器的子容器----------------------------
        fm2_0 = Frame(fm00)
        fm2_0.pack(side=LEFT, fill=BOTH, expand=YES)
        self.result = Text(fm2_0, 
            width=50,
            height=10,
            font=('StSong', 14),
            foreground=self.rgb)
        self.result.pack(side=LEFT, fill=BOTH, expand=YES)
        # 创建Scrollbar组件，设置该组件与result的纵向滚动关联
        scroll_y = Scrollbar(fm2_0, command=self.result.yview)
        scroll_y.pack(side=RIGHT, fill=Y, expand=YES)
        # 设置result的纵向滚动影响scroll滚动条
        self.result.configure(yscrollcommand=scroll_y.set)
        # 创建第二个容器的子容器----------------------------
        fm2_1 = Frame(fm00)
        fm2_1.pack(side=LEFT, fill=BOTH, expand=YES)
        d_button = Button(fm2_1, text = 'd(h1k1l1)', 
            bd=3, width = 10, height = 1, 
            command = self.distance, 
            activebackground='black', activeforeground='white')
        d_button.pack(side=TOP, ipadx=1, ipady=5, pady=10)
        phi_button = Button(fm2_1, text = 'Angle', 
            bd=3, width = 10, height = 1, 
            command = self.p1_p2_angle, 
            activebackground='black', activeforeground='white')
        phi_button.pack(side=TOP, ipadx=1, ipady=5, pady=10)
        new_button = Button(fm2_1, text = 'Clear', 
            bd=3, width = 10, height = 1, 
            command = self.clear, 
            activebackground='black', activeforeground='white')
        new_button.pack(side=TOP, ipadx=1, ipady=5, pady=10)

    def clear(self):
        self.result.delete(0.0, 'end')

    def hihj(self, p1, p2):
        abc = np.array([self.a.get(), self.b.get(), self.c.get()])
        abg = np.array([self.alpha.get()*np.pi/180, self.beta.get()*np.pi/180, self.gamma.get()*np.pi/180])
        return (p1*p2).dot((np.sin(abg)**2)/(abc**2)) + (p1[1]*p2[2]+p1[2]*p2[1])*(np.cos(abg[1])*np.cos(abg[2])-np.cos(abg[0]))/(abc[1]*abc[2]) + (p1[2]*p2[0]+p1[0]*p2[2])*(np.cos(abg[2])*np.cos(abg[0])-np.cos(abg[1]))/(abc[2]*abc[0]) + (p1[0]*p2[1]+p1[1]*p2[0])*(np.cos(abg[0])*np.cos(abg[1])-np.cos(abg[2]))/(abc[0]*abc[1])

    def distance(self):
        self.abc = np.array([self.a.get(), self.b.get(), self.c.get()])
        self.abg = np.array([self.alpha.get()*np.pi/180, self.beta.get()*np.pi/180, self.gamma.get()*np.pi/180])
        self.p1 = np.array([self.h1.get(), self.k1.get(), self.l1.get()])
        try:
            vol = (1 - np.cos(self.abg[0])**2 - np.cos(self.abg[1])**2 - np.cos(self.abg[2])**2 + 2*np.cos(self.abg[0])*np.cos(self.abg[1])*np.cos(self.abg[2]))**0.5
            cal_distance = vol/(self.hihj(self.p1, self.p1))**0.5
            self.result.insert('end', '晶面({},{},{})的晶面距为: {} Å\n'.format(int(self.h1.get()), int(self.k1.get()), int(self.l1.get()), str(cal_distance)))
            self.result.insert('end', ' {}   40.0   23.0  {}  {}   {}        26.586  13.293  0.1493  1.8756\n'.format(
                str(float(int(cal_distance*1000)/1000)), int(self.h1.get()), int(self.k1.get()), int(self.l1.get())))
        except:
            messagebox.showinfo(title='警告',message='请重新输入相关参数')

    def p1_p2_angle(self):
        self.abc = np.array([self.a.get(), self.b.get(), self.c.get()])
        self.abg = np.array([self.alpha.get()*np.pi/180, self.beta.get()*np.pi/180, self.gamma.get()*np.pi/180])
        self.p1 = np.array([self.h1.get(), self.k1.get(), self.l1.get()])
        self.p2 = np.array([self.h2.get(), self.k2.get(), self.l2.get()])
        try:
            h11 = self.hihj(self.p1, self.p1)
            h22 = self.hihj(self.p2, self.p2)
            h12 = self.hihj(self.p1, self.p2)
            cal_phi12 = np.arccos(h12/(h11*h22)**0.5)*180./np.pi
            self.result.insert('end', '({},{},{})({},{},{})的晶面夹角为: {}°\n'.format(int(self.h1.get()), int(self.k1.get()), int(self.l1.get()), int(self.h2.get()), int(self.k2.get()), int(self.l2.get()), str(cal_phi12)))
        except:
            messagebox.showinfo(title='警告',message='请重新输入相关参数')

    def cancel_click(self, event=None):
        # print('取消')
        # 将焦点返回给父窗口
        self.parent.focus_set()
        # 销毁自己
        self.destroy()
