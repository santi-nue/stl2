import requests
import streamlit as st

state = st.session_state
if 'flask_started' not in state:
    state.flask_started = False

def start_flask():
    if state.flask_started:
        return

    import os, sys, time
    import subprocess
    import threading

    def _run(job):
        print (f'\nRunning job: {job}\n')
        proc = subprocess.Popen(job)
        proc.wait()
        return proc

    job = [f'{sys.executable}', os.path.join('.', 'flask_runner.py'), 'localhost', '8888']

    # server thread will remain active as long as streamlit thread is running, or is manually shutdown
    thread = threading.Thread(name='Flask Server', target=_run, args=(job,), daemon=False)
    thread.start()

    time.sleep(5)
    state.flask_started = True

flask_message = st.empty()
x = st.slider('Pick a number')
st.write('You picked:', x)

start_flask()

if state.flask_started:
    resp = requests.get('http://localhost:8888/foo').text
    flask_message.write(resp)
