import streamlit as st
from db_utils import read_data  # Import the read_data function from db_utils


def main():
    st.title("Sensor Data Viewer")

    # Read data from the database
    df = read_data()

    if not df.empty:
        st.write("Data Types:", df.dtypes)
        st.write("First 5 Rows:", df.head())

        # Display the dataframe
        st.dataframe(df)

        # Display individual columns
        st.subheader("Accelerometer Data")
        st.line_chart(df[["accel_x", "accel_y", "accel_z"]])

        st.subheader("Force Data")
        st.line_chart(df["force"])
    else:
        st.write("No data available.")


if __name__ == "__main__":
    main()
