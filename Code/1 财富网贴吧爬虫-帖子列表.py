# -*- coding: utf-8 -*-
"""
Created on Tue Jan 30 21:42:19 2018
抓取每个股票版块的帖子列表，抓取如下内容：
titles：标题
reads：浏览量
comm：回复量
hrefs：网址
users：发帖人用户名
uids：发帖人id
post：发帖时间
update：最后回复时间
page：帖子在第几页

@author: Administrator
"""
import pandas as pd
import numpy as np
import timeit
import time
import random
import re
import os
import requests
from lxml import etree
import copy

#%%
#把错误日志+当前时间写入日志文件，并在屏幕输出
def error_info(log):
    log=time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))+'\t'+log
    with open('./error_log.txt','a') as f:
        f.write(log+'\n')
    print(log)
    
def getUrl(stock):
    #读取论坛帖子的页数
    url = "http://guba.eastmoney.com/list,{0},f.html".format(stock)
    try:
        user_agent="Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:57.0) Gecko/20100101 Firefox/57.0"
        Host="guba.eastmoney.com"
        headers={
            "User-Agent":user_agent,
            "Host":Host
            }
        htmlText=requests.get(url, headers=headers).text
        seletor=etree.HTML(htmlText)
        #由帖子总数和每页帖子数计算出页码
        page_string=seletor.xpath('//span[@class="pagernums"]/@data-pager')
        page_info=page_string[0].split(',')[-1]
        page_info=page_info.split('|')
        pagenum=int(np.ceil(int(page_info[1])/int(page_info[2])))
    except:
        error_info('读取股票{0}的帖子总页数出错'.format(stock))
    
    data_all=pd.DataFrame()
    for i in range(pagenum):
        url = "http://guba.eastmoney.com/list,{0},f_{1}.html".format(stock, i+1)
        data_temp=pd.DataFrame()
        data_temp=spiderPage(url,i+1,stock)
        if data_all.shape[0]==0:
            data_all=copy.deepcopy(data_temp)
        else:
            data_all=data_all.append(data_temp,ignore_index=True)
        if i%500==0:
            print('股票{0}: 已完成{1}/{2}页帖子列表抓取'.format(stock,i+1,pagenum))
    return data_all,pagenum
    
def spiderPage(url,page,stock):
    if url is None:
        return None
    
    try:
        user_agent="Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:57.0) Gecko/20100101 Firefox/57.0"
        Host="guba.eastmoney.com"
        headers={
            "User-Agent":user_agent,
            "Host":Host
        }
#        # IP地址取自国内髙匿代理IP网站：http://www.xicidaili.com/nn/
#        proxies={
#            "http": "http://39.134.68.8:80"
#        }

#        htmlText=requests.get(url, headers=headers, proxies=proxies).text
        htmlText=requests.get(url, headers=headers).text
        
        seletor=etree.HTML(htmlText)
        #读取每一条帖子的网址，并获取帖子内容
        articles=seletor.xpath('//div[contains(@class, "articleh")]')
        titles=[] #标题列表
        reads=[]  #阅读量列表
        comm=[]   #评论量列表
        hrefs=[]  #帖子地址
        users=[]  #发帖人账号
        uids=[]   #发帖人id
        post=[]   #发表日期
        update=[] #最后更新时间，如果没有回帖的话，这就是发帖时间（偶尔有例外）
        for article in articles:
            #用.代表本节点，不然默认是在父节点搜索
            titles.append(article.xpath('.//a/@title'))
            reads.append(article.xpath('.//span[@class="l1 a1"]/text()'))
            comm.append(article.xpath('.//span[@class="l2 a2"]/text()'))
            #不能只取第一个网址，有时候帖子的网址在后面几个中
            href_list=article.xpath('.//a/@href')
            for item in href_list:
                if item.startswith('/news,'):
                    hrefs.append(item)
                    break
                else:
                    pass
            #当没有符合要求的帖子网址时，填补空
            if len(hrefs)<len(titles):
                hrefs.append(None)
            uids.append(article.xpath('.//a/@data-popper'))
            users.append(article.xpath('.//a/font/text()'))
            update.append(article.xpath('.//span[@class="l5 a5"]/text()'))
            post.append(article.xpath('.//span[@class="l5 a5"]/text()'))
            #抓取帖子详细内容
#            spiderDetail(hrefs)
        data=pd.DataFrame(titles,columns=['titles'])
        data['reads']=reads
        data['comm']=comm
        data['hrefs']=hrefs
        data['users']=users
        data['uids']=uids
        data['post']=post
        data['update']=update
        data['page']=page #帖子的第几页（随时间变化）
        
        #删除无内容的帖子
        data=data.loc[~pd.isnull(data['titles']),:]
        #删除无网址，或网址不符合要求的帖子
        data=data.loc[~pd.isnull(data['hrefs']),:]
    except:
        error_info('读取股票{0}的第{1}页帖子列表出错'.format(stock,page))
        data=pd.DataFrame()
    return data

def spiderDetail(href):
    if href is None:
        return None
    try:
        pass
    except:
        error_info('读取帖子{0}详细内容出错'.format(href))
    
#%%
os.chdir(r'E:\NJU\毕业论文\Data') # Set current working directory

#读取股票代码
##以CSMAR的数据为基础
#types={'Stkcd':str,'Indcd':str,'Stknme':str,'Nnindcd':str,'Nnindnme':str,
#       'Estbdt':str,'Listdt':str,'Markettype':str}
#stk=pd.read_csv(r'.\stock_info_CSMAR.csv',sep='\t',dtype=types)
#
##剔除无关数据
## B股不要
#stk=stk.loc[stk['Markettype']!='2',:]
#stk=stk.loc[stk['Markettype']!='8',:]
## 终止上市的不要
#stk=stk.loc[stk['Statco']!='D',:]
## 替换列名称
#stk=stk.loc[:,['Stkcd','Stknme','Nnindnme','Estbdt','Listdt','Statco','Markettype']]
#stk.columns=['股票代码','股票简称','行业代码','公司成立日期','上市日期','交易状态','市场类型']

'''读取沪深300成分股票代码，仍然以CSMAR为准'''
types={'股票代码':str}
stk=pd.read_excel(r'../Data/000300cons.xls', converters={'成分券代码Constituent Code': str},encoding='GBK')
index = np.where(stk['成分券代码Constituent Code'] == '002555')[0][0]
stk = stk.iloc[index:, :]
#测试代码
#data=getUrl('300736')

stk_list=stk['成分券代码Constituent Code'].values.tolist()

#抓取数据
#stk_list=['600856']
#for stock in stk_list:
# os.mkdir('post_list')
for ix,stock in enumerate(stk_list):
    data=pd.DataFrame()
    data,page=getUrl(stock)
    print('抓取股票{0}(序号{1}/{2})的全部{3}页帖子，当前时间{4}'.format(
            stock,ix+1,stk.shape[0],page,time.strftime("%H:%M:%S")))
    data.to_csv('./post_list/Guba-'+ stock +'.csv',encoding='utf_8_sig',index=False)