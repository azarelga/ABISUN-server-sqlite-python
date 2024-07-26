import threading
import os
import time
def streamlit_app():
    os.system("streamlit run app.py")
def start_flask_app():
    os.system("python3.10 server.py")
t1 = threading.Thread(target=streamlit_app)
t2 = threading.Thread(target=start_flask_app)
t1.start()
t2.start()
