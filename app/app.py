import streamlit as st
import base64
import numpy as np
import plotly.express as px
import pandas as pd
import requests
from statistics import mode
import joblib
import time
from scipy.signal import argrelextrema
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
        self.text_colors = ['green','red', 'red', 'red','green']
        st.set_page_config(
            page_title="ABISUN App",
            page_icon="chart_with_upwards_trend",
        )
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
        self.server_url = f"http://abisun-server.local:5000/last-request-time"  # Replace with your server URL

    def main(self):
        if st.session_state['running'] == False:
            self.home_page()
        else:
            self.run_simulation()

    def home_page(self):
        # Halaman utama
        st.markdown("<h1 style='text-align: center;'>Selamat Datang pada Simulasi RJP: ABISUN!</h1>", unsafe_allow_html=True)
        st.header("Tata Cara CPR yang Benar")
        st.write("""
        1. Pastikan area aman untuk Anda dan subjek RJP.
        2. Lakukan kompresi dada:
            - Tempatkan tumit salah satu tangan di tengah dada korban, tepat di antara puting susu.
            - Tempatkan tangan lainnya di atas tangan pertama dan kunci jari-jari Anda.
            - Tekan dada korban ke bawah setidaknya 4 cm untuk orang dewasa dan anak-anak, dan 3 cm untuk bayi.
            - Lakukan kompresi dengan kecepatan 100-120 kali per menit.
        """)

        st.header("Step by Step Simulasi")
        st.write("""
        0. Buatlah hotspot dari Handphone anda dengan detail sebagai berikut, pastikan laptop anda juga sudah terhubung:
            - Nama Hotspot: ABISUN
            - Password Hotspot: bantucpr
        1. Pilih sesi: Dewasa, Anak, atau Bayi.
        2. Mulai simulasi dengan menekan tombol "Mulai Simulasi" di bawah.
        3. Lakukan simulasi RJP pada maneken selama 60 detik. Irama RJP diselaraskan dengan irama metronome yang dimainkan!
        4. Evaluasi performa RJP setelah simulasi telah selesai.
        """)
        self.start_button()
        check_connection = st.empty()
        while True:
            with check_connection.container():
                self.check_connection()
                time.sleep(5)

    def run_simulation(self):
        # Load the appropriate model based on session type
        if self.subject_session == "Bayi":
            self.model = load_model("../model/model_kedalaman_bayi.h5")
        else:
            self.model = load_model("../model/model_kedalaman_dewasa_anak.h5")

        self.labels = []
        self.time_series = self.time_series.iloc[0:0]

        # Countdown before starting the simulation
        self.autoplay_audio("../assets/metronome.mp3")
        countdown_placeholder = st.empty()
        for i in range(5, 0, -1):
            countdown_placeholder.text(f"Siap - siap! Simulasi CPR akan dimulai dalam {i} detik...")
            time.sleep(1)
        countdown_placeholder.empty()  # Clear countdown after starting

        self.show_live()  # Function to show live simulation data
        self.result()  # Function to show results after simulation

        st.subheader("Mulai lagi?")
        self.start_button()

    def set_page(self):
        st.session_state['running'] = True

    def start_button(self):
        self.subject_session = st.selectbox("Pilih Sesi", ["Dewasa", "Anak", "Bayi"])
        st.button("Mulai Simulasi", 
                  type='primary',
                  use_container_width=True, 
                  on_click=self.set_page()
                  )

    def autoplay_audio(self,file_path: str):
        with open(file_path, "rb") as f:
            data = f.read()
            b64 = base64.b64encode(data).decode()
            md = f"""
                <audio controls autoplay="true" style='display:none;'>
                <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
                </audio>
                """
            st.markdown(
                md,
                unsafe_allow_html=True,
            )


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
                st.markdown(f"<h3 style='color:{self.text_colors[label_index]}';>{self.string_feedbacks[label_index]}</h3>",
                            unsafe_allow_html=True)
                st.subheader(f"Sisa {i} detik lagi!")
                print(self.labels)
                print(label_index)
            self.time_series = read_df_60_seconds(self.start_time)
            if i % 10 == 0 and i != 60:
                if (len(self.time_series) < 10):
                    depth_mode = self.time_series['depth'].mode()
                    for i in range (10 - len(self.time_series)):
                        additional_rows = pd.DataFrame({
                                            'timestamp': time.time(),
                                            'depth': depth_mode,
                                        })
                        self.time_series = pd.concat([self.time_series, additional_rows], ignore_index=True)
                label_index = self.review_quality(self.time_series[['depth']].tail(10))
                self.labels.append(label_index)
            #chart_placeholder.plotly_chart(self.chart_builder('depth'))
            with chart_placeholder.container():
                self.debug_chart()
            time.sleep(1)
        st.session_state['done'] = True

    def debug_chart(self):
        st.write(self.time_series.tail(1)[['timestamp','depth']])

    def chart_builder(self, col):
        fig = px.line(self.time_series, x='timestamp', y=col, title="Data Kedalaman")
        fig.update_layout(xaxis_title='Waktu (detik)', 
                          yaxis_title='Kedalaman (cm)', 
                          modebar_remove=['select','zoom', 'pan'])
        threshold = [[3.5,5.5],[2.5,4.5]]
        if self.subject_session != "Bayi":
            fig.add_hline(y=threshold[0][0],line_dash="dash", line_color="lightgreen")
            fig.add_hline(y=threshold[0][1],line_dash="dash", line_color="lightgreen")
            fig.add_hrect(
                y0=threshold[0][0],
                y1=threshold[0][1],
                fillcolor="green", 
                opacity=0.3
            )
        else:
            fig.add_hline(y=threshold[1][0],line_dash="dash", line_color="lightgreen")
            fig.add_hline(y=threshold[1][1],line_dash="dash", line_color="lightgreen")
            fig.add_hrect(
                y0=threshold[1][0],
                y1=threshold[1][1],
                fillcolor="green", 
                opacity=0.3
            )
        return fig

    def review_quality(self,df):
        array = df.to_numpy().reshape(1,-1)
        array = self.scaler.transform(array).reshape(1,10,-1)
        y_pred = self.model.predict(array)
        y_pred_label = np.argmax(y_pred,axis=1)[0]
        return y_pred_label

    def result(self):
        result_placeholder = st.empty()
        self.time_series['local_max'] = self.time_series.iloc[argrelextrema(self.time_series['depth'].values, np.greater_equal, order=1)[0]]['depth']
        self.time_series['local_min'] = self.time_series.iloc[argrelextrema(self.time_series['depth'].values, np.less_equal, order=1)[0]]['depth']
        num_local_maxima = self.time_series['local_max'].count()
        num_local_minima = self.time_series['local_min'].count()

        with result_placeholder.container():
            st.header("Berikut adalah hasil CPR anda!")
            overall_quality = mode(self.labels)
            compression = (num_local_minima + num_local_maxima) // 2
            st.markdown(
                f"<h2>Jumlah kompresimu: <span style='color : {'red' if compression > 120 or compression < 100 else 'green'};'>{compression}</span></h2>", 
                unsafe_allow_html=True)
            st.markdown(
                f"<h2>Kualitas RJP-mu secara garis besar: <span style='color : {self.text_colors[overall_quality]};'>{self.string_predictions[overall_quality]}</span></h2>", 
                unsafe_allow_html=True)
            col1, col2, col3, col4, col5, col6= st.columns(6)
            with col1:
                st.subheader(f"**Detik 0-10**")
                st.markdown(
                    f"<p style='color : {self.text_colors[self.labels[0]]}';>{self.string_predictions[self.labels[0]]}</p>",
                    unsafe_allow_html=True
                )
            with col2:
                st.subheader(f"**Detik 10-20**")
                st.markdown(
                    f"<p style='color : {self.text_colors[self.labels[1]]}';>{self.string_predictions[self.labels[1]]}</p>",
                    unsafe_allow_html=True
                )
            with col3:
                st.subheader(f"**Detik 20-30**")
                st.markdown(
                    f"<p style='color : {self.text_colors[self.labels[2]]}';>{self.string_predictions[self.labels[2]]}</p>",
                    unsafe_allow_html=True
                )
            with col4:
                st.subheader(f"**Detik 30-40**")
                st.markdown(
                    f"<p style='color : {self.text_colors[self.labels[3]]}';>{self.string_predictions[self.labels[3]]}</p>",
                    unsafe_allow_html=True
                )
            with col5:
                st.subheader(f"**Detik 40-50**")
                st.markdown(
                    f"<p style='color : {self.text_colors[self.labels[4]]}';>{self.string_predictions[self.labels[4]]}</p>",
                    unsafe_allow_html=True
                )
            with col6:
                st.subheader(f"**Detik 50-60**")
                st.markdown(
                    f"<p style='color : {self.text_colors[self.labels[5]]}';>{self.string_predictions[self.labels[5]]}</p>",
                    unsafe_allow_html=True
                )
            chart_placeholder = st.empty()
            chart_placeholder.plotly_chart(self.chart_builder('depth'))
        if not st.session_state['done']:
            result_placeholder.empty()

if __name__ == "__main__":
    app = App()
    app.main()
