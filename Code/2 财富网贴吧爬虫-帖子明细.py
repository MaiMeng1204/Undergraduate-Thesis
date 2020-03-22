# -*- coding: utf-8 -*-
"""
Created on Sat Feb  3 18:50:53 2018
根据帖子列表，逐个访问帖子的每一页，抓取如下内容：
hrefs: 帖子网址
post_uids：发帖人id
post_date：发帖日期
source：发帖工具（PC/Android/iPhone/WinPhone/mobile）
reply_uids：回帖人id
reply_date：回帖日期
post_num：回帖数量

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
import logging
import sys
from lxml import etree
import copy
from ast import literal_eval

#%%
#把错误日志+当前时间写入日志文件，并在屏幕输出
def error_info(log):
    log=time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))+'\t'+log
    with open('./error_log_detail.txt','a') as f:
        f.write(log+'\n')
#    print(log)

#读取文件，并抓取每个帖子的内容
def getUrl(file,website):
    stk=pd.read_csv(r'./post_list/'+file, encoding='utf-8-sig')
    #剔除 href为nan的行
    stk=stk.loc[~pd.isnull(stk['hrefs']),:]
    stk=stk.loc[~pd.isnull(stk['uids']),:]
    stk.reset_index(drop=True,inplace=True)
    '''测试'''
    # stk = stk.iloc[:5, :]
    
    reply_uids = []
    reply_date = []
    reply_content = []
    post_uids = []
    post_date = []
    post_content = []
    source_list = []
    post_num = []
    for ix,[href,uid] in enumerate(zip(stk['hrefs'],stk['uids'])):
        #将uid从字符串转为list
        try:
            uid=literal_eval(uid)
        except:
            uid=[]
            error_info('读取帖子{0}的UID出错'.format(href))
        re_uid, re_date, re_content, po_date, po_content, source, po_num, again = spiderDetail(href,website)
        #如果有问题，就重新读取一次
        if again==True:
            time.sleep(5)
            re_uid, re_date, re_content, po_date, po_content, source, po_num, again = spiderDetail(href,website)
        print('帖子内容：', po_content)
        print('回帖内容：', re_content)
        reply_uids.append(re_uid)
        reply_date.append(re_date)
        reply_content.append(re_content)
        post_uids.append(uid)
        post_date.append(po_date)
        post_content.append(po_content)
        source_list.append(source)
        post_num.append(po_num)
        
        if ix%5==0:
            logger.info('文件{0}: 已完成 {1}/{2} 个帖子明细抓取，当前时间{3}'.format(
                    file,ix+1,stk.shape[0],time.strftime("%H:%M:%S")))
    
    data_all=pd.DataFrame()
    data_all['hrefs']=stk['hrefs']
    data_all['post_uids']=post_uids
    data_all['post_date']=post_date
    data_all['post_content'] = post_content
    data_all['source']=source_list
    data_all['reply_uids']=reply_uids
    data_all['reply_date']=reply_date
    data_all['reply_content'] = reply_content
    data_all['post_num']=post_num
    
    return data_all, stk.shape[0]
    
#只需要提取每个帖子的发帖人、时间
def spiderDetail(href,website):
    again=False
    if href is None:
        return None
    try:
        url=website+href
        '''proxy = random.choice(proxy_ip)
        proxies = {
            'http': proxy,
            'https': proxy
        }
        
        print('proxy:', proxy)'''
        # user_agent="Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:57.0) Gecko/20100101 Firefox/57.0"
        user_agent = random.choice(user_agent_list)
        Host="guba.eastmoney.com"
        headers={
            "User-Agent":user_agent,
            "Host":Host,
            # 'Connection': 'keep-alive',
            'Referrer': 'http://guba.eastmoney.com/'
        }
        print('user_agent:', user_agent)
        homepage = requests.get('http://guba.eastmoney.com/', headers=headers)
        time.sleep(random.random())
        htmlText=requests.get(url, headers=headers).text
        seletor=etree.HTML(htmlText)
        
        #看帖子是否被404
        if len(seletor.xpath('//div[@class="gb404tt"]/text()'))>0:
            error_info('帖子{0}被404'.format(href))
            re_uid, re_date='',''
            post_date=''
            source='Unknown'
            re_num1=0
        else:
            #读取发帖人的发帖时间
            post_date=seletor.xpath('//div[@class="zwfbtime"]/text()')
            post_content = seletor.xpath('//div[contains(@id, "zw") and contains(@id, "body")]//*/text()')
            post_content = ''.join(post_content).replace(u'\u3000', '')
            post_content = post_content.strip()
            try:
                post_date=post_date[0]
            except:
                post_date=''
                again=True
            if '网页版' in post_date:
                source='PC'
            elif '电脑版' in post_date:
                source='PC'
            elif 'Android' in post_date:
                source='Android'
            elif 'iPhone' in post_date:
                source='iPhone'
            elif 'WP' in post_date:
                source='WinPhone'
            elif '手机' in post_date:
                source='mobile'
            elif 'iPad' in post_date:
                source='mobile'
            else:
                source='Unknown'
            #剔除无关字符
            post_date=post_date.replace('发表于 ','')
            post_date=post_date.replace(' 股吧网页版','')
            post_date=post_date.replace(' 东方财富网iPhone版','')
            post_date=post_date.replace(' 东方财富网Android版','')
            post_date=post_date.replace(' 东方财富电脑版','')
            
            post_date=post_date.replace(' 股吧手机网页版','')
            post_date=post_date.replace(' 股吧Android版','')
            post_date=post_date.replace(' 股吧iPhone版','')
            post_date=post_date.replace(' 东方财富通WP版','')
            post_date=post_date.replace(' 东方财富手机版','')
            post_date=post_date.replace(' 东方财富网iPad版','')
            
            #读取回帖数量
            try:
                re_num1=seletor.xpath('//div[@id="zwcontab"]//span[@class="comment_num"]/text()')[0]
                re_num1=re_num1.replace('（','')
                re_num1=re_num1.replace('）','')
                re_num1=int(re_num1)
            except:
                re_num1=0
                re_count = 30
            '''这一段弃置不用，因为部分网页的代码不规范，可能匹配不到
            try:
                temp=seletor.xpath('//div[@id="zwlist"]/script[2]/text()')[0]
                re_num1=int(re.findall(r'var pinglun_num=(\d+);',temp)[0])
            except:
                re_num1=0
                error_info('读取帖子{0}回帖数量1出错'.format(href))
            '''
            #第二次读取回帖数量（有第二页的帖子才有这一信息）
            re_num_temp=seletor.xpath('//span[@class="pagernums1"]/@data-page')
            try:
                re_num_temp=re_num_temp[0]
                re_num_temp=re_num_temp.split('|')
                re_count=int(re_num_temp[2])
                re_num2=int(re_num_temp[1])
                #如果有信息，但两个回帖数量不一致，则输出错误日志
#                if re_num2!=re_num1:
#                    error_info('帖子{0}的两个回帖数量不一致'.format(href))
            except:
                re_num2=1  #设置为1，这样计算出的re_page_num至少为1
                re_count=30
            re_page_num=int(np.ceil(max(re_num1, re_num2)/re_count))
            
            #读取每一页回帖的内容
            re_date='' #回帖时间
            re_uid=''  #回帖id
            re_content=''   #回帖内容
            for page in range(1, re_page_num+1):
                #生成url，并访问这个url
                url=url.split('.html')[0]
                #剔除之前的下一页代码
                url=url.split('_')[0]
                url=url+'_'+str(page)+'.html'
                htmlText=requests.get(url, headers=headers).text
                seletor=etree.HTML(htmlText)
                
                #回复时间
                re_date_list=seletor.xpath('//div[@class="zwlitime"]/text()')
                re_uid_list=seletor.xpath('//div[@class="zwli clearfix"]/@data-huifuid')
                re_content_list = seletor.xpath('//div[@class="short_text"]/text()')
                re_content_list = [x.strip() for x in re_content_list if x.strip != '']

                #剔除无关字符，并将list转换为一个字符串
                for i in range(min(len(re_date_list), len(re_uid_list), len(re_content_list))):
                    date_temp=re_date_list[i]
                    date_temp=date_temp.replace('发表于 ','')
                    date_temp=date_temp.replace('  ',' ')
                    #将回帖时间和回帖人id分别合并到字符串中
                    re_date=re_date+'|'+date_temp
                    re_uid=re_uid+'|'+re_uid_list[i]
                    re_content = re_content + '|' + re_content_list[i].strip()
            
            #剔除re_uid、re_date、re_content的第一个|
            if re_date.startswith('|'):
                re_date=re_date[1:]
            if re_uid.startswith('|'):
                re_uid=re_uid[1:]
            if re_content.startswith('|'):
                re_content=re_content[1:]
    except:
        error_info('读取帖子{0}详细内容出错'.format(href))
        again=True
        re_uid, re_date='',''
        re_content = ''
        post_date=''
        post_content = ''
        source='Unknown'
        re_num1=0
    return re_uid, re_date, re_content, post_date, post_content, source, re_num1, again

#%%
proxy_ip = [
    'http://124.75.27.101:80',
    'http://47.95.202.28:3128',
    'http://220.242.160.147:80',
    'http://117.83.159.219:8118',
    'http://221.122.91.32:10286'
]
user_agent_list = [
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1",
    "Mozilla/5.0 (X11; CrOS i686 2268.111.0) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1092.0 Safari/536.6",
    "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1090.0 Safari/536.6",
    "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/19.77.34.5 Safari/537.1",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.9 Safari/536.5",
    "Mozilla/5.0 (Windows NT 6.0) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.36 Safari/536.5",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
    "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_0) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
    "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
    "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
    "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
    "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.0 Safari/536.3",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24",
    "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24",
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36'
]
os.chdir(r'E:\NJU\毕业论文\Data') # Set current working directory
logger = logging.getLogger()
logger.setLevel(logging.INFO)
fh = logging.FileHandler('爬取帖子明细.log')
fh.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO)
logger.addHandler(fh)
logger.addHandler(handler)
#读取每个股票的帖子列表
#读取csv文件的地址不能有中文，但写入时可以有中文
filepath = r'./post_list'
#files = os.listdir(filepath)
#files.sort()

website='http://guba.eastmoney.com'

stk=pd.read_excel(r'../Data/000016cons.xls', converters={'成分券代码Constituent Code': str},encoding='GBK')
stk = stk.iloc[25:, :]
#确定股票的文件名列表
stk['files']=stk['成分券代码Constituent Code'].apply(lambda x: 'Guba-' + x + '.csv')
files=stk['files'].values.tolist()

#抓取数据()

files_scrape=files
for i in range(len(files_scrape)):
    file=files_scrape[i]
    stk=file.split('-')[1].split('.')[0]
    data=pd.DataFrame()
    data,post_num = getUrl(file,website)
    
    logger.info('完成股票{0}(序号:{1}/{2})的{3}个帖子，当前时间{4}'.format(
            stk,i+1,len(files_scrape),post_num,time.strftime("%H:%M:%S")))
    data.to_csv('./post_detail/Guba-'+stk+'-detail.csv', encoding='utf_8_sig', index=False)
