import pandas as pd

import numpy as np
#from PublicFA import ReadFile, ReadRunoff, ReadRunoff1, CaluFlow, paipin, chazhi
import math, os
def ReadFile():
    str1 = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    zv = np.loadtxt((str1 + '\\data\\z_v.dat'), skiprows=1, delimiter=',')
    gzz = zv[:, 0]
    gvv = zv[:, 1]
    mmg = len(gzz)
    zq = np.loadtxt((str1 + '\\data\\z_q.dat'), skiprows=1, delimiter=',')
    gz1 = zq[:, 0]
    gqq = zq[:, 1]
    nng = len(gz1)
    return (gzz, gvv, mmg, gz1, gqq, nng)

def ReadRunoff():
    #b年平均径流 a 1-12的径流 q0多年平均径流 m年数 i0 1950第一行
    str1 = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    f = open(str1 + '\\data\\data.dat', 'r')
    content = f.readline()
    content = content.strip('\n')
    content_list = content.split('   ')
    m = int(content_list[0])
    i0 = int(content_list[1])
    ii0 = int(content_list[2])
    data = np.loadtxt((str1 + '\\data\\data.dat'), skiprows=1, delimiter='\t')
    aa = data[:, 0]
    aa.astype(int)
    b = data[:, 13]
    a = data[:, 1:13]
    q0 = np.mean(b)
    #print(b, q0)
    return (m, i0, ii0, a, b, q0)

def CaluFlow(m, a):
    for i in range(0, m):
        for j in range(0, 12):
            if j == 1:
                a[(i, j)] = a[(i, j)] - 22
            else:
                if 1 < j < 6:
                    a[(i, j)] = a[(i, j)] - 45
                else:
                    a[(i, j)] = a[(i, j)] - 10

    return a


def paipin(n, x):
    index = np.argsort(-x)
    p = np.zeros(n + 1)
    for i in range(1, n + 1):
        p[index[i - 1]] = i / (n + 1) * 100

    return p

def chazhi(a, b, m, x):
    xy = 0
    if (x - a[0]) * (x - a[m - 1]) > 0:
        if x < a[0]:
            xy = b[0]
        if x > a[m - 1]:
            xy = b[m - 1]
        return xy
    for i in range(0, m):
        j = 0
        if (x - a[i]) * (x - a[i + 1]) <= 0:
            j = i
            if a[j + 1] - a[j] != 0:
                xy = b[j] + (x - a[j]) / (a[j + 1] - a[j]) * (b[j + 1] - b[j])
            else:
                xy = b[j]
            return xy



def tiaojieliuliang(zz):
    # gzz 水位 gvv 对应容积 mmg z_v的行数
    # gz1退水水位流量关系的 相应水位 gqq下游相应流量 nng z_q行数目
    # b年平均径流 a 1-12的径流 q0多年平均径流
    # zz正常高水位 zzs死水位
    gzz, gvv, mmg, gz1, gqq, nng = ReadFile()
    m, i0, ii0, a, b, q0 = ReadRunoff()
    a = CaluFlow(m, a)
    zz = float(zz)
    if zz <= 0:
        exit()
    QQa = 0.8 * q0
    vv1 = chazhi(gzz, gvv, mmg, zz)
    condition = True
    while condition:
        zz1 = chazhi(gqq, gz1, nng, QQa)
        zzs = max(82, zz - (zz - zz1) * 0.35) #计算死水位，淤积水位小于82m
        vv2 = chazhi(gzz, gvv, mmg, zzs)
        v = vv1 - vv2
        w = [0, 0]
        k = 1
        for i in range(1, m + 1):
            for j in range(1, 13):
                wtemp = w[k] + a[(i - 1, j - 1)] - q0
                w.append(wtemp)
                k = k + 1

        kk = 1
        iis = 1
        Q = np.zeros(32)
        ig = np.zeros(32)
        iss = np.zeros(32)
        iee = np.zeros(32)
        while kk <= m:
            ie = iis + 9
            if ie > 12 * m + 1:
                ie = 12 * m + 1
            F = w[iis]
            for h in range(iis, ie + 1):
                if w[h] > F:
                    F = w[h]
                    iu = h   #茶几曲线最大处对应序号

            fi = w[iu]
            iiu = iu + 9
            if iiu > 12 * m + 1:
                iiu = 12 * m + 1
            for s in range(iu, iiu + 1):
                if w[s] < fi:
                    fi = w[s]
                    IL = s  #最小

            ii1 = IL
            il1 = 1
            il2 = 1
            while il1 != IL or il2 != iu:
                il1 = IL
                il2 = iu
                for e in range(iu, IL + 1):
                    d = w[iu] + (w[IL] + v - w[iu]) / float(IL - iu) * (e - iu)  #v 加值 斜率计算 检验不能交叉
                    if d > w[e] + v:
                        IL = e

                for f in range(iu, IL + 1):
                    d = w[iu] + (w[IL] + v - w[iu]) / float(IL - iu) * (f - iu) #供水起初 期末  水量平衡验证
                    if d < w[f]:
                        iu = f

            Q[kk] = (w[IL] + v - w[iu]) / float(IL - iu) + q0
            iss[kk] = iu #供水期初
            iee[kk] = IL#末
            ig[kk] = IL - iu
            kk = kk + 1
            iis = ii1

        p = paipin(m, Q)
        ax = float(100)
        for t in range(1, m + 1):
            if abs(p[t] - 87.5) < ax:
                ax = abs(p[t] - 87.5)
                jf = t

        condition = abs(Q[jf] - QQa) > 1 # 误差小于1时候停止
        if condition:
            QQa = Q[jf]

    str1 = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    f = open(str1 + '\\data\\no.dat', 'w')
    for i in range(m):
        f.write(f"{int(iss[i + 1] - 1)}   {int(iee[i + 1] - 1)}   {Q[i + 1]}\n")

    f.close()
    vs = chazhi(gzz, gvv, mmg, zzs)
    dd = np.zeros(32)
    nianfen = np.zeros(32)
    nianfen = nianfen.astype(int)
    qichu = np.zeros(32)
    qichu = qichu.astype(int)
    qimo = np.zeros(32)
    qimo = qimo.astype(int)
    gongshuiqi = np.zeros(32)
    gongshuiqi = gongshuiqi.astype(int)
    for i in range(1, m + 1):
        dd[i] = w[int(iee[i])] - w[int(iss[i])] + q0 * (int(iee[i]) - int(iss[i]))
        i1 = int(iss[i]) - 12 * (i - 1) + ii0 - 1
        if i1 > 12:
            i1 = i1 - 12
        i2 = int(iee[i]) - 12 * (i - 1) + ii0 - 2
        if i2 > 12:
            i2 = i2 - 12
        nianfen[i] = i + i0
        qichu[i] = i1
        qimo[i] = i2
        gongshuiqi[i] = ig[i]
    for i in [nianfen, qichu, qimo, gongshuiqi, dd, v, Q, p]:
        i = np.array(i)
    # 创建DataFrame
    outputlen = len(nianfen)
    data = {
        "年份": nianfen,
        "供水期初": qichu,
        "供水期末": qimo,
        "供水期": gongshuiqi,
        "来水量": dd,
        "兴利库容": v,
        "调节流量": Q,
        "频率": p,
        "死水位": [np.nan] + [zzs] + [np.nan] * (outputlen - 2),
        "死库容": [np.nan] + [v] + [np.nan] * (outputlen - 2)
    }
    df = pd.DataFrame(data)
    df = df.drop(index=0)
    return (df)
#nianfen 年份 qichu供水期初 qimo供水期末 gongshuiqi 供水期
# dd来水量 v 兴利库容 Q调节流量 p频率 zzs死水位 vs死库容
#(zzs, vs, nianfen, qichu, qimo, gongshuiqi, dd, v, Q, p)=tiaojieliuliang(120)
#print(type(vs))
#
# import pandas as pd
# import numpy as np
# import os

#
# for i in [nianfen, qichu, qimo, gongshuiqi, dd, v, Q, p]:
#     i=np.array(i)
# # 创建DataFrame
# outputlen=len(nianfen)
# data = {
#     "年份": nianfen,
#     "供水期初": qichu,
#     "供水期末": qimo,
#     "供水期": gongshuiqi,
#     "来水量": dd,
#     "兴利库容": v,
#     "调节流量": Q,
#     "频率": p,
#     "死水位":[np.nan]+[zzs]+[np.nan]*(outputlen-2),
#     "死库容":[np.nan]+[v]+[np.nan]*(outputlen-2)
# }
# df = pd.DataFrame(data)
# df=df.drop(index=0)
#
# # 保存到Excel
# file_path = os.path.join(os.getcwd(), '调节流量计算结果.xlsx')
# df.to_excel(file_path, index=False)
#
# print(f"数据已保存到 {file_path}")
# #
#

