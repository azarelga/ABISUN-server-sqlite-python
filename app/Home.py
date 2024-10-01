import base64
import time
from statistics import mode

import yaml
import joblib
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st
from keras.models import load_model

from db import (  # Import the read_data function from db_utils
    has_recent_entry,
    read_df,
    read_df_60_seconds,
)


class Home:
    def __init__(self):
        self.model = None
        self.scaler = joblib.load("../model/scaler.gz")
        self.df = read_df()
        if "running" not in st.session_state:
            st.session_state["running"] = False
        if "done" not in st.session_state:
            st.session_state["done"] = False
        if "show_modal" not in st.session_state:
            st.session_state["show_modal"] = False
        self.time_series = pd.DataFrame()
        self.start_time = time.strftime("%Y-%m-%d %H:%M:%S")
        self.subject_session = "Dewasa"
        with open("../assets/texts.yaml", "r") as file:
            self.texts = yaml.safe_load(file)
        self.labels = []
        self.text_colors = ["green", "red", "red", "red", "green"]
        # st.sidebar.header("ABISUN")
        st.set_page_config(
            page_title="ABISUN App",
            page_icon="chart_with_upwards_trend",
        )
        st.markdown(
            """
            <style>
            [aria-label="close"]{
                all: unset;
                background: none;
            }
            [aria-label="dialog"]{
                width: 60%;
                background-color: black;
            }
            .buruk {
                color: red;
            }
            .baik {
                color: green;
            }
            </style>
            """,
            unsafe_allow_html=True,
        )

    def main(self):
        if not st.session_state["running"]:
            self.home_page()
        else:
            self.run_simulation()

    def home_page(self):
        # Halaman utama
        st.markdown(
            "<h1 style='text-align: center;'>Selamat Datang pada Simulasi RJP: ABISUN!</h1>",
            unsafe_allow_html=True,
        )
        st.header("Step by Step Simulasi")
        st.write(self.texts["step_by_step"])
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
        if st.session_state["running"]:
            self.autoplay_audio("../assets/metronome.mp3")
        countdown_placeholder = st.empty()
        for i in range(5, 0, -1):
            countdown_placeholder.text(
                f"Siap - siap! Simulasi CPR akan dimulai dalam {i} detik..."
            )
            time.sleep(1)
        countdown_placeholder.empty()  # Clear countdown after starting

        self.show_live()  # Function to show live simulation data
        self.result()  # Function to show results after simulation

        st.subheader("Mulai lagi?")
        if st.button("Balik ke Halaman Utama", type="secondary"):
            st.session_state["running"] = False
            st.session_state["done"] = False
            st.session_state["show_modal"] = False
            st.rerun()

    def set_page(self):
        st.session_state["running"] = True
        st.session_state["show_modal"] = False
        st.rerun()

    def start_button(self):
        # Store button clicks in session state to persist the state across reruns
        self.subject_session = st.selectbox("Pilih Sesi", ["Dewasa", "Anak", "Bayi"])
        if st.button("Lanjutkan", type="secondary", use_container_width=True):
            st.session_state["show_modal"] = True

        if st.session_state["show_modal"]:
            self.start_modal()

    def start_modal(self):
        st.write(self.texts["dialog_message"][self.subject_session])
        if st.button("Mulai Simulasi", type="primary", use_container_width=True):
            self.set_page()

    def autoplay_audio(self, file_path: str):
        with open(file_path, "rb") as f:
            data = f.read()

        b64 = base64.b64encode(data).decode()

        # First time: Play the audio and then pause it after a specific time
        md = f"""
            <audio id="audio-player" controls autoplay style='display:none;'>
                <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
            </audio>
            """

        st.markdown(md, unsafe_allow_html=True)

    def check_connection(self):
        try:
            if has_recent_entry():
                st.success("Maneken sudah tersambung")
            else:
                st.error("Maneken belum tersambung.")
        except Exception as e:
            st.error(f"Koneksi Error: {str(e)}")

    def show_live(self):
        live_placeholder = st.empty()
        with live_placeholder.container():
            st.header("Lakukan RJP pada Maneken!")
            self.live_chart("depth")
        live_placeholder.empty()

    def live_chart(self, col):
        text_placeholder = st.empty()
        chart_placeholder = st.empty()
        self.start_time = time.strftime("%Y-%m-%d %H:%M:%S")
        label_index = 4
        for i in range(60, -1, -1):
            with text_placeholder.container():
                st.markdown(
                    f"<h3 style='color:{self.text_colors[label_index]}';>{self.texts['string_feedbacks'][label_index]}</h3>",
                    unsafe_allow_html=True,
                )
                st.subheader(f"Sisa {i} detik lagi!")
                print(self.labels)
                print(label_index)
            self.time_series = read_df_60_seconds(self.start_time)
            if i % 10 == 0 and i != 60:
                if len(self.time_series) < 10:
                    depth_mode = self.time_series["depth"].mode()
                    for i in range(10 - len(self.time_series)):
                        additional_rows = pd.DataFrame(
                            {
                                "timestamp": time.time(),
                                "depth": depth_mode,
                            }
                        )
                        self.time_series = pd.concat(
                            [self.time_series, additional_rows], ignore_index=True
                        )
                label_index = self.review_quality(self.time_series[["depth"]].tail(10))
                self.labels.append(label_index)
            chart_placeholder.plotly_chart(self.chart_builder("depth"))
            time.sleep(1)
        st.session_state["done"] = True

    def debug_chart(self):
        st.write(self.time_series.tail(1)[["timestamp", "depth"]])

    def chart_builder(self, col):
        fig = px.line(self.time_series, x="timestamp", y=col, title="Data Kedalaman")
        fig.update_layout(
            xaxis_title=dict(text="Waktu (detik)", font=dict(size=20)),
            yaxis_title=dict(text="Kedalaman (cm)", font=dict(size=20)),
            yaxis=dict(tickfont=dict(size=20)),
            xaxis=dict(tickfont=dict(size=20)),
            modebar_remove=["select", "zoom", "pan"],
        )
        threshold = [[4, 5], [3.8, 4.2]]
        if self.subject_session != "Bayi":
            fig.add_hline(y=threshold[0][0], line_dash="dash", line_color="lightgreen")
            fig.add_hline(y=threshold[0][1], line_dash="dash", line_color="lightgreen")
            fig.add_hrect(
                y0=threshold[0][0], y1=threshold[0][1], fillcolor="green", opacity=0.3
            )
        else:
            fig.add_hline(y=threshold[1][0], line_dash="dash", line_color="lightgreen")
            fig.add_hline(y=threshold[1][1], line_dash="dash", line_color="lightgreen")
            fig.add_hrect(
                y0=threshold[1][0], y1=threshold[1][1], fillcolor="green", opacity=0.3
            )
        return fig

    def review_quality(self, df):
        array = df.to_numpy().reshape(1, -1)
        array = self.scaler.transform(array).reshape(1, 10, -1)
        y_pred = self.model.predict(array)
        y_pred_label = np.argmax(y_pred, axis=1)[0]
        return y_pred_label

    def show_quality(self, label_index):
        st.subheader(f"**Detik {label_index*10}-{(label_index+1)*10}**")
        label = self.labels[label_index]
        st.markdown(
            f"<h3 style='color:{self.text_colors[label]}';>{self.texts['string_predictions'][label]}</h3>",
            unsafe_allow_html=True,
        )

    def result(self):
        st.session_state["running"] = False
        result_placeholder = st.empty()
        # self.time_series["local_max"] = self.time_series.iloc[
        #     argrelextrema(self.time_series["depth"].values, np.greater_equal, order=1)[
        #         0
        #     ]
        # ]["depth"]
        # self.time_series["local_min"] = self.time_series.iloc[
        #     argrelextrema(self.time_series["depth"].values, np.less_equal, order=1)[0]
        # ]["depth"]
        # num_local_maxima = self.time_series["local_max"].count()
        # num_local_minima = self.time_series["local_min"].count()

        with result_placeholder.container():
            st.header("Berikut adalah hasil CPR anda!")
            overall_quality = mode(self.labels)
            # compression = (num_local_minima + num_local_maxima) // 2
            # st.markdown( f"<h2>Jumlah kompresimu: <span style='color : {'red' if compression > 120 or compression < 100 else 'green'};'>{compression}</span></h2>", unsafe_allow_html=True)
            st.markdown(
                f"<h2>Kualitas RJP-mu secara garis besar: <span style='color : {self.text_colors[overall_quality]};'>{self.texts['string_predictions'][overall_quality]}</span></h2>",
                unsafe_allow_html=True,
            )
            col1, col2, col3, col4, col5, col6 = st.columns(6)
            with col1:
                self.show_quality(0)
            with col2:
                self.show_quality(1)
            with col3:
                self.show_quality(2)
            with col4:
                self.show_quality(3)
            with col5:
                self.show_quality(4)
            with col6:
                self.show_quality(5)
            chart_placeholder = st.empty()
            chart_placeholder.plotly_chart(self.chart_builder("depth"))
        if not st.session_state["done"]:
            result_placeholder.empty()


if __name__ == "__main__":
    home = Home()
    home.main()
