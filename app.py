from flask import Flask, render_template, request
import requests
import time

# Webアプリ作成
app = Flask(__name__) 

# エンドポイント設定（ルーティング）
@app.route('/')
def fetch_online_users():
    # live_idをクエリパラメータまたはPOSTデータから取得
    live_id = request.args.get('live_id', '') or request.form.get('liveid', '')

    if not live_id:
        return render_template("index.html", hour=False, minute=False, second=False, names=False, userides=False, error="Live ID is required.")
    else:
        url = f"https://www.mirrativ.com/api/live/online_users?live_id={live_id}&page=1"
        headers = {
            'User-Agent': 'MR_APP/10.45.3/Android/PIXEL 8/12',
        }
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            data = response.json()
            users = data.get('users', [])
            user_info = []
            
            for user in users:
                name = user.get('name', '').encode().decode('utf-8', 'ignore')  # 名前を取得
                user_id = user.get('user_id', '')  # user_idを取得
                user_info.append({'name': name, 'user_id': user_id})
                print(f'Name: {name}, User ID: {user_id}')
            
            # ユーザー情報を名前とuser_idで分けて辞書に格納
            names = {item['name']: item['name'] for item in user_info}
            userides = {item['name']: item['user_id'] for item in user_info}
            
            # 現在時刻を取得
            current_time = time.localtime()
            hour = current_time.tm_hour
            minute = current_time.tm_min
            second = current_time.tm_sec
            
            return render_template("index.html", hour=hour, minute=minute, second=second, names=names, userides=userides, error=None)
        else:
            return render_template("index.html", error="Failed to fetch online users. Please try again later.")

# POSTリクエストでlive_idを受け取る
@app.route("/liveid", methods=['POST'])
def liveid():
    live_id = request.form['liveid']
    print(f"[+] LiveId POST Success: {live_id}")
    # POSTされたlive_idを使って再度fetch_online_users関数に処理を行わせる
    return fetch_online_users()

if __name__ == '__main__': 
    app.run(debug=True)
