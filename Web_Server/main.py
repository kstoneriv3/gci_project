# Flask などの必要なライブラリをインポートする
from flask import Flask, render_template, request, redirect, url_for
import pandas as pd

# ソースコードのインポート
import predictor
import convert_raw_data
import convert_raw_data
import convert_to_json
import get_info
import data_box

raw_data = data_box.raw_data
analytical_data = convert_raw_data.get_AnalyticalData(raw_data)

# 自身の名称を app という名前でインスタンス化する
app = Flask(__name__)

# メッセージをランダムに表示するメソッド

# ここからウェブアプリケーション用のルーティングを記述
# index にアクセスしたときの処理
@app.route('/')
def index():
    title = "ようこそ"
    message = "URLを入力してください"
    # index.html をレンダリングする
    return render_template('index.html', message=message, title=title)

# /post にアクセスしたときの処理
@app.route('/post', methods=['GET', 'POST'])
def post():
    title = "こんにちは!"
    if request.method == 'POST':
        # リクエストフォームから「名前」を取得して
        name = request.form['name']
        # index.html をレンダリングする
        return render_template('index.html', name=name, title=title)
    else:
        # エラーなどでリダイレクトしたい場合はこんな感じで
        return redirect(url_for('index'))

@app.route('/get_pred0')
def get_pred0():
	text_to_render = convert_to_json.convert_to_json(analytical_data,predictor.get_pred)
	return text_to_render

@app.route('/bar_chart')
def bar_chart():
	return render_template('bar_chart.html')

if __name__ == '__main__':
    app.debug = True # デバッグモード有効化
    app.run(host='0.0.0.0') # どこからでもアクセス可能に
    