import pandas as pd
import jieba
import os
import matplotlib.pyplot as plt
from wordcloud import WordCloud

data_path = r'post_detail'
file_list = os.listdir(data_path)
all_post = pd.DataFrame()
for file in file_list:
    post_detail = pd.read_csv(os.path.join(data_path, file), usecols=[1, 2, 3, 7, 8], converters={2: str, 'reply_content':str}).dropna(subset=['post_date', 'post_content'])
    post_detail['post_date'] = pd.to_datetime(post_detail['post_date'].apply(lambda x: x.split(' ')[0]), format='%Y-%m-%d')
    post_detail.sort_values('post_date', ascending=False, inplace=True)
    post_detail['post_date'] = post_detail['post_date'].apply(lambda x: x.year * 10000 + x.month * 100 + x.day)
    post_detail.reset_index(drop=True, inplace=True)
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
