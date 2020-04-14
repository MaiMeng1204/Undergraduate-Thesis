#!/usr/bin/env python
# coding: utf-8

# 数据预处理
import pandas as pd
import numpy as np
import jieba
import os
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation

data_path = r'Data\post_detail'
file_list = os.listdir(data_path)
all_post = pd.DataFrame()
file_shape = [0]
for file in file_list:
    post_detail = pd.read_csv(os.path.join(data_path, file), usecols=[1, 2, 3, 7, 8], converters={2: str, 'reply_content':str}).dropna(subset=['post_date', 'post_content'])
    post_detail['post_date'] = pd.to_datetime(post_detail['post_date'].apply(lambda x: x.split(' ')[0]), format='%Y-%m-%d')
    post_detail.sort_values('post_date', ascending=False, inplace=True)
    post_detail['post_date'] = post_detail['post_date'].apply(lambda x: x.year * 10000 + x.month * 100 + x.day)
    post_detail.reset_index(drop=True, inplace=True)
    all_post = pd.concat([all_post, post_detail])
    file_shape.append(post_detail.shape[0])
print(file_shape)
corpus = []
output_dir = r'Data\LDA_result2'
if not os.path.exists(output_dir):
    os.makedirs(output_dir, exist_ok=True)
for index, row in all_post.iterrows():
    all_list = row['post_content'] + row['reply_content'].replace('|', '。')
    cut = jieba.cut(all_list)
    result = ' '.join(cut)
    corpus.append(result)

#从文件导入停用词表
stpwrdpath = r"Data\stop_words\stop_words.txt"
stpwrd_dic = open(stpwrdpath, 'r')
stpwrd_content = stpwrd_dic.read()

#将停用词表转换为list  
stpwrdlst = stpwrd_content.splitlines()
stpwrd_dic.close()

cntVector = CountVectorizer(stop_words=stpwrdlst)
cntTf = cntVector.fit_transform(corpus)
lda = LatentDirichletAllocation(n_components=3, max_iter=1000)
docres = lda.fit_transform(cntTf)

# 保存结果
file_shape = np.cumsum(file_shape)
print(file_shape)
for index, file in enumerate(file_list):
    with open(os.path.join(output_dir, '{}_doc_topic_result.txt'.format(file.split('-')[1])), 'w') as f:
        docres_temp = docres[file_shape[index]: file_shape[index+1]]
        for doc in docres_temp:
            f.write(','.join([str(i) for i in doc]))
            f.write('\n')
        f.close()

tf_feature_names = cntVector.get_feature_names()
with open(os.path.join(output_dir, 'topic_word_result.txt'), 'w') as f:
    for index, topic in enumerate(lda.components_):
        f.write(','.join([tf_feature_names[i] for i in topic.argsort()[:-20:-1]]))
        f.write('\n')
    f.close()