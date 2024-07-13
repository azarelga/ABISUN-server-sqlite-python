import streamlit as st
import numpy as np
import plotly.express as px
import pandas as pd
import time
from keras.models import load_model
import datetime
from db import read_df, read_df_60_seconds, latest_data # Import the read_data function from db_utils

class App:
    def __init__(self):
        st.title("ABISUN: Sensor Data Viewer")
        self.model_dewasa = load_model('model/model_kedalaman_dewasa_anak.h5')
        # self.model_bayi = load_model('model/model_kedalaman_bayi.h5')
        self.df = read_df()
        if 'running' not in st.session_state:
            st.session_state['running'] = False
        if 'done' not in st.session_state:
            st.session_state['done'] = False
        self.time_series = pd.DataFrame()
        self.start_time = time.strftime("%Y-%m-%d %H:%M:%S")
        self.subject_session = "Dewasa"

    def main(self):
        if not st.session_state['running']:
            self.start_button()
        else:
            countdown_placeholder = st.empty()
            for i in range(5, 0, -1):
                countdown_placeholder.text(f"Siap - siap! Simulasi CPR akan dimulai dalam {i} detik...")
                time.sleep(1)
            countdown_placeholder.empty()  # Clear countdown after starting
            self.show_live()
            self.result()
            st.subheader("Mulai lagi?")
            self.start_button()


    def start_button(self):
        self.subject_session = st.selectbox("Pilih Sesi", ["Dewasa", "Anak", "Bayi"])
        if st.button("Mulai Simulasi", type='primary'):
            st.session_state['running'] = True
            st.session_state['done'] = False
            st.empty()

    def show_live(self):
        live_placeholder = st.empty()
        with live_placeholder.container():
            self.live_chart("depth")
        live_placeholder.empty()

    def live_chart(self, col):
        text_placeholder=st.empty()
        chart_placeholder = st.empty()
        self.start_time = time.strftime("%Y-%m-%d %H:%M:%S")
        for i in range(60, -1 , -1):
            text_placeholder.write(f"Sisa {i} detik lagi!")
            self.time_series = read_df_60_seconds(self.start_time)
            chart_placeholder.plotly_chart(self.chart_builder('depth'))
            time.sleep(1)
        st.session_state['done'] = True

    def chart_builder(self, col):
        fig = px.line(self.time_series, x='timestamp', y=col, title="Data Kedalaman")
        fig.update_layout(xaxis_title='Waktu', 
                          yaxis_title='Kedalaman', 
                          modebar_remove=['select','zoom', 'pan'])
        return fig

    def split_dataframe(self, df):
        # Calculate the size of each part
        total_rows = 60
        part_size = total_rows // 3

        # Split the DataFrame into three parts based on the order
        df_part1 = df.iloc[:part_size]
        df_part2 = df.iloc[part_size:2*part_size]
        df_part3 = df.iloc[2*part_size:]

        # If there are remaining rows, add them to the last part
        if total_rows % 3 != 0:
            df_part3 = df.iloc[2*part_size:]

        return df_part1, df_part2, df_part3

    def result(self):
        df_part1, df_part2, df_part3 = self.split_dataframe(self.time_series)
        array_part1 = df_part1[['depth']].to_numpy().reshape(-1, 10, 1)
        array_part2 = df_part2[['depth']].to_numpy().reshape(-1, 10, 1)
        array_part3 = df_part3[['depth']].to_numpy().reshape(-1, 10, 1)
        predictions = [self.model_dewasa.predict(array_part1), self.model_dewasa.predict(array_part2), self.model_dewasa.predict(array_part3)]
        string_predictions = ["Stabil", "Tidak Stabil", "Cenderung Terlalu Dalam", "Cenderung Kurang Dalam"]
        col1, col2, col3 = st.columns(3)
        with col1:
            st.subheader(f"Performa 20 detik pertama")
            st.write(string_predictions[np.argmax(predictions[0],axis=1)])
        with col2:
            st.subheader(f"Performa 20 detik kedua")
            st.write(string_predictions[np.argmax(predictions[1],axis=1)])
        with col3:
            st.subheader(f"Performa 20 detik terakhir")
            st.write(string_predictions[np.argmax(predictions[2],axis=1)])
        result_placeholder = st.empty()
        with result_placeholder.container():
            st.subheader("Berikut adalah hasil CPR anda!")
            chart_placeholder = st.empty()
            chart_placeholder.plotly_chart(self.chart_builder('depth'))
        if not st.session_state['done']:
            result_placeholder.empty()

if __name__ == "__main__":
    app = App()
    app.main()
