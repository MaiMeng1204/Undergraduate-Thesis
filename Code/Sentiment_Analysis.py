import pandas as pd
import os
import logging
# from aip import AipNlp
from snownlp import SnowNLP

FORMAT = '%(asctime)-15s %(message)s'
logging.basicConfig(filename='E:/NJU/毕业论文/Code/情感分析.log', level='INFO', format=FORMAT)

'''
APP_ID = '19098615'
API_KEY = 'mitF2GQL3mK9a9YXvVoqmQAR'
SECRET_KEY = '08611Sh4hlKEPcYerTSHODCM6q3Ymmsd'
client = AipNlp(APP_ID, API_KEY, SECRET_KEY)
'''

data_path = r'E:\NJU\毕业论文\Data\post_detail'
output_dir = os.path.join(r'E:\NJU\毕业论文\Data', 'sentiment_result')
if not os.path.exists(output_dir):
    os.makedirs(output_dir, exist_ok=True)
file_list = os.listdir(data_path)
for file in file_list:
    logging.info('处理文档{}'.format(file))
    try:
        post_detail = pd.read_csv(os.path.join(data_path, file), usecols=[1, 2, 3, 7, 8], converters={2: str, 'reply_content':str}).dropna(subset=['post_date', 'post_content'])
        post_detail['post_date'] = pd.to_datetime(post_detail['post_date'].apply(lambda x: x.split(' ')[0]), format='%Y-%m-%d')
        post_detail.sort_values('post_date', ascending=False, inplace=True)
        post_detail['post_date'] = post_detail['post_date'].apply(lambda x: x.year * 10000 + x.month * 100 + x.day)
        post_detail.reset_index(drop=True, inplace=True)
        for index, row in post_detail.iterrows():
            post_content = row['post_content']
            if len(post_content) > 300:
                continue
            reply_content = row['reply_content'].replace('|', '。')
            content = post_content + reply_content
            print('content:', content)
            if content == '':
                continue
            items = SnowNLP(content)  # 情感分析
                
            sentiment = items.sentiments   # positive的概率
            print('sentiment:', sentiment)
            post_detail.loc[index, 'sentiment'] = sentiment
        post_detail.to_csv(os.path.join(output_dir, file.split('-')[1] + '.csv'))
    
    except Exception as e:
        logging.error(e)
        # print(client.sentimentClassify(content)["error_msg"])
