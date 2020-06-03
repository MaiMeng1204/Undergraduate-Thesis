#!/usr/bin/env python
# coding: utf-8

# 数据预处理
import pandas as pd
import numpy as np
import jieba
import os
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation
from sklearn.model_selection import GridSearchCV

data_path = 'post_detail'
file_list = os.listdir(data_path)
all_post = pd.DataFrame()
file_shape = [0]
for file in file_list:
    post_detail = pd.read_csv(os.path.join(data_path, file), usecols=[1, 2, 3, 7, 8], converters={2: str, 'reply_content':str}).dropna(subset=['post_date', 'post_content'])
    post_detail['post_date'] = pd.to_datetime(post_detail['post_date'].apply(lambda x: x.split(' ')[0]), format='%Y-%m-%d')
    post_detail.sort_values('post_date', ascending=False, inplace=True)
    post_detail['post_date'] = post_detail['post_date'].apply(lambda x: x.year * 10000 + x.month * 100 + x.day)
    post_detail.reset_index(drop=True, inplace=True)
    file_shape.append(post_detail.shape[0])
    all_post = pd.concat([all_post, post_detail])

corpus = []
for index, row in all_post.iterrows():
    all_list = row['post_content'] + row['reply_content'].replace('|', '。')
    cut = jieba.cut(all_list)
    result = ' '.join(cut)
    corpus.append(result)


#从文件导入停用词表
with open(r'stopwords-master\all_stopwords.txt', 'r', encoding='gbk') as f:
    stopwords = f.read()
    stpwrdlst = stopwords.splitlines()
    f.close()
stpwrdlst = stopwords.splitlines()


# 确定最优topic数
search_params = {'n_components': list(range(1, 21))}
cntVector = CountVectorizer(stop_words=stpwrdlst)
cntTf = cntVector.fit_transform(corpus)
lda = LatentDirichletAllocation(max_iter=10)
gridsearch = GridSearchCV(lda, param_grid=search_params, n_jobs=-1, verbose=0)
gridsearch.fit(cntTf)
print("Best Model's Params: ", gridsearch.best_params_)
print("Best Log Likelihood Score: ", gridsearch.best_score_)


# %%
result = pd.DataFrame(gridsearch.cv_results_)


# %%
gridsearch.best_estimator_.perplexity(cntTf)


# %%
result.to_csv('LDA主题数选取结果.csv')


# %%
# 训练LDA模型
topic = 7
lda = LatentDirichletAllocation(n_components=topic, max_iter=10)
docres = lda.fit_transform(cntTf)


# %%
# 保存结果
file_shape = np.cumsum(file_shape)
output_dir = r'LDA_result_topic{}'.format(topic)
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


# %%
import matplotlib.pyplot as plt
from wordcloud import WordCloud
wc = WordCloud(
    background_color = "white", #设置背景颜色
    #mask = "图片",  #设置背景图片
    max_words = 200, #设置最大显示的字数
    stopwords = stpwrdlst, #设置停用词
    font_path = r"E:\Font\SourceHanSerifSC_EL-M\SourceHanSerifSC-Regular.otf",
    #设置中文字体，使得词云可以显示（词云默认字体是“DroidSansMono.ttf字体库”，不支持中文）
    max_font_size = 50,  #设置字体最大值
    random_state = 30, #设置有多少种随机生成状态，即有多少种配色方案
)
myword = wc.generate(corpus)#生成词云

plt.imshow(myword)
plt.axis("off")
plt.show()

