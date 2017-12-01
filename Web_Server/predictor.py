import pandas as pd
import numpy as np
import math
import pickle
from sklearn.ensemble import RandomForestRegressor

with open('storage/RF_models.pickle', mode='rb') as f:
     RF_models = pickle.load(f)

RF_avoid_0_to_7682 = RF_models["RF_avoid_0_to_7682"]
RF_avoid_7682_to_15364 = RF_models["RF_avoid_7682_to_15364"]
RF_avoid_15364_to_23046 = RF_models["RF_avoid_15364_to_23046"]
RF_avoid_23046_to_30728 = RF_models["RF_avoid_23046_to_30728"]
RF_whole_data = RF_models["RF_whole_data"]

with open('storage/train_data_urls.pickle', mode='rb') as f:
    train_data_urls = pickle.load(f)

#予測値を出す関数
def get_pred(DF_analytical_data):
    if(list(DF_analytical_data.url)[0] in list(train_data_urls.iloc[pd.Series(range(0,7682))])):
        #print(1)
        return RF_avoid_0_to_7682.predict(DF_analytical_data.iloc[:,3:])[0]
    if(list(DF_analytical_data.url)[0] in list(train_data_urls.iloc[pd.Series(range(7682,15364))])):
        #print(2)
        return RF_avoid_7682_to_15364.predict(DF_analytical_data.iloc[:,3:])[0]
    if(list(DF_analytical_data.url)[0] in list(train_data_urls.iloc[pd.Series(range(15364,23046))])):
        #print(3)
        return RF_avoid_15364_to_23046.predict(DF_analytical_data.iloc[:,3:])[0]
    if(list(DF_analytical_data.url)[0] in list(train_data_urls.iloc[pd.Series(range(23046,30728))])):
        #print(4)
        return RF_avoid_23046_to_30728.predict(DF_analytical_data.iloc[:,3:])[0]
    else:
        #print(5)
        return RF_whole_data.predict(DF_analytical_data.iloc[:,3:])[0]

