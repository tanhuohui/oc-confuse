# -*- coding: utf-8 -*-
#   OC代码混淆器
#       by charon
import os
import re
import hashlib
import sys
import string,random
from descr import Descr
from compiler.ast import flatten
#定义第三方SDK列表
SDK_LIST = ["MJRefresh","Masonry","AFNet","MJExtension","HUPhotoBrowser","MBProgressHUD","Pods"]
#定义系统的主要函数列表 必须填.m
SYSTEM_LIST = ['main.m']
#定义密钥的长度20
KEY_BIT = 20
#需要加的盐
SALT_KEY = ''

path = "/Users/86itsec.com/Desktop/qqq副本"

#
# path = "/Users/hya/Desktop/安全猎手副本"

#过滤.m .h .pch文件
#在同级目录遍历,查找到所有的文件
#传入参数:项目绝对路径
def hmpchFilter(path):
    mergelist = []
    for list in os.walk(path):
     #过滤掉为空的列表
        if list[2] != []:
        #组合列表 拼凑出绝对路径
            for absfile in list[2]:
                mergelist.append(list[0] + '/' + absfile)
    filelist = []
    for mstr in mergelist:
    #过滤查找项目中.m和.h和.pch文件
        if mstr.endswith('.m') or mstr.endswith('.h') or mstr.endswith('.pch'):
            filelist.append(mstr)
    return filelist

#过滤第三方SDK文件 :
#参数 1.源列表 2.需要过滤的SDK列表
def sdkFilter(list,unlist):
    result = []
    #下标
    idxlist = len(list) - 1
    print idxlist
    while idxlist >= 0:
        #定义找SDK 的标志位
        idxflag = 0
        for sdks in unlist:
            if sdks in list[idxlist]:
                idxflag = 1#包含了SDK flag 置1
                break
        if idxflag == 0:
            result.append(list[idxlist])
        idxlist = idxlist - 1
    return result

#过滤系统的必须类名方法
#不对这些文件进行改名(注意:但对他们内容仍然进行加密)
#参数:1未过滤字典 2:需要过滤的系统文件列表
def sysFilter(list,unlist):
    result = []
    idxlist = len(list) - 1
    while idxlist >= 0:
        # 定义找SDK 的标志位
        idxflag = 0
        for sdks in unlist:
            if sdks in list[idxlist]:
                idxflag = 1  # 包含了SDK flag 置1
                break
        if idxflag == 0:
            result.append(list[idxlist])
        idxlist = idxlist - 1
    return result

#获取到所有的类名,并且进行排重过滤 生成对应字典
#传入参数: 列表(已过滤)
#返回值:  字典
def keyDictCreate(list):
    all_cls_list = []
    #首先获取项目中所有的类名
    for str in list:
        result = re.findall(r'[^\/]+[^.h|^.m|^.pch]',str)[-1]
        all_cls_list.append(result)

    #然后去重
    new_cls_list = {}.fromkeys(all_cls_list).keys()
    print new_cls_list

    #生成20位的随机数字母用作密钥
    key_list = []
    for i in range(len(new_cls_list)):
        key_list.append(sec_key_create())
    #合并密钥和类名为一个字典
    key_dict = dict(zip(new_cls_list,key_list))
    return key_dict


#随机数密钥生成器
#返回值 : n位的随机数字符串(大小写)
def sec_key_create():
    sec_key = []
    #随机数种子
    seed = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    for i in range(KEY_BIT):
        sec_key.append(random.choice(seed))
    salt = SALT_KEY.join(sec_key)
    return salt

#开始逐个进行替换操作
#参数1:列表(需要加密文件的绝对路径) 参数2:使用的加密字典
#返回值 : 成功与否标志
#替换操作
def doReplaceKeys(file_path_list, keydict):
    # 对文件名列表进行遍历
    for file_path in file_path_list:
            # 读取文件内容
            f_context = readContextFromFile(file_path)
            # 使用正则进行替换通篇文章
            for k, v in keydict.iteritems():
                replace_reg = re.compile(r'\b(%s)\b' % k)
                f_context = replace_reg.sub(v, f_context)
            #写入信息到文件中
            writeContextToFile(f_context, file_path)
    return True

#内容写入文件操作
def writeContextToFile(context,filepath):
    try:
        fwrite = open(filepath,'w')
        fwrite.write(context)
    except Exception,e:
        print "ERROR(-1):file is not exist and write failed!",str(e)
    fwrite.close()

#从文件读取内容操作
#返回值:文件内容串
def readContextFromFile(filepath):
    try:
        fread = open(filepath, 'r')
    except Exception, e:
        print "ERROR(-2):read the source code error!", str(e)
    tmpstr = fread.read()
    fread.close()
    return tmpstr

#未完成
#!!!!
# def doReplaceAttributes(file_path_list,keydict):
#     #对文件名列表进行遍历
#     for file_path in file_path_list:
#         #读取文件内容
#         f_context = readContextFromFile(file_path)
        #使用正则通篇替换 首先读取到属性的每一行 @property

#进行修改文件名操作
# def doModifiFileName(file_path_list,keydict):
#     #重新拼接文件名
#     new_path_list = []
#     for filename in file_path_list:


#提取所有方法,存放在一个列表里
#参数list: 已过滤的文件列表
#return 列表:所有方法
def getAllmethod(file_path_list):
    #用于存放方法
    method_list = []
    method_name_list = []
    #遍历所有文件名
    for file_path in file_path_list:
        #读取文件内容
        m_file = readContextFromFile(file_path)
        result = re.findall(r'(?:^|\n)([\-|\+].*)', m_file)
        method_list.append(result)
    method_name_list = flatten(method_list)
    return method_name_list

#提取所有方法,存放在一个列表里
#参数list: 已过滤的文件列表
#return 列表:所有需要混淆的方法名和MD5对应的字典
def getAllmethodName(method_list):
    #用于存放方法名
    method_name_list = []
    #遍历存放方法的列表
    for method_name in method_list:
        #读取文件内容
        result = re.findall(r'\w+', method_name)
        method_name_list.append(result)
    #提取第一个方法名
    first_name = []
    for f_name in method_name_list:
        result = f_name[1]
        first_name.append(result)
    #去重
    first_name_qc = []
    first_name_qc = {}.fromkeys(first_name).keys()

    # 生成20位的随机数字母用作密钥
    key_list_m = []
    for i in range(len(first_name_qc)):
        key_list_m.append(sec_key_create())

     # 合并密钥和类名为一个字典
    key_dict = dict(zip(first_name_qc, key_list_m))
    return key_dict

def replaceMain(list,dict):
    #找到main方法的绝对路径
    for filename in list:
        if "main.m" in filename:
            text_str = readContextFromFile(filename)
            for k,v in dict.iteritems():
                replace_reg = re.compile(r'\b(%s)\b' % k)
                text_str = replace_reg.sub(v, text_str)

            writeContextToFile(text_str,filename)
            break

if __name__ == '__main__':
    des = Descr()

    #step 1:获取到工程下的所有.h .m .pch
    hmp_list = hmpchFilter(path)
    des.printList(hmp_list)
    print '------Filter(ido,SYSTEM_LIST)'

    #step 1:获取到需要进行加密的文件的绝对路径 (过滤SDK)
    need_encrypt_files_list = sdkFilter(hmp_list,SDK_LIST)
    des.printList(need_encrypt_files_list)
    print '----KeyDic'

    #step 1.2:过滤系统函数文件
    need_encrypt_files_list = sysFilter(need_encrypt_files_list,SYSTEM_LIST)
    des.printList(need_encrypt_files_list)

    #step 2:生成了类名对应的加密字典
    key_dic = keyDictCreate(need_encrypt_files_list)
    print key_dic
    print '----FilterDic'

    #step 3:混淆关键类名、文件名
    isTrue =doReplaceKeys(need_encrypt_files_list,key_dic)
    print isTrue
    #step 4:混淆main
    replaceMain(hmp_list,key_dic)

    list_m = getAllmethod(need_encrypt_files_list)
    print list_m

    key_dic_m = getAllmethodName(list_m)
    print 'method{k:v}:', key_dic_m

    #step 5:混淆方法名
    isTrue = doReplaceKeys(need_encrypt_files_list,key_dic_m)
    print isTrue
    #step 5:混淆关键属性变量










