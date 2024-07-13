import streamlit as st
import numpy as np
import plotly.graph_objs as go
import pandas as pd
import time
import datetime
from db import read_df, read_df_60_seconds # Import the read_data function from db_utils

class App:
    def __init__(self):
        st.title("ABISUN: Sensor Data Viewer")
        self.df = read_df()
        if 'running' not in st.session_state:
            st.session_state['running'] = False
        if 'done' not in st.session_state:
            st.session_state['done'] = False
        self.time_series = read_df_60_seconds()
        self.subject_session = "Dewasa"

    def main(self):
        if not st.session_state['running']:
            self.start_button()
        else:
            countdown_placeholder = st.empty()
            for i in range(5, 0, -1):
                countdown_placeholder.text(f"Get Ready! Starting in {i} seconds...")
                time.sleep(1)
            countdown_placeholder.empty()  # Clear countdown after starting
            self.show_live()
            if st.session_state['done']:
                self.result()

    def start_button(self):
        self.subject_session = st.selectbox("Select Session", ["Dewasa", "Bayi"])
        if st.button("Start", type='primary'):
            st.session_state['running'] = True
            st.empty()

    def show_live(self):
        st.subheader("Depth Value")
        self.live_chart("depth")

    def live_chart(self, col):
        chart_placeholder = st.empty()
        for _ in range(60):
            self.time_series = read_df_60_seconds()
            fig = go.Figure(data=[go.Scatter(x=self.time_series['id'], y=self.time_series[col], mode='lines')])
            chart_placeholder.plotly_chart(fig)
            time.sleep(1)
        st.session_state['done'] = True

    def result(self):
        if not self.df.empty:
            # Display the dataframe
            st.dataframe(self.df)

            # Display individual columns
            st.subheader("Accelerometer Data")
            st.line_chart(self.df[["mma_accel"]])

            st.subheader("Force Data")
            st.line_chart(self.df["fsr"])

            st.subheader("Depth Data")
            st.line_chart(self.df["depth"])
        else:
            st.write("No data available.")

if __name__ == "__main__":
    app = App()
    app.main()
