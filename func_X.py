import re
from itertools import permutations

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


class Xyy():
    def __init__(self, path, el=None, ael = None, d1=None, d2=None, d3=None, phi12=None, phi23=None):
        self.path = path
        self.el = el
        self.ael = ael
        self.d1 = d1
        self.d2 = d2
        self.d3 = d3
        self.phi12 = phi12
        self.phi23 = phi23
    
        self.text = []
        self.d_A_Index = 0
        self.title = ''
        self.cryForm = ''
        self.cellPara = np.zeros(6) # 晶胞参数 np.array([[a,b,c],[alpha,beta,gamma]])
        self.data = pd.DataFrame(columns=['d(A)','h','k','l']) # 包含晶面指数及晶面距等信息的pd.dataframe
        self.dA_hkl = pd.DataFrame(columns=['d(A)','h','k','l']) # 去除异常值后的data
        
    def getPdfInfo(self):
        i = 0
        d_A_Regex = re.compile(r'd\(.\)')
        with open(self.path) as jcpds:# 根据路径读取PDF卡片，保存在text(list)中
            for line in jcpds:
                match = d_A_Regex.search(line)
                if match:
                    self.d_A_Index = i
                self.text.append(line)
                i += 1
        self.title = self.text[0].split()[0] + ' ' + self.text[2]# 记录PDF卡片号码及物质化学式
        
        # 读取相应晶体类型cryForm及晶胞参数
        cryFormRegex = re.compile(r'Cubic|Tetragonal|Orthorhombic|Monoclinic|Triclinic|Hexagonal|Trigonal|Rhombohedral')
        cellParaRegex = re.compile(r'((\d)+\.(\d)+)')
        paraIndex = 0
        for i in self.text:
            if cryFormRegex.search(i):
                paraIndex = self.text.index(i) + 1
                cryFormSearch = cryFormRegex.search(i)
                self.cryForm = cryFormSearch.group()
                break
        cellParaSearch = cellParaRegex.findall(self.text[paraIndex])
        cellPara0 = [ cellParaSearch[i][0] for i in range(0, len(cellParaSearch)) ]
        
        if self.cryForm == 'Cubic':
            a = b = c = float(cellPara0[0])
            alpha = beta = gamma = 90.0
        elif self.cryForm == 'Tetragonal':
            a = b = float(cellPara0[0])
            c = float(cellPara0[1])
            alpha = beta = gamma = 90.0
        elif self.cryForm == 'Orthorhombic':
            a = float(cellPara0[0])
            b = float(cellPara0[1])
            c = float(cellPara0[2])
            alpha = beta = gamma = 90.0
        elif self.cryForm == 'Monoclinic':
            a = float(cellPara0[0])
            b = float(cellPara0[1])
            c = float(cellPara0[2])
            alpha = 90.0
            if (len(cellPara0) == 4)or(len(cellPara0) == 5):
                beta = float(cellPara0[3])
            elif len(cellPara0) == 6:
                beta = float(cellPara0[4])
            gamma = 90.0
        elif self.cryForm == 'Triclinic':
            a = float(cellPara0[0])
            b = float(cellPara0[1])
            c = float(cellPara0[2])
            alpha = float(cellPara0[3])
            beta = float(cellPara0[4])
            gamma = float(cellPara0[5])
        elif self.cryForm == 'Hexagonal':
            a = b = float(cellPara0[0])
            c = float(cellPara0[1])
            alpha = 90.0
            beta = 90.0
            gamma = 120.0
        elif (self.cryForm == 'Trigonal') or (self.cryForm =='Rhombohedral'):
            a = float(cellPara0[0])
            b = float(cellPara0[0])
            c = float(cellPara0[1])
            alpha = 90.0
            beta = 90.0
            gamma = 120.0
        else:
            print('Invalid PDF Card: {}'.format(self.title))
        self.cellPara = np.array([a, b ,c, alpha, beta, gamma]).reshape(2,3)

        # 获取晶面指数及晶面距、衍射强度等信息，以pandas.DataFrame形式保存
        columns = self.text[self.d_A_Index].split()
        if len(self.text[self.d_A_Index].split()) - len(self.text[self.d_A_Index+1].split()) >= 1:
            columns.remove('n^2')

        for i in columns:
            if i == 'l)':
                columns[columns.index(i)] = i.split(')')[0]
        if '(' in columns:
            columns.remove('(')
        if 'd(?)' in columns:
            columns.insert(columns.index('d(?)'), 'd(A)')
            columns.remove('d(?)')

        rest = self.text[self.d_A_Index+1:]
        participle = []
        for i in rest:
            row = i.split()
            if '(' in row:
                row.remove('(')
                participle.append(row)
            else:
                participle.append(row)
        for i in participle:
            for j in i:
                if j != j.split(')')[0]:
                    i[i.index(j)] = j.split(')')[0]
                else:
                    if '(-' in j:
                        i[i.index(j)] = j.split('(')[1]

        preData = pd.DataFrame(participle, columns = columns)
        preData = preData.dropna()# 去除空值
        self.data = preData.astype('float')
        dA = self.data['d(A)']
        h = self.data[['h']]
        k = self.data[['k']]
        l = self.data[['l']]
        self.dA_hkl = pd.concat([h,k,l], axis = 1)
        self.dA_hkl.index = dA

    def fit(self):
        pod1 = self.dA_hkl.loc[[x for x in self.data['d(A)'] if abs(x-self.d1)<=self.el]]
        pod2 = self.dA_hkl.loc[[x for x in self.data['d(A)'] if abs(x-self.d2)<=self.el]]
        pod3 = self.dA_hkl.loc[[x for x in self.data['d(A)'] if abs(x-self.d3)<=self.el]]
        # dA = self.data['d(A)']
        if (pod1.values.tolist()==[])or(pod2.values.tolist()==[])or(pod3.values.tolist()==[]):
            print('No solution in the card--{}'.format(self.title))
            raise ValueError
        else:
            pass


        # 生成三个包含同一组晶面的dataframe的list
        expod1, expod2, expod3 = [], [], []
        # 立方晶系48，六方晶系24，四方晶系16，三方晶系12，正交晶系8，单斜晶系4，三斜晶系2

        # 立方晶系指数位置符号均可独立改变，共48种可能变换
        if self.cryForm == 'Cubic':
            h = pod1[['h']]
            k = pod1[['k']]
            l = pod1[['l']]
            sel = [[p*h, q*k, m*l] for p in [1, -1] for q in [1,-1] for m in [1,-1]]
            for x in sel:
                ss = [p for p in permutations(x)]
                for y in ss:
                    expod1.append(pd.concat(y, axis=1))
            h = pod2[['h']]
            k = pod2[['k']]
            l = pod2[['l']]
            sel = [[p*h, q*k, m*l] for p in [1, -1] for q in [1,-1] for m in [1,-1]]
            for x in sel:
                ss = [p for p in permutations(x)]
                for y in ss:
                    expod2.append(pd.concat(y, axis=1))
            h = pod3[['h']]
            k = pod3[['k']]
            l = pod3[['l']]
            sel = [[p*h, q*k, m*l] for p in [1, -1] for q in [1,-1] for m in [1,-1]]
            for x in sel:
                ss = [p for p in permutations(x)]
                for y in ss:
                    expod3.append(pd.concat(y, axis=1))
        # 六方晶系i=-(h+k)，可以从四指数中h、k、i任取两个作为三指数的h、k，三指数中h、k位置可互换,符号需一起变，l可任意改变符号，故共24种可能变换
        elif self.cryForm == 'Hexagonal':
            _h = pod1[['h']]
            _k = pod1[['k']]
            _i = -_h-_k
            l = pod1[['l']]
            for i in permutations([_h, _k, _i]):
                h, k = i[0], i[1]
                sel = [[p*h, p*k, m*l] for p in [1, -1] for m in [1, -1]]
                for x in sel:
                    ss = [p for p in permutations(x[:2])]
                    for y in ss:
                        hk = list(y)
                        hk.extend([x[-1]])
                        expod1.append(pd.concat(hk, axis=1))
            _h = pod2[['h']]
            _k = pod2[['k']]
            _i = -_h-_k
            l = pod2[['l']]
            for i in permutations([_h, _k, _i]):
                h, k = i[0], i[1]
                sel = [[p*h, p*k, m*l] for p in [1, -1] for m in [1, -1]]
                for x in sel:
                    ss = [p for p in permutations(x[:2])]
                    for y in ss:
                        hk = list(y)
                        hk.extend([x[-1]])
                        expod2.append(pd.concat(hk, axis=1))
            _h = pod3[['h']]
            _k = pod3[['k']]
            _i = -_h-_k
            l = pod3[['l']]
            for i in permutations([_h, _k, _i]):
                h, k = i[0], i[1]
                sel = [[p*h, p*k, m*l] for p in [1, -1] for m in [1, -1]]
                for x in sel:
                    ss = [p for p in permutations(x[:2])]
                    for y in ss:
                        hk = list(y)
                        hk.extend([x[-1]])
                        expod3.append(pd.concat(hk, axis=1))
        # 四方晶系h、k指数位置可互换，符号可以任意改变，共16种可能变换
        elif self.cryForm == 'Tetragonal':
            h = pod1[['h']]
            k = pod1[['k']]
            l = pod1[['l']]
            sel = [[p*h, q*k, m*l] for p in [1, -1] for q in [1,-1] for m in [1,-1]]
            for x in sel:
                ss = [p for p in permutations(x[:2])]
                for y in ss:
                    hk = list(y)
                    hk.extend([x[-1]])
                    expod1.append(pd.concat(hk, axis=1))
            h = pod2[['h']]
            k = pod2[['k']]
            l = pod2[['l']]
            sel = [[p*h, q*k, m*l] for p in [1, -1] for q in [1,-1] for m in [1,-1]]
            for x in sel:
                ss = [p for p in permutations(x[:2])]
                for y in ss:
                    hk = list(y)
                    hk.extend([x[-1]])
                    expod2.append(pd.concat(hk, axis=1))
            h = pod3[['h']]
            k = pod3[['k']]
            l = pod3[['l']]
            sel = [[p*h, q*k, m*l] for p in [1, -1] for q in [1,-1] for m in [1,-1]]
            for x in sel:
                ss = [p for p in permutations(x[:2])]
                for y in ss:
                    hk = list(y)
                    hk.extend([x[-1]])
                    expod3.append(pd.concat(hk, axis=1))
        # 正交晶系指数符号可以独立变化，位置不能变， 共8种可能变换
        elif self.cryForm == 'Orthorhombic':
            h = pod1[['h']]
            k = pod1[['k']]
            l = pod1[['l']]
            sel = [[p*h, q*k, m*l] for p in [1, -1] for q in [1,-1] for m in [1,-1]]
            for x in sel:
                expod1.append(pd.concat(x, axis=1))
            h = pod2[['h']]
            k = pod2[['k']]
            l = pod2[['l']]
            sel = [[p*h, q*k, m*l] for p in [1, -1] for q in [1,-1] for m in [1,-1]]
            for x in sel:
                expod2.append(pd.concat(x, axis=1))
            h = pod3[['h']]
            k = pod3[['k']]
            l = pod3[['l']]
            sel = [[p*h, q*k, m*l] for p in [1, -1] for q in [1,-1] for m in [1,-1]]
            for x in sel:
                expod3.append(pd.concat(x, axis=1))
        # 三方（菱形）晶系各指数位置可变，符号必须一起变，共12 种可能变换
        elif (self.cryForm == 'Trigonal')or(self.cryForm == 'Rhombohedral'):
            h = pod1[['h']]
            k = pod1[['k']]
            l = pod1[['l']]
            sel = [[p*h, p*k, p*l] for p in [1, -1]]
            for x in sel:
                ss = [p for p in permutations(x)]
                for y in ss:
                    expod1.append(pd.concat(y, axis=1))
            h = pod2[['h']]
            k = pod2[['k']]
            l = pod2[['l']]
            sel = [[p*h, p*k, p*l] for p in [1, -1]]
            for x in sel:
                ss = [p for p in permutations(x)]
                for y in ss:
                    expod2.append(pd.concat(y, axis=1))
            h = pod3[['h']]
            k = pod3[['k']]
            l = pod3[['l']]
            sel = [[p*h, p*k, p*l] for p in [1, -1]]
            for x in sel:
                ss = [p for p in permutations(x)]
                for y in ss:
                    expod3.append(pd.concat(y, axis=1))
        # 单斜晶系指数的位置不能变，k的符号可以单独改变，共4种可能变换
        elif self.cryForm == 'Monoclinic':
            h = pod1[['h']]
            k = pod1[['k']]
            l = pod1[['l']]
            sel = [[p*h, p*k, m*l] for p in [1, -1] for m in [1,-1]]
            for x in sel:
                expod1.append(pd.concat(x, axis=1))
            h = pod2[['h']]
            k = pod2[['k']]
            l = pod2[['l']]
            sel = [[p*h, p*k, m*l] for p in [1, -1] for m in [1,-1]]
            for x in sel:
                expod2.append(pd.concat(x, axis=1))
            h = pod3[['h']]
            k = pod3[['k']]
            l = pod3[['l']]
            sel = [[p*h, p*k, m*l] for p in [1, -1] for m in [1,-1]]
            for x in sel:
                expod3.append(pd.concat(x, axis=1))
        # 三斜晶系指数的位置不能变，符号一起变，共2种可能变换
        elif self.cryForm == 'Triclinic':
            h = pod1[['h']]
            k = pod1[['k']]
            l = pod1[['l']]
            sel = [[p*h, p*k, p*l] for p in [1, -1]]
            for x in sel:
                expod1.append(pd.concat(x, axis=1))
            h = pod2[['h']]
            k = pod2[['k']]
            l = pod2[['l']]
            sel = [[p*h, p*k, p*l] for p in [1, -1]]
            for x in sel:
                expod2.append(pd.concat(x, axis=1))
            h = pod3[['h']]
            k = pod3[['k']]
            l = pod3[['l']]
            sel = [[p*h, p*k, p*l] for p in [1, -1]]
            for x in sel:
                expod3.append(pd.concat(x, axis=1))

        # 筛选出满足矢量加法条件的晶面
        lis_extpod1, lis_extpod2, lis_extpod3 = [], [], []
        lis_expod1, lis_expod2, lis_expod3 = [], [], []

        for p in expod1:
            lis_extpod1.extend(p.values.tolist())
        for q in expod2:
            lis_extpod2.extend(q.values.tolist())
        for m in expod3:
            lis_extpod3.extend(m.values.tolist())
        for p in lis_extpod1:
            if p not in lis_expod1:
                lis_expod1.append(p)
        for q in lis_extpod2:
            if q not in lis_expod2:
                lis_expod2.append(q)
        for m in lis_extpod3:
            if m not in lis_expod3:
                lis_expod3.append(m)
        
        rs=[]
        psb_rslt = pd.DataFrame()
        for q in lis_expod2:
            for p in lis_expod1:
                for m in lis_expod3:
                    if ((np.array(p) + np.array(m)) == np.array(q)).all():
                        h11 = self.hihj(np.array(p), np.array(p))
                        h22 = self.hihj(np.array(q), np.array(q))
                        h33 = self.hihj(np.array(m), np.array(m))
                        h12 = self.hihj(np.array(p), np.array(q))
                        h23 = self.hihj(np.array(q), np.array(m))
                        cal_d1 = self.cal_d(np.array(p))
                        cal_d2 = self.cal_d(np.array(q))
                        cal_d3 = self.cal_d(np.array(m))
                        cal_phi12 = np.arccos(h12/(h11*h22)**0.5)*180./np.pi
                        cal_phi23 = np.arccos(h23/(h22*h33)**0.5)*180./np.pi
                        if (abs(cal_phi12 - self.phi12) <= self.ael)and(abs(cal_phi23 - self.phi23) <= self.ael):
                            rs.append([p,q,m,cal_phi12,cal_phi23,cal_d1,cal_d2,cal_d3]) 

        if rs == []:
            print('No solution in Card-*-: {}'.format(self.title))

        else:
            psb_rslt = pd.DataFrame(rs, columns = ['posiible d1', 'posiible d2', 'posiible d3', 'cal_phi<d1,d2>', 'cal_phi<d2,d3>', 'cal_d1', 'cal_d2', 'cal_d3'])


        return psb_rslt
# H函数
# p1,p2为ndarray([h0,k0,l0])

    def hihj(self, p1, p2):
        abc = self.cellPara[0]
        abg = self.cellPara[1]*np.pi/180
        return (p1*p2).dot((np.sin(abg)**2)/(abc**2)) + (p1[1]*p2[2]+p1[2]*p2[1])*(np.cos(abg[1])*np.cos(abg[2])-np.cos(abg[0]))/(abc[1]*abc[2]) + (p1[2]*p2[0]+p1[0]*p2[2])*(np.cos(abg[2])*np.cos(abg[0])-np.cos(abg[1]))/(abc[2]*abc[0]) + (p1[0]*p2[1]+p1[1]*p2[0])*(np.cos(abg[0])*np.cos(abg[1])-np.cos(abg[2]))/(abc[0]*abc[1])

# 计算晶面距的函数

    def cal_d(self, p):
        ang = self.cellPara[1]*np.pi/180
        vol = (1 - np.cos(ang[0])**2 - np.cos(ang[1])**2 - np.cos(ang[2])**2 + 2*np.cos(ang[0])*np.cos(ang[1])*np.cos(ang[2]))**0.5
        cal_distance = vol/(self.hihj(p, p))**0.5
        return cal_distance
