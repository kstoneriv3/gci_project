import pandas as pd
import numpy as np
from sqlalchemy import create_engine
import math

import predictor

# データベースの情報
server = 'gciteam16.database.windows.net'
database = 'mynavi-database'
username = 'gciteam16'
password = 'Password0'
port =1433

# 接続エンジンの作成
engine_config = "?driver=ODBC+Driver+13+for+SQL+Server?charset=shift-jis"
db_settings = {
    "host": server,
    "database": database,
    "user": username,
    "password": password,
    "port":port,
    "config_query":engine_config
}
engine = create_engine('mssql+pyodbc://{user}:{password}@{host}:{port}/{database}{config_query}'.format(**db_settings))

#緯度・経度のスケール
lat_mean =  35.64
lat_500m = (90/10000)*(1/math.cos(math.pi*lat_mean/180))*0.500
lng_500m = (90/10000)*0.500

def get_RegionalData(DF_analytical_data):
	arg_dict = {
	    "lat_500m" : lat_500m
	    ,"lng_500m" : lng_500m
	    ,"sup_lat" : list(DF_analytical_data.address_lat)[0] + lat_500m
	    ,"inf_lat" : list(DF_analytical_data.address_lat)[0] - lat_500m
	    ,"sup_lng" : list(DF_analytical_data.address_lng)[0] + lng_500m
	    ,"inf_lng" : list(DF_analytical_data.address_lng)[0] - lng_500m
	    ,"DF_analytical_data_lat" : list(DF_analytical_data.address_lat)[0]
	    ,"DF_analytical_data_lng" : list(DF_analytical_data.address_lng)[0]
	}
	query = """
	    SELECT * FROM 
	        (
	        SELECT * FROM analytical_data_table 
	            WHERE 
	                (address_lat < {sup_lat}) 
	                and (address_lat > {inf_lat})
	                and (address_lng < {sup_lng})
	                and (address_lng > {inf_lng}) 
	        ) as Sub_Table
	        WHERE 
	            SQUARE((Sub_Table.address_lat-{DF_analytical_data_lat})/{lat_500m})
	            + SQUARE((Sub_Table.address_lng-{DF_analytical_data_lng})/{lng_500m}) 
	            < 1
	    ;
	    """.format(**arg_dict)
	try:
		regional_data = pd.read_sql(query, con=engine)
	except:
		engine = create_engine('mssql+pyodbc://{user}:{password}@{host}:{port}/{database}{config_query}'.format(**db_settings))
		regional_data = pd.read_sql(query, con=engine)
	return regional_data

def get_df_new_created(regional_data):
	df_new = regional_data[["url","rent","area","address_lat","address_lng","year_built"]]
	df_new.columns = ["URL","価格(家賃)","床面積","緯度","経度","築年"]
	return df_new

def get_Prediction_added(df_new,regional_data,get_pred):
	y_pred_regional=[get_pred(row.to_frame().T) for i,row in regional_data.iterrows()]
	df_new["予測価格"] = y_pred_regional
	df_new["割引率(％)"] = round((1-regional_data.rent/y_pred_regional)*1000)/10
	return df_new

station_names = pd.Index(["千歳船橋駅"     ,"八幡山駅"       ,"千歳烏山駅"     ,"芦花公園駅" 
    ,"桜新町駅"       ,"駒沢大学駅"     ,"世田谷駅"       ,"用賀駅"     
    ,"二子玉川駅"     ,"祖師ケ谷大蔵駅"  ,"桜上水駅"       ,"下高井戸駅" 
    ,"上北沢駅"       ,"松陰神社前駅"   ,"若林駅"         ,"久我山駅"   
    ,"吉祥寺駅"       ,"東松原駅"       ,"新代田駅"       ,"明大前駅"   
    ,"等々力駅"       ,"尾山台駅"       ,"自由が丘駅"     ,"豪徳寺駅"       
    ,"山下駅"         ,"宮の坂駅"       ,"成城学園前駅"    ,"三軒茶屋駅" 
    ,"西太子堂駅"      ,"笹塚駅"         ,"代田橋駅"       ,"下北沢駅"   
    ,"上町駅"         ,"経堂駅"         ,"松原駅"         ,"仙川駅"     
    ,"梅ケ丘駅"       ,"世田谷代田駅"    ,"池ノ上駅"       ,"上野毛駅"   
    ,"喜多見駅"       ,"学芸大学駅"     ,"祐天寺駅"       ,"池尻大橋駅" 
    ,"九品仏駅"       ,"春日駅"         ,"後楽園駅"       ,"本郷三丁目駅"
    ,"田端駅"         ,"千駄木駅"       ,"本駒込駅"       ,"護国寺駅"   
    ,"江戸川橋駅"     ,"茗荷谷駅"       ,"千石駅"         ,"巣鴨駅"     
    ,"神楽坂駅"       ,"飯田橋駅"       ,"駒込駅"         ,"新大塚駅"   
    ,"西日暮里駅"     ,"御茶ノ水駅"     ,"新御茶ノ水駅"    ,"白山駅"     
    ,"東大前駅"       ,"根津駅"         ,"水道橋駅"       ,"湯島駅"     
    ,"御徒町駅"       ,"上野御徒町駅"    ,"大塚駅"         ,"向原駅"     
    ,"東池袋駅"       ,"日暮里駅"       ,"早稲田駅"       ,"秋葉原駅"   
    ,"池袋駅"         ,"末広町駅"       ,"上野広小路駅"    ,"快速日暮里駅"    
    ,"牛込神楽坂駅"    ,"雑司が谷駅"     ,"鬼子母神前駅"    ,"目白駅"     
    ,"東池袋四丁目駅"  ,"上野駅"         ,"都電雑司ケ谷駅"  ,"鶯谷駅"     
    ,"上中里駅"       ,"京成上野駅"     ,"西ケ原駅"       ,"高田馬場駅" 
    ,"快速上野駅"     ,"田園調布駅"     ,"奥沢駅"         ,"狛江駅"     
    ,"緑が丘駅"       ,"大岡山駅"       ,"雪が谷大塚駅"    ,"牛込柳町駅" 
    ,"西巣鴨駅"       ,"面影橋駅"       ,"仲御徒町駅"     ,"浅草橋駅"   
    ,"蔵前駅"         ,"新御徒町駅"     ,"三ノ輪駅"       ,"入谷駅"     
    ,"馬喰町駅"       ,"南千住駅"       ,"三ノ輪橋駅"     ,"淡路町駅"   
    ,"小伝馬町駅"     ,"稲荷町駅"       ,"快速三河島駅"    ,"浅草駅"     
    ,"田原町駅"       ,"快速南千住駅"    ,"東日本橋駅"     ,"岩本町駅"   
    ,"両国駅"         ,"曳舟駅"         ,"本所吾妻橋駅"    ,"とうきょうスカイツリー駅"    
    ,"馬喰横山駅"     ,"東向島駅"        ,"押上駅"        ,"千住大橋駅" 
    ,"荒川一中前駅"    ,"北千住駅"       ,"人形町駅"       ,"浜町駅"     
    ,"東北沢駅"       ,"代々木上原駅"    ,"二子新地駅"     ,"目黒駅"      
    ,"五反田駅"       ,"恵比寿駅"       ,"不動前駅"       ,"白金台駅" 
    ,"洗足駅"         ,"北千束駅"       ,"西小山駅"       ,"駒場東大前駅"
    ,"中目黒駅"       ,"都立大学駅"     ,"武蔵小山駅"     ,"代官山駅"   
    ,"渋谷駅"         ,"神泉駅"         ,"つつじケ丘駅"    ,"多摩川駅"   
    ,"石川台駅"       ,"高津駅"         ,"三鷹台駅"       ,"富士見ケ丘駅"
    ,"幡ケ谷駅"       ,"西永福駅"       ,"高井戸駅"       ,"永福町駅"   
    ,"新宿駅"         ,"御嶽山駅"       ,"浜田山駅"       ,"和泉多摩川駅"
    ,"代々木駅"       ,"千駄ケ谷駅"     ,"北参道駅"       ,"南新宿駅"   
    ,"広尾駅"         ,"新宿三丁目駅"    ,"初台駅"         ,"西新宿五丁目駅"
    ,"原宿駅"         ,"明治神宮前駅"    ,"代々木公園駅"    ,"代々木八幡駅"
    ,"参宮橋駅"       ,"中野新橋駅"     ,"方南町駅"       ,"表参道駅"   
    ,"中野坂上駅"     ,"都庁前駅"       ,"外苑前駅"       ,"中野富士見町駅"
    ,"信濃町駅"       ,"白金高輪駅"     ,"国立競技場駅"    ,"西新宿駅"   
    ,"椎名町駅"       ,"要町駅"         ,"北池袋駅"       ,"板橋駅"     
    ,"東長崎駅"       ,"千川駅"         ,"小竹向原駅"     ,"下板橋駅"   
    ,"落合南長崎駅"    ,"巣鴨新田駅"     ,"大山駅"         ,"庚申塚駅"   
    ,"新板橋駅"       ,"新江古田駅"     ,"中井駅"         ,"新庚申塚駅" 
    ,"江古田駅"       ,"下落合駅"       ,"学習院下駅"     ,"西ケ原四丁目駅"
    ,"板橋区役所前駅"    ,"東中野駅"      ,"王子駅"         ,"蓮根駅"     
    ,"浮間舟渡駅"     ,"西台駅"         ,"下赤塚駅"       ,"地下鉄赤塚駅"
    ,"平和台駅"       ,"志村坂上駅"     ,"本蓮沼駅"       ,"志村三丁目駅"
    ,"北赤羽駅"   ,"西早稲田駅"         ,"新井薬師前駅"    ,"滝野川一丁目駅"
    ,"新三河島駅"     ,"尾久駅"         ,"赤羽駅"         ,"赤羽岩淵駅" 
    ,"十条駅"         ,"板橋本町駅"     ,"志茂駅"         ,"東十条駅"   
    ,"王子神谷駅"     ,"梶原駅"         ,"栄町駅"         ,"赤土小学校前駅"
    ,"小台駅"         ,"宮ノ前駅"       ,"荒川遊園地前駅"    ,"飛鳥山駅"   
    ,"荒川車庫前駅"    ,"戸田公園駅"     ,"西新井駅"       ,"熊野前駅"   
    ,"新桜台駅"       ,"上板橋駅"       ,"東武練馬駅"     ,"氷川台駅"   
    ,"高島平駅"       ,"ときわ台駅"     ,"成増駅"         ,"地下鉄成増駅"
    ,"新高島平駅"     ,"中板橋駅"       ,"和光市駅"       ,"西高島平駅" 
    ,"光が丘駅"       ,"練馬春日町駅"    ,"豊島園駅"       ,"上石神井駅" 
    ,"西荻窪駅"       ,"武蔵関駅"       ,"練馬駅"         ,"桜台駅"     
    ,"練馬高野台駅"    ,"富士見台駅"     ,"石神井公園駅"    ,"荻窪駅"     
    ,"中村橋駅"       ,"鷺ノ宮駅"       ,"東伏見駅"       ,"野方駅"     
    ,"都立家政駅"     ,"大泉学園駅"      ,"井荻駅"         ,"保谷駅"     
    ,"西武柳沢駅"     ,"上井草駅"       ,"朝霞駅"         ,"下井草駅"   
    ,"沼袋駅"         ,"高円寺駅"       ,"三鷹駅"         ,"ひばりケ丘駅"   
    ,"中野駅"         ,"井の頭公園駅"    ,"阿佐ケ谷駅" ])

get_min_inverse_to_station = lambda row_of_regional_data: row_of_regional_data[148:435].max()
get_min_to_station = lambda row_of_regional_data:round(1.0/get_min_inverse_to_station(row_of_regional_data)) if get_min_inverse_to_station(row_of_regional_data)<=1 else 0
get_min_station = lambda row_of_regional_data: list(station_names[get_min_inverse_to_station(row_of_regional_data)==row_of_regional_data[148:435]])[0]

def get_StationDist_added(df_new,regional_data):
	df_new["最寄駅"] = pd.Series([get_min_station(row) for i,row in regional_data.iterrows()])
	df_new["最寄駅への所要時間"] = pd.Series([get_min_to_station(row) for i,row in regional_data.iterrows()])
	return df_new

#離散変数の処理
def get_RoomInfo_added(df_new,regional_data):
	def get_room_structure(row):
	    get_row_by = lambda colname:list(row[regional_data.columns==colname])[0]
	    txt = ''
	    txt += str(get_row_by("the_number_of_rooms"))
	    txt += 'L' if get_row_by("has_L") else ''
	    txt += 'D' if get_row_by("has_D") else ''
	    txt += 'K' if get_row_by("has_K") else ''
	    return txt
	df_new["間取り"] = pd.Series([get_room_structure(row) for i,row in regional_data.iterrows()])
	return df_new
def get_Direction_added(df_new,regional_data):
	def get_direction(row):
	    get_row_by = lambda colname:list(row[regional_data.columns==colname])[0]
	    if get_row_by("direction_1"): return '北'
	    if get_row_by("direction_2"): return '北東'
	    if get_row_by("direction_3"): return '東'
	    if get_row_by("direction_4"): return '南東'
	    if get_row_by("direction_5"): return '南'
	    if get_row_by("direction_6"): return '南西'
	    if get_row_by("direction_7"): return '西'
	    if get_row_by("direction_8"): return '北西'
	    else: return "方角不明"
	df_new["方角"] = pd.Series([ get_direction(row) for i,row in regional_data.iterrows()])
	return df_new

def get_Structure_sdded(df_new,regional_data):
	def get_structure(row):
	    get_row_by = lambda colname:list(row[regional_data.columns==colname])[0]
	    if get_row_by("structure_1"): return 'コンクリート'
	    if get_row_by("structure_2"): return 'コンクリート'
	    if get_row_by("structure_3"): return 'コンクリート'
	    if get_row_by("structure_4"): return 'コンクリート'
	    if get_row_by("structure_5"): return 'コンクリート'
	    if get_row_by("structure_7"): return '鉄骨'
	    if get_row_by("structure_8"): return '鉄骨'
	    if get_row_by("structure_9"): return '鉄骨'
	    if get_row_by("structure_10"): return '木造'
	    else: return 'その他'
	df_new["建物構造"] = pd.Series([ get_structure(row) for i,row in regional_data.iterrows()])
	return df_new

def get_StoveNum_added(df_new,regional_data):
	def get_stove_num(row):
	    get_row_by = lambda colname:list(row[regional_data.columns==colname])[0]
	    if get_row_by("isNull_stove_num"): return 'コンロ口数不明'
	    else: return get_row_by("stove_num_Null_to_Zero")
	df_new["コンロ口数"] = pd.Series([get_stove_num(row) for i,row in regional_data.iterrows()])
	return df_new

def get_Miscellaneous_added(df_new,regional_data):
	df_new["浴室乾燥機"] = regional_data.bath_drier_Null_to_Zero.apply(lambda TF:'浴室乾燥機あり' if TF else '浴室乾燥機なし')
	df_new["オートロック"] = regional_data.auto_lock.apply(lambda TF:'オートロックあり' if TF else 'オートロックなし')
	df_new["フローリング"] = regional_data.flooring.apply(lambda TF:'フローリング〇' if TF else 'フローリング×')
	return df_new

def get_PropertyTag_added(df_new,regional_data,DF_analytical_data,property_name):
	tag_property = lambda TF:property_name if TF else "周囲の物件 (500m県内) "
	df_new["選択物件"] = (regional_data.url==list(DF_analytical_data.url)[0]).apply(tag_property)
	return df_new

def render_txt(df_new): 

	txt_to_render = ""
	IF_start = True

	for i,row in df_new.iterrows():
	    get_row_by = lambda colname:list(row[df_new.columns==colname])[0]
	    if IF_start==False:
	        txt_to_render += ",\n"
	    txt_to_render += "{"
	    IF_start = False
	    if_start = True
	    for colname in df_new.columns:
	        if if_start==False:
	            txt_to_render += ","
	        if_start = False
	        txt_to_render += "\"{colname}\":\"{value}\"".format(colname=colname,value=get_row_by(colname))
	    txt_to_render += "}"

	txt_to_render = "[\n" + txt_to_render + "\n]"

	return txt_to_render

def convert_to_json(DF_analytical_data,get_pred,property_name):
	regional_data = get_RegionalData(DF_analytical_data)
	df_new = get_df_new_created(regional_data)
	df_new = get_Prediction_added(df_new,regional_data,get_pred)
	df_new = get_StationDist_added(df_new,regional_data)
	df_new = get_RoomInfo_added(df_new,regional_data)
	df_new = get_Structure_sdded(df_new,regional_data)
	df_new = get_Direction_added(df_new,regional_data)
	df_new = get_StoveNum_added(df_new,regional_data)
	df_new = get_Miscellaneous_added(df_new,regional_data)
	df_new = get_PropertyTag_added(df_new,regional_data,DF_analytical_data,property_name)
	df_new["count"] = 1
	return render_txt(df_new)