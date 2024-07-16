from db import read_df
from keras.models import load_model
import pandas as pd
import numpy as np
import random
from sklearn.preprocessing import StandardScaler
import joblib

def split_dataframe(df):
    # Calculate the size of each part
    total_rows = 60
    part_size = total_rows // 3

    # Split the DataFrame into three parts based on the order
    df_part1 = df.iloc[:part_size]
    df_part2 = df.iloc[part_size:2*part_size]
    df_part3 = df.iloc[2*part_size:]
    def average_rows(df_part):
        avg_df = pd.DataFrame((df_part.values[::2] + df_part.values[1::2]) / 2)
        return avg_df

    # Reduce the number of rows in each part by averaging every two rows
    df_part1_avg = average_rows(df_part1)
    df_part2_avg = average_rows(df_part2)
    df_part3_avg = average_rows(df_part3)

    return df_part1_avg, df_part2_avg, df_part3_avg


scaler = joblib.load('model/scaler.gz')
df = read_df()
model_dewasa = load_model('model/model_kedalaman_dewasa_anak.h5')
random_array = np.random.uniform(4.0, 5.0, 10).reshape(1,-1)
print(random_array)
random_array = scaler.transform(random_array)
random_array = random_array.reshape(1,10,-1) 

y_pred = model_dewasa.predict(random_array)
y_pred_label = np.argmax(y_pred, axis=1)
print(y_pred_label)
