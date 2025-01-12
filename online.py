from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import requests
import json
import time
import threading

app = Flask(__name__)
socketio = SocketIO(app)

# スレッドとフラグを管理するための変数
threads = {}
stop_flags = {}

def fetch_online_users(live_id, stop_flag):
    while not stop_flag.is_set():
        url = f"https://www.mirrativ.com/api/live/online_users?live_id={live_id}&page=1"
        headers = {
            'User-Agent': 'MR_APP/10.45.3/Android/PIXEL 8/12',
        }
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            data = response.json()
            users = data.get('users', [])
            user_info = [{'name': user.get('name', '').encode().decode('utf-8', 'ignore'), 'user_id': user.get('user_id', '')} for user in users]
            
            # Get current time in hours, minutes, and seconds
            current_time = time.localtime()
            hour = current_time.tm_hour
            minute = current_time.tm_min
            second = current_time.tm_sec

            socketio.emit('update_users', {'time': f"{hour}時{minute}分{second}秒", 'users': user_info})
        else:
            socketio.emit('update_users', {'error': f"Error: {response.status_code}"})

        time.sleep(5)

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('start_fetching')
def start_fetching(data):
    live_id = data['live_id']
    
    # 既存のスレッドを停止
    if live_id in stop_flags:
        stop_flags[live_id].set()
        threads[live_id].join()
    
    # 新しいスレッドを開始
    stop_flag = threading.Event()
    stop_flags[live_id] = stop_flag
    thread = threading.Thread(target=fetch_online_users, args=(live_id, stop_flag))
    threads[live_id] = thread
    thread.start()

@socketio.on('stop_fetching')
def stop_fetching(data):
    live_id = data['live_id']
    if live_id in stop_flags:
        stop_flags[live_id].set()
        threads[live_id].join()
        del stop_flags[live_id]
        del threads[live_id]

if __name__ == '__main__':
    socketio.run(app,host="0.0.0.0", debug=True)
