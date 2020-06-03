# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'
# %%
import pandas as pd
import numpy as np
import os


# %%
file_list = os.listdir('sentiment_result/')[:15]


# %%
def get_topic(row):
    max_topic = np.max([row[2:9]])
    if max_topic == row[0]:
        row['主题一'] = row['情感']
    elif max_topic == row[1]:
        row['主题二'] = row['情感']
    elif max_topic == row[2]:
        row['主题三'] = row['情感']
    elif max_topic == row[3]:
        row['主题四'] = row['情感']
    elif max_topic == row[4]:
        row['主题五'] = row['情感']
    elif max_topic == row[5]:
        row['主题六'] = row['情感']
    else:
        row['主题七'] = row['情感']
    return row


# %%
def senti(data):
    if data['sentiment'] > 0.6:
        data['情感'] = '积极'
    elif data['sentiment'] < 0.4:
        data['情感'] = '消极'
    return data


# %%
file_shape = []
iterables = [['主题一', '主题二', '主题三', '主题四', '主题五', '主题六', '主题七'], ['积极', '消极', '中性']]
senti_sum = pd.DataFrame(columns=pd.MultiIndex.from_product(iterables, names=['主题', '情感']))
for file in file_list:
    data_path = os.path.join('sentiment_result', file)
    lda_path = os.path.join('LDA_result_topic7', '{}_doc_topic_result.txt'.format(file.split('.')[0]))
    data = pd.read_csv(data_path, usecols=[2, 6], encoding='utf8')
    lda_data = pd.read_csv(lda_path, header=None)
    data = pd.concat([data, lda_data], axis=1)
    data.dropna(subset=['sentiment'], inplace=True)
    file_shape.append(data.shape[0])
    data['主题一'] = np.NAN
    data['主题二'] = np.NAN
    data['主题三'] = np.NAN
    data['主题四'] = np.NAN
    data['主题五'] = np.NAN
    data['主题六'] = np.NAN
    data['主题七'] = np.NAN
    data['情感'] = '中性'
    data = data.apply(senti, axis=1)
    data = data.apply(get_topic, axis=1)
    senti_sum.loc[file.split('.')[0], ('主题一', '积极')] = data['主题一'].value_counts()['积极']
    senti_sum.loc[file.split('.')[0], ('主题一', '消极')] = data['主题一'].value_counts()['消极']
    senti_sum.loc[file.split('.')[0], ('主题一', '中性')] = data['主题一'].value_counts()['中性']
    senti_sum.loc[file.split('.')[0], ('主题二', '积极')] = data['主题二'].value_counts()['积极']
    senti_sum.loc[file.split('.')[0], ('主题二', '消极')] = data['主题二'].value_counts()['消极']
    senti_sum.loc[file.split('.')[0], ('主题二', '中性')] = data['主题二'].value_counts()['中性']
    senti_sum.loc[file.split('.')[0], ('主题三', '积极')] = data['主题三'].value_counts()['积极']
    senti_sum.loc[file.split('.')[0], ('主题三', '消极')] = data['主题三'].value_counts()['消极']
    senti_sum.loc[file.split('.')[0], ('主题三', '中性')] = data['主题三'].value_counts()['中性']
    senti_sum.loc[file.split('.')[0], ('主题四', '积极')] = data['主题四'].value_counts()['积极']
    senti_sum.loc[file.split('.')[0], ('主题四', '消极')] = data['主题四'].value_counts()['消极']
    senti_sum.loc[file.split('.')[0], ('主题四', '中性')] = data['主题四'].value_counts()['中性']
    senti_sum.loc[file.split('.')[0], ('主题五', '积极')] = data['主题五'].value_counts()['积极']
    senti_sum.loc[file.split('.')[0], ('主题五', '消极')] = data['主题五'].value_counts()['消极']
    senti_sum.loc[file.split('.')[0], ('主题五', '中性')] = data['主题五'].value_counts()['中性']
    senti_sum.loc[file.split('.')[0], ('主题六', '积极')] = data['主题六'].value_counts()['积极']
    senti_sum.loc[file.split('.')[0], ('主题六', '消极')] = data['主题六'].value_counts()['消极']
    senti_sum.loc[file.split('.')[0], ('主题六', '中性')] = data['主题六'].value_counts()['中性']
    senti_sum.loc[file.split('.')[0], ('主题七', '积极')] = data['主题七'].value_counts()['积极']
    senti_sum.loc[file.split('.')[0], ('主题七', '消极')] = data['主题七'].value_counts()['消极']
    senti_sum.loc[file.split('.')[0], ('主题七', '中性')] = data['主题七'].value_counts()['中性']
    data.to_csv('all_result/{}.csv'.format(file.split('.')[0]), encoding='gbk',index=False)
senti_sum.to_csv('sentiment_result/senti_count.csv', encoding='gbk')


# %%
#!/usr/bin/env python
# coding: utf-8

# 数据预处理
import pandas as pd
import numpy as np
import os

data_path = 'post_detail'
file_list = os.listdir(data_path)
all_post = pd.DataFrame()
tickers = []
file_shape = []
start_date = []
end_date = []
for file in file_list:
    post_detail = pd.read_csv(os.path.join(data_path, file), usecols=[1, 2, 3, 7, 8], converters={2: str, 'reply_content':str}).dropna(subset=['post_date', 'post_content'])
    post_detail['post_date'] = pd.to_datetime(post_detail['post_date'].apply(lambda x: x.split(' ')[0]), format='%Y-%m-%d')
    post_detail.sort_values('post_date', ascending=False, inplace=True)
    start_date.append(post_detail['post_date'].iloc[-1])
    end_date.append(post_detail['post_date'].iloc[0])
    post_detail['post_date'] = post_detail['post_date'].apply(lambda x: x.year * 10000 + x.month * 100 + x.day)
    post_detail.reset_index(drop=True, inplace=True)
    all_post = pd.concat([all_post, post_detail])
    tickers.append(file.split('-')[1])
    file_shape.append(post_detail.shape[0])
    
summary = pd.DataFrame({'股票代码': tickers, '贴子数': file_shape, '起始时间': start_date, '结束时间': end_date})
summary.to_csv('样本概览.csv', encoding='gbk')

