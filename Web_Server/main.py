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

def respond_url_query(url):
    info = get_info.get_info(url)
    print("retrieving")
    data = info[1].to_frame().T
    property_name = info[0]
    analytical_data = convert_raw_data.get_AnalyticalData(data)
    print("converting to analytical_data")
    text_to_render = convert_to_json.convert_to_json(analytical_data,predictor.get_pred,property_name)
    print("converting to json")
    return render_template('visualization.html',title=property_name,message="ここにグラフを表示します",data=text_to_render)


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
    if request.method == 'POST':
        # リクエストフォームから「名前」を取得して
        url = request.form['name']
        # index.html をレンダリングする
        try:
            return respond_url_query(url)
        except:
            return render_template('index.html', message="(エラー)URLを入力してください", title="サーバー―エラー")
    else:
        # エラーなどでリダイレクトしたい場合はこんな感じで
        return redirect(url_for('index'))
        
#@app.route('/get_pred0')
#def get_pred0():
    

@app.route('/bar_chart')
def bar_chart():
	return render_template('bar_chart.html')

if __name__ == '__main__':
    app.debug = True # デバッグモード有効化
    app.run(host='0.0.0.0') # どこからでもアクセス可能に

