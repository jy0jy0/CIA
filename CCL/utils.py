#%%
import pandas as pd
import torch
import numpy as np
import random
from collections import defaultdict
from model import MF, NCF
#%%
# load_data
def data_load():
    file_path = "movie_data"
    train_data = pd.read_csv(file_path+"/"+"ua.base", sep='\t', names=["user_id", "item_id", "rating", "timestamp"])
    test_data = pd.read_csv(file_path+"/"+"ua.test", sep='\t', names=["user_id", "item_id", "rating", "timestamp"])
    num_user = max(train_data["user_id"].max(),test_data["user_id"].max())
    num_item = max(train_data["item_id"].max(),test_data["item_id"].max())
    x_train = train_data[["user_id","item_id"]].to_numpy()
    x_train = x_train - 1 # 시작 인덱스 0부터
    y_train = train_data[["rating"]].to_numpy()
    x_test = test_data[["user_id","item_id"]].to_numpy()
    x_test = x_test - 1 # 시작 인덱스 0부터
    y_test = test_data[["rating"]].to_numpy()
    train_df = pd.DataFrame(data = x_train, columns = ["user","item"])
    return train_data, test_data, x_train, y_train, x_test, y_test, train_df, num_user, num_item

# sampling "popularity"
def calculus_pop(train_df, num_user):    
    item_popularity = train_df['item'].value_counts().reset_index()
    item_popularity.columns = ['item', 'interaction_count']
    item_popularity = item_popularity.sort_values(by = "item").reset_index(drop = True)
    # 누락된 아이템을 자동으로 추가하고 상호작용이 없으면 0으로 설정
    item_popularity = item_popularity.set_index("item").reindex(range(1682), fill_value=0)
    item_pop = item_popularity["interaction_count"]
    item_pop = item_pop / item_pop.max()
    item_pop = np.sqrt(item_pop)
    # sampling "user_popularity"
    total_user_list = [i for i in range(num_user)]
    train_df['popularity'] = train_df['item'].map(item_pop)
    return item_pop, train_df
# 유저별로 아이템 인기도 평균 계산
def calculus_user_pop(train_df, x_test):
    user_popularity_avg = train_df.groupby('user')['popularity'].mean()
    top_20_user = user_popularity_avg.nlargest(5).index
    low_20_user = user_popularity_avg.nsmallest(5).index
    all_user_idx = np.unique(x_test[:,0])
    all_tr_idx = np.arange(len(x_test))
    return user_popularity_avg, all_user_idx, all_tr_idx

def load_movie_data():
    movie_path = "movie_data/u.item"
    # 결과를 저장할 리스트
    movie_titles = []
    # 파일 읽기
    with open(movie_path, encoding='latin-1') as file:
        for line in file:
            # 각 줄을 '|' 기준으로 나눔
            columns = line.split('|')
            # 두 번째 열 (영화 제목)에서 년도 제거
            movie_name = columns[1].rsplit(' (', 1)[0]
            
            # 만약 제목이 ', The'로 끝나면 수정
            if movie_name.endswith(', The'):
                movie_name = 'The ' + movie_name[:-5]  # ', The'를 떼고 앞에 'The '를 붙이기
            elif movie_name.endswith(', An'):
                movie_name = 'An ' + movie_name[:-4]  # ', An' 처리
            elif movie_name.endswith(', A'):
                movie_name = 'A ' + movie_name[:-3]   # ', A' 처리

            movie_titles.append(movie_name)
        movie_array = np.array(movie_titles)
    return movie_array
# 리스트를 NumPy 배열로 변환
def user_movie_name(train_data, movie_array):        
    train_data_true = train_data[train_data["rating"] >= 3]
    train_data_true = train_data_true[["user_id","item_id"]]
    train_data_true = train_data_true - 1
    user_movie = pd.DataFrame({"user_id":train_data_true["user_id"], 
                            "movie_name":movie_array[train_data_true["item_id"]]})
    return user_movie


