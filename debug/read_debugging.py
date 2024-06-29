from db_utils import read_data  # Import the read_data function from db_utils
import time


def main():
    try:
        while True:
            read_data()  # Read and display data from the table
            time.sleep(0.5)  # Wait for 5 seconds before reading again
    except KeyboardInterrupt:
        print("Exiting the program.")


if __name__ == "__main__":
    main()
