import streamlit as st
import numpy as np
import plotly.express as px
import pandas as pd
import requests
import joblib
import time
from keras.models import load_model
import datetime
from db import read_df, read_df_60_seconds, latest_data # Import the read_data function from db_utils

class App:
    def __init__(self):
        self.model = None
        self.scaler = joblib.load('../model/scaler.gz')
        self.df = read_df()
        if 'running' not in st.session_state:
            st.session_state['running'] = False
        if 'done' not in st.session_state:
            st.session_state['done'] = False
        self.time_series = pd.DataFrame()
        self.start_time = time.strftime("%Y-%m-%d %H:%M:%S")
        self.subject_session = "Dewasa"
        self.labels = []
        self.string_feedbacks = [
            "Kerja bagus! Kompresimu sudah stabil, mari pertahankan hingga akhir sesi!",
            "Tekananmu tidak stabil, kadang terlalu dangkal, kadang terlalu dalam, coba perdekat tekanan di sekitar 4 cm!",
            "Pelan - pelan, sobat! Kompresimu terlalu dalam!", 
            "Memang ini melelahkan, tapi kompresimu terlalu dangkal, coba tekan lebih dalam!",
            "Tetap lakukan kompresi!"
        ]
        self.string_predictions = [
            "Stabil",
            "Tidak Stabil",
            "Cenderung Terlalu Dalam", 
            "Cenderung Kurang Dalam"
        ]
        self.server_url = "http://192.168.100.11:5000/last-request-time"  # Replace with your server URL

    def main(self):
        if not st.session_state['running']:
            # Halaman utama
            st.title("Selamat Datang pada Simulasi RJP: ABISUN!")
            st.header("Tata Cara CPR yang Benar")
            st.write("""
            1. Pastikan area aman untuk Anda dan subjek RJP.
            2. Lakukan kompresi dada:
                - Tempatkan tumit salah satu tangan di tengah dada korban, tepat di antara puting susu.
                - Tempatkan tangan lainnya di atas tangan pertama dan kunci jari-jari Anda.
                - Tekan dada korban ke bawah setidaknya 5 cm untuk orang dewasa, 4 cm untuk anak-anak, dan 3 cm untuk bayi.
                - Lakukan kompresi dengan kecepatan 100-120 kali per menit.
            3. Lanjutkan siklus 30 kompresi.
            """)

            st.header("Step by Step Simulasi")
            st.write("""
            0. Buatlah hotspot dari Handphone anda dengan detail sebagai berikut, pastikan laptop anda juga sudah terhubung:
                - Nama Hotspot: ABISUN
                - Password Hotspot: bantucpr
            1. Pilih sesi: Dewasa, Anak, atau Bayi.
            2. Mulai simulasi dengan menekan tombol di bawah.
            3. Lakukan simulasi RJP pada maneken selama 60 detik.
            4. Evaluasi performa RJP setelah simulasi telah selesai.
            """)
            self.start_button()
            check_connection = st.empty()
            while True:
                with check_connection.container():
                    self.check_connection()
                    time.sleep(5)
        else:
            if self.subject_session is "Bayi":
                self.model = load_model("../model/model_kedalaman_bayi.h5")
            else: 
                self.model = load_model("../model/model_kedalaman_dewasa_anak.h5")
            self.labels=[]
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

    def check_connection(self):
        try:
            response = requests.get(self.server_url)
            if response.status_code == 200:
                last_request_time = response.json().get("last_request_time")
                last_request_datetime = datetime.datetime.fromtimestamp(last_request_time)
                time_diff = datetime.datetime.now() - last_request_datetime
                if time_diff.total_seconds() < 5:  # Assume device is connected if the last request was within 5 seconds
                    st.success(f"Maneken sudah tersambung. Last request received {time_diff.seconds} seconds ago.")
                else:
                    st.error("Maneken belum tersambung.")
            else:
                st.error("Server gagal.")
        except Exception as e:
            st.error(f"Koneksi Error: {str(e)}")

    def show_live(self):
        live_placeholder = st.empty()
        with live_placeholder.container():
            st.header("Lakukan RJP pada Maneken!")
            self.live_chart("depth")
        live_placeholder.empty()

    def live_chart(self, col):
        text_placeholder=st.empty()
        chart_placeholder = st.empty()
        self.start_time = time.strftime("%Y-%m-%d %H:%M:%S")
        label_index = 4
        for i in range(60, -1 , -1):
            with text_placeholder.container():
                st.write(f"**{self.string_feedbacks[label_index]}**")
                st.write(f"Sisa {i} detik lagi!")
                print(self.labels)
                print(label_index)
            self.time_series = read_df_60_seconds(self.start_time)
            if i % 10 == 0 and i != 60:
                label_index = self.review_quality(self.time_series[['depth']].head(10))
                self.labels.append(label_index)
            chart_placeholder.plotly_chart(self.chart_builder('depth'))
            time.sleep(1)
        st.session_state['done'] = True

    def chart_builder(self, col):
        fig = px.line(self.time_series, x='timestamp', y=col, title="Data Kedalaman")
        fig.update_layout(xaxis_title='Waktu (detik)', 
                          yaxis_title='Kedalaman (cm)', 
                          modebar_remove=['select','zoom', 'pan'])
        return fig

    def review_quality(self,df):
        array = df.to_numpy().reshape(1,-1)
        array = self.scaler.transform(array).reshape(1,10,-1)
        y_pred = self.model.predict(array)
        y_pred_label = np.argmax(y_pred,axis=1)[0]
        return y_pred_label

    # DEPRECATED
    def split_dataframe(self, df):
        # Calculate the size of each part
        total_rows = 60
        part_size = total_rows // 3

        # Split the DataFrame into three parts based on the order
        df_part1 = df.iloc[:part_size]
        df_part2 = df.iloc[part_size:2*part_size]
        df_part3 = df.iloc[2*part_size:]

        def average_rows(df_part):
            avg_df = pd.DataFrame((df_part['depth'].values[::2] + df_part['depth'].values[1::2]) / 2)
            return avg_df

        df_part1_avg = self.scaler.transform(average_rows(df_part1))
        df_part2_avg = self.scaler.transform(average_rows(df_part2))
        df_part3_avg = self.scaler.transform(average_rows(df_part3))

        return df_part1_avg, df_part2_avg, df_part3_avg

    def result(self):
        result_placeholder = st.empty()
        with result_placeholder.container():
            st.subheader("Berikut adalah hasil CPR anda!")
            col1, col2, col3, col4, col5, col6= st.columns(6)
            with col1:
                st.write(f"**Detik 0-10**")
                st.write(self.string_predictions[self.labels[0]])
            with col2:
                st.write(f"**Detik 10-20**")
                st.write(self.string_predictions[self.labels[1]])
            with col3:
                st.write(f"**Detik 20-30**")
                st.write(self.string_predictions[self.labels[2]])
            with col4:
                st.write(f"**Detik 30-40**")
                st.write(self.string_predictions[self.labels[3]])
            with col5:
                st.write(f"**Detik 40-50**")
                st.write(self.string_predictions[self.labels[4]])
            with col6:
                st.write(f"**Detik 40-50**")
                st.write(self.string_predictions[self.labels[5]])

            chart_placeholder = st.empty()
            chart_placeholder.plotly_chart(self.chart_builder('depth'))
        if not st.session_state['done']:
            result_placeholder.empty()

if __name__ == "__main__":
    app = App()
    app.main()
