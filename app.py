import streamlit as st
from db import read_df  # Import the read_data function from db_utils

def main():
    st.title("ABISUN: Sensor Data Viewer")
    result()

def result():
    # Read data from the database
    df = read_df()

    if not df.empty:
        # Display the dataframe
        st.dataframe(df)

        # Display individual columns
        st.subheader("Accelerometer Data")
        st.line_chart(df[["mma_accel"]])

        st.subheader("Force Data")
        st.line_chart(df["fsr"])

        st.subheader("Depth Data")
        st.line_chart(df["depth"])
    else:
        st.write("No data available.")


if __name__ == "__main__":
    main()
