import pandas as pd
import numpy as np
import math
import re
import urllib
from xml.etree import ElementTree as ET

def convert_type(data):
    for col in cols_to_convert_type:
        data[col] = data[col].apply(lambda x:float(x))

def get_Geocode_Added(data):
	serviceurl = 'http://maps.googleapis.com/maps/api/geocode/xml?'

	address = data.address[0].encode("utf-8")
	url = serviceurl + urllib.parse.urlencode({u'sensor':u'false', u'address': address})
	#print ('Retrieving', url)
	uh = urllib.request.urlopen(url)
	text = uh.read()
	tree = ET.fromstring(text)

	if tree.findall("status")[0].text!='OK':
	    print("Geocoding Failed.")
	    return None
	results = tree.findall('result')
	lat = float( results[0].find('geometry').find('location').find('lat').text )
	lng = float( results[0].find('geometry').find('location').find('lng').text )
	location = results[0].find('formatted_address').text

	data["address_lat"] = pd.Series([lat])
	data["address_lng"] = pd.Series([lng])
	return data

# <h3>築年数（築年）の取得
def get_YearBuild_Added(data):
	get_year_build = lambda date:int(re.findall("([0-9]+)年[0-9]+月",date)[0]) if len( re.findall("([0-9]+)年[0-9]+月",date) )>0 else None
	data["year_built"] = data.date.apply(get_year_build)
	# 築年のないログ
	if sum( data.year_built.apply(math.isnan) )!=0:
		return None
	return data

#近所の施設⽬での距離を取得

facilities = ['幼稚園・保育園', '小学校', '学校', 'コンビニ', 'スーパー', '郵便局', '図書館',
       'ドラッグストア', '飲食店', '銀行', '総合病院', '病院', '公園', '大学', 'レンタルビデオ',
       'クリーニング', 'デパート']
new_colnames_F = ['kindergarten', 'elementary_school', 'school', 'convenient_store', 'super_market', 'post_office', 'library',
       'drug_store', 'restaurant', 'bank', 'general_hospital', 'hospital', 'park', 'university', 'rental_video',
       'cleaning_shop', 'department_store']

#施設までの距離を取得する関数
get_distance = lambda facility, text: int(re.findall("【"+facility+"】\S+?\(([0-9]+)m",text)[0]) if len(re.findall("【"+facility+"】\S+?\(([0-9]+)m",text))==1 else None

def get_FacilityDist_Added(data):
	#施設までの距離を持った新しいデータフレーム作成
	df_new = pd.DataFrame(index=data.index, columns=new_colnames_F)	
	#数字を実際に取得して埋める
	for facility,colname in zip(facilities, new_colnames_F):
	    get_distance_fac = lambda text: get_distance(facility, text)
	    df_new[colname][data.surroundings.isnull()==False] = data[data.surroundings.isnull()==False].surroundings.apply(get_distance_fac)
	#横結合で、元のデータフレームを拡張
	data = pd.concat([data, df_new], axis=1)
	return data

#間取り情報の抽出

#情報を抽出する関数
has_K = lambda text: len(re.findall("K",text))>0
has_L = lambda text: len(re.findall("L",text))>0
has_D = lambda text: len(re.findall("D",text))>0
has_S = lambda text: len(re.findall("S",text))>0
get_Num_Rooms = lambda text: int(re.findall("[0-9]+",text)[0])

#追加したいカラム名
new_colnames_RI = ["has_K","has_L","has_D","has_S","the_number_of_rooms"]

def get_RoomInfo_Added(data):
	#間取りの情報を持った新しいデータフレーム作成
	df_new = pd.DataFrame(index=data.index, columns=new_colnames_RI)
	#数字を実際に取得して埋める
	df_new["has_K"][data.layout.isnull()==False] = data[data.layout.isnull()==False].layout.apply(has_K)
	df_new["has_L"][data.layout.isnull()==False] = data[data.layout.isnull()==False].layout.apply(has_L)
	df_new["has_D"][data.layout.isnull()==False] = data[data.layout.isnull()==False].layout.apply(has_D)
	df_new["has_S"][data.layout.isnull()==False] = data[data.layout.isnull()==False].layout.apply(has_S)
	df_new["the_number_of_rooms"][data.layout.isnull()==False] = data[data.layout.isnull()==False].layout.apply(get_Num_Rooms)
	#横結合で、元のデータフレームを拡張
	data = pd.concat([data, df_new], axis=1)
	return data


# 欠損値にフラグを⽴てて、使えるデータに変換

#欠損してる説明変数一覧：
null_colnames = pd.Series([
 "locality"         ,"buildings_height"    ,"buildings_undergrand" ,"total_units"
,"balcony"          ,"shower"              ,"bath_drier"           ,"washlet"
,"toilet_style"     ,"bathhouse"           ,"water_heater"         ,"system_kitchen"
,"counter_kitchen"  ,"independent_kitchen" ,"L_kitchen"            ,"refrigerator" 
,"gas_stove"        ,"IH_stove"            ,"electric_stove"       ,"stove_num"
,"office"           ,"instrument"          ,"togather"             ,"share"
,"foreigner"        ,"pet"                 ,"male"                 ,"female"
, "kindergarten"    ,"elementary_school"   ,"school"               ,"convenient_store"
,"super_market"     ,"post_office"         ,"library"              ,"drug_store"
,"restaurant"       ,"bank"                ,"general_hospital"     ,"hospital"
,"park"             ,"university"          ,"rental_video"         ,"cleaning_shop"
,"department_store" ,"the_number_of_rooms" ,"year_built"
])

#欠損地にフラグを立ててカラムを追加
def get_NullFixed(data):
    data["isNull_" + null_colnames] = data[null_colnames].isnull()
    data[null_colnames + "_Null_to_Zero"] = data[null_colnames].fillna(0)
    data = data.apply(lambda col:col.apply(lambda x:0 if x=='' else x),axis=1)
    return data

#最寄駅情報の抽出

# 駅名と徒歩何分かを取得する関数
remove_bracket = lambda text :re.sub(u'\(.+?\)','',re.sub(u'（.+?）', '',re.sub(u'「」', '',text))) 
remove_question_mark = lambda text :re.sub(u'\?','',text)
remove_noise = lambda text:remove_bracket(remove_question_mark(text))
remove_dot = lambda text :re.sub(u'・.+?線','',text)#"・中央線東京駅"みたいなのを除く

get_station_info_0 = lambda text: (
    re.findall(u"線(\S+?駅).*?徒歩([0-9]+?)分", remove_noise(text)) 
    + re.findall(u"ライン(\S+?駅).*?徒歩([0-9]+?)分", remove_noise(text)) 
    + re.findall(u"ライナー(\S+?駅).*?徒歩([0-9]+?)分", remove_noise(text))
)

get_station_info_1 = lambda text:[(re.sub(u"「",u"",st_tuple[0]),st_tuple[1]) for st_tuple in get_station_info_0(text)]
get_station_info = lambda text:{remove_dot(t[0]):int(t[1]) for t in get_station_info_1(text)} if len(get_station_info_1(text)) > 0 else {}
get_station_name = lambda text:[remove_dot(t[0]) for t in get_station_info_1(text)] if len(get_station_info_1(text)) > 0 else []

station_names = pd.Series(["千歳船橋駅"     ,"八幡山駅"       ,"千歳烏山駅"     ,"芦花公園駅" 
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

# 駅ごとにそれらを求める関数(徒歩0分の場合は、inverse:=2とした)
get_inverse_dist_to_st = lambda arg_dict, st_name : (1.0/arg_dict[st_name] if arg_dict[st_name]!=0 else 2) if st_name in arg_dict.keys() else 0

def get_StationDist_added(data):
	station_info = data.traffic.apply(get_station_info)
	# 近くの駅までの所要時間の逆数のデータフレーム（説明変数に使う）
	df_new = pd.DataFrame(index=data.index, columns=station_names).astype(np.float)
	for st_name in station_names:
	    this_st = st_name
	    get_inverse_dist_to_this_st = lambda arg_dict: get_inverse_dist_to_st(arg_dict ,this_st)
	    df_new[st_name] = station_info.apply(get_inverse_dist_to_this_st)
	#横結合で、元のデータフレームを拡張
	data = pd.concat([data, df_new], axis=1)
	return data

#分析用データの作成

analytical_columns = [
    "url"         ,"rent"         ,"area"        ,"flooring"    ,"year_built"
    ,"parking"     ,"structure"   ,"air_conditioner","auto_lock"
    ,"bath_toilet" ,"reheating"   ,"wash_basin"  ,"washing_machine"
    ,"top_floor"   ,"corner_room" ,"immediate"   ,"upper"
    ,"direction_1" ,"direction_2" ,"direction_3" ,"direction_4"
    ,"direction_5" ,"direction_6" ,"direction_7" ,"direction_8"
    ,"structure_1" ,"structure_2" ,"structure_3" ,"structure_4"
    ,"structure_5" ,"structure_6" ,"structure_7" ,"structure_8"
    ,"structure_9" ,"structure_10","structure_11"
    ,"status_1"    ,"status_2"    ,"status_3"    ,"status_4"    
    ,"transaction_type_1","transaction_type_2","transaction_type_3"
    ,"transaction_type_4","transaction_type_5","transaction_type_6"
    ,"bath_style_0","bath_style_1","bath_style_2"
    ,"address_lat" ,"address_lng"
    ,"has_K"       ,"has_L"       ,"has_D"       ,"has_S"
    ,"the_number_of_rooms"
    
    ,"isNull_locality"            ,"isNull_buildings_height"
    ,"isNull_buildings_undergrand","isNull_total_units"
    ,"isNull_balcony"             ,"isNull_shower"
    ,"isNull_bath_drier"          ,"isNull_washlet"
    ,"isNull_toilet_style"        ,"isNull_bathhouse"
    ,"isNull_water_heater"        ,"isNull_system_kitchen"
    ,"isNull_counter_kitchen"     ,"isNull_independent_kitchen"
    ,"isNull_L_kitchen"           ,"isNull_refrigerator"
    ,"isNull_gas_stove"           ,"isNull_IH_stove"
    ,"isNull_electric_stove"     ,"isNull_stove_num"
    ,"isNull_office"              ,"isNull_instrument"
    ,"isNull_togather"            ,"isNull_share"
    ,"isNull_foreigner"           ,"isNull_pet"
    ,"isNull_male"                ,"isNull_female"
    ,"isNull_kindergarten"        ,"isNull_elementary_school"
    ,"isNull_school"              ,"isNull_convenient_store"
    ,"isNull_super_market"        ,"isNull_post_office"
    ,"isNull_library"             ,"isNull_drug_store"
    ,"isNull_restaurant"          ,"isNull_bank"
    ,"isNull_general_hospital"    ,"isNull_hospital"
    ,"isNull_park"                ,"isNull_university"
    ,"isNull_rental_video"        ,"isNull_cleaning_shop"
    ,"isNull_department_store"    ,"isNull_the_number_of_rooms"
   
    ,"locality_Null_to_Zero"      ,"buildings_height_Null_to_Zero"
    ,"buildings_undergrand_Null_to_Zero"    ,"total_units_Null_to_Zero"
    ,"balcony_Null_to_Zero"       ,"shower_Null_to_Zero"
    ,"bath_drier_Null_to_Zero"    ,"washlet_Null_to_Zero"
    ,"toilet_style_Null_to_Zero"  ,"bathhouse_Null_to_Zero"
    ,"water_heater_Null_to_Zero"  ,"system_kitchen_Null_to_Zero"
    ,"counter_kitchen_Null_to_Zero"    ,"independent_kitchen_Null_to_Zero"
    ,"L_kitchen_Null_to_Zero"     ,"refrigerator_Null_to_Zero"
    ,"gas_stove_Null_to_Zero"     ,"IH_stove_Null_to_Zero"
    ,"electric_stove_Null_to_Zero","stove_num_Null_to_Zero"
    ,"office_Null_to_Zero"        ,"instrument_Null_to_Zero"
    ,"togather_Null_to_Zero"      ,"share_Null_to_Zero"
    ,"foreigner_Null_to_Zero"     ,"pet_Null_to_Zero"
    ,"female_Null_to_Zero"        ,"kindergarten_Null_to_Zero"
    ,"elementary_school_Null_to_Zero"    ,"school_Null_to_Zero"
    ,"convenient_store_Null_to_Zero"    ,"super_market_Null_to_Zero"
    ,"post_office_Null_to_Zero"   ,"library_Null_to_Zero"
    ,"drug_store_Null_to_Zero"    ,"restaurant_Null_to_Zero"
    ,"bank_Null_to_Zero"          ,"general_hospital_Null_to_Zero"
    ,"hospital_Null_to_Zero"    ,"park_Null_to_Zero"
    ,"university_Null_to_Zero"    ,"rental_video_Null_to_Zero"
    ,"cleaning_shop_Null_to_Zero" ,"department_store_Null_to_Zero"
    ,"the_number_of_rooms_Null_to_Zero"

    ,"千歳船橋駅"     ,"八幡山駅"       ,"千歳烏山駅"     ,"芦花公園駅" 
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
    ,"中野駅"         ,"井の頭公園駅"    ,"阿佐ケ谷駅" 
]

def get_AnalyticalData(data):
    data = get_Geocode_Added(data)
    data = get_YearBuild_Added(data)
    data = get_FacilityDist_Added(data)
    data = get_RoomInfo_Added(data)
    data = get_NullFixed(data)
    data = get_StationDist_added(data)
    data["index"] = pd.Series([0])
    data = data[["index"]+analytical_columns]
    return data