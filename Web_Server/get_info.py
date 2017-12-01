from bs4 import BeautifulSoup
import requests
import re
import pandas as pd
from pandas import Series

def get_info(url):
    # url = 'https://chintai.mynavi.jp/tokyo/113/room121700007311.html'
    response = requests.get(url)
    soup = BeautifulSoup(response.content,'lxml')


    a = soup.select("dt") #基本データ項目取得
    b = soup.select("dd") #基本データ内容取得
    c = soup.select("#setsubi tr > th") #設備詳細データ項目取得
    d = soup.select("#setsubi tr > td") #設備詳細データ内容取得
    e = soup.select("#bukken tr > th") #物件情報詳細データ項目取得
    f = soup.select("#bukken tr > td") #物件情報詳細データ内容取得
    g = soup.select("#nyukyo tr > th") #入居条件詳細データ項目取得
    h = soup.select("#nyukyo tr > td") #入居条件詳細データ内容取得
    i = soup.select("td > ul > li") #こだわり条件取得、0~9に情報が格納
    j = soup.select("#top > div.wr_layout > div.mt20.search_name_area.clear-fix > h1") #物件名



    def shaping_datas(datas):
        ret = [0 for i in range(len(datas))]
        for i in range(len(datas)):
            ret[i] = str(datas[i])
            ret[i] = re.sub("<.*?>","",ret[i])
        return ret



    def conv_str(datas): 
        ret = [0 for i in range(len(datas))]
        for i in range(len(datas)):
            ret[i] = str(datas[i])
        return ret


    def modify_detail(detail):
        ret = ['' for i in range(10)]
        for i in range(10):
            if ('li class="cu"' in detail[i]):
                ret[i] = '1'
            else:
                ret[i] = '0'
        return ret


    def del_id(datas):
        for i in range(len(datas)):
            if("物件ID" in datas[i]):
                del datas[i]
        return datas


    basic_menu = shaping_datas(a)[:9]
    basic_contents = shaping_datas(b)[:9]
    detail_menu = shaping_datas(c)[1:] + shaping_datas(e) + shaping_datas(g)
    detail_contents = shaping_datas(d)[1:] + del_id(shaping_datas(f)) + shaping_datas(h)
    detail_tag_menu = shaping_datas(i)[0:10]
    detail_tag_contents = modify_detail(conv_str(i))
    building_name = shaping_datas(j)



    menu = basic_menu + detail_menu
    contents = basic_contents + detail_contents 


#     for i in range(len(menu)):
#         print(menu[i],contents[i])


    menu[3] = re.sub("地図を見る","",menu[3])


    def sorting(menu,contents):
        index = ['' for i in range(39)]
        ret = ['' for i in range(39)]
        item_list = [
             '交通',#0
             '所在地',#1
             '賃料(管理費・共益費)',#2
             '敷金 (保証金)',#3
             '間取り',#4
             '面積',#5
             '方角',#6
             '築年数',#7
             '備考',#8
             '建物構造',#9
             '所在階/階数',#10
             '間取り詳細',#11
             '駐車場',#12
             '物件ID',#13
             '引渡',#14
             '現況',#15
             '取引態様',#16
             '住宅保険',#17
             '保証会社',#18
             '更新料',#19
             '償却・敷引',#20
             '敷金積増し',#21
             '契約期間',#22
             '仲介手数料',#23
             '権利金',#24
             'バルコニー面積',#25
             '総戸数',#26
             '周辺環境',#27
             'その他費用',#28
             'その他月額費用',#29
             '保証人代行',#30
             'リフォーム',#31
             '位置・方角',#32
             'バス・トイレ',#33
             '設備/サービス',#34
             '入居条件',#35
             'その他',#36
             '礼金 (敷引・償却金)',#37
             'キッチン'#38
             ]
        for i in range(len(menu)):
            try:
                index[i] = item_list.index(menu[i])
            except:
                pass

        for i in range(len(index)):
            if isinstance(index[i], str):
                index[i] = 0

            if len(ret[index[i]]) == 0:
                ret[index[i]] = contents[i]
        return ret


    # In[12]:

    sort = ['' for i in range(39)]
    sort = sorting(menu, contents)


    # In[13]:

    item_list = [
         '交通',#0
         '所在地',#1
         '賃料(管理費・共益費)',#2
         '敷金 (保証金)',#3
         '間取り',#4
         '面積',#5
         '方角',#6
         '築年数',#7
         '備考',#8
         '建物構造',#9
         '所在階/階数',#10
         '間取り詳細',#11
         '駐車場',#12
         '物件ID',#13
         '引渡',#14
         '現況',#15
         '取引態様',#16
         '住宅保険',#17
         '保証会社',#18
         '更新料',#19
         '償却・敷引',#20
         '敷金積増し',#21
         '契約期間',#22
         '仲介手数料',#23
         '権利金',#24
         'バルコニー面積',#25
         '総戸数',#26
         '周辺環境',#27
         'その他費用',#28
         'その他月額費用',#29
         '保証人代行',#30
         'リフォーム',#31
         '位置・方角',#32
         'バス・トイレ',#33
         '設備/サービス',#34
         '入居条件',#35
         'その他',#36
         '礼金 (敷引・償却金)',#37
         'キッチン'#38
         ]


    item_dict = {
        "address":sort[1],
        "air_conditioner":detail_tag_contents[4],
        "area":sort[5],
        "auto_lock":detail_tag_contents[5],
        "balcony":sort[25],
        "bath":sort[33],
        "bath_toilet":detail_tag_contents[0],
        "brokerage_fee":sort[23],
        "date":sort[7],
        "deposit":sort[3],
        "depreciation":sort[20],
        "direction":sort[6],
        "facility":sort[34],
        "flooring":detail_tag_contents[8],
        "guarantee":sort[18],
        "guarantor":sort[30],
        "handover":sort[14],
        "id":sort[13],
        "insurance":sort[17],
        "key_money":sort[37],
        "kitchen":sort[38],
        "layout":sort[4],
        "layout_detail":sort[11],
        "locality":sort[10],
        "location":sort[32],
        "name":building_name,
        "other":sort[36],
        "other_expence":sort[28],
        "other_monthlyexpence":sort[29],
        "parking":detail_tag_contents[7],
        "parking_detail":sort[12],
        "period":sort[22],
        "premium":sort[21],
        "qualification":sort[35],
        "reform":sort[31],
        "reheating":detail_tag_contents[1],
        "remark":sort[8],
        "renewal_fee":sort[19],
        "rent":sort[2],
        "right_money":sort[24],
        # "south":detail_tag_contents[2],
        "status":sort[15],
        "structure":sort[9],
        "surroundings":sort[27],
        "total_units":sort[26],
        "traffic":sort[0],
        "transaction_type":sort[16],
        "upper":detail_tag_contents[6],
        "url":url,
        "wash_basin":detail_tag_contents[9],
        "washing_machine":detail_tag_contents[3]
    }


    def delete(char, item):
        if item.find(char) > -1:
            item = ''
            item = re.sub(char,"",item)
        return item

    def dum(char, item):
        ret = 0
        if (char in item):
            ret = 1
        return ret

    def dum2(char1,char2,char3,item):
        ret = ''
        if(char1 in item):
            ret = 2
        elif(char2 in item):
            ret = 1
        elif(char3 in item):
            ret = 0
        else:
            pass
        return ret

    def dum3(char1,char2,item):
        ret = ''
        if(char1 in item):
            ret = 1
        elif(char2 in item):
            ret = 0
        else:
            pass
        return ret

    def dum4(char, item):
        ret = ''
        if(char in item):
            ret = 1
        else:
            ret = 0
        return ret
        
    def dum_mul(chars, item):
        ret = ''
        for i in range(len(chars)):
            if (chars[i] in item):
                ret = i
                break
        return ret

    def del_yen(item):
        ret = re.sub("\,","",item)
        ret = re.sub("円","",item)
        return ret

    def convert_yen(rent,item):
        ret = item
        if('円' in item):
            ret = re.sub(",","",item)
            ret = re.sub("円","",item)
        elif('ヶ月' in item):
            ret = re.sub("ヶ月","",item)
            ret = int(ret) * int(rent)
        return ret



    #単位除去・テーブル分割

    item_dict["area"] = re.sub("m2","",item_dict["area"])
    item_dict["balcony"] = re.sub("m2","",item_dict["balcony"])
    item_dict["total_units"] = re.sub("戸","",item_dict["total_units"])

    loca2= item_dict["locality"].split('／')
    loca3= ""

    flag = False
    if ('(' in loca2[1]):
        loca4= loca2[1].split('(')
        flag = True

    item_dict["locality"] = re.sub("階","",loca2[0])
    if (flag == True):
        loca4[1] = re.sub("地下","",loca4[1])
        loca4[1] = re.sub("階）","",loca4[1])
        loca4[1] = loca3

    item_dict.update({"buildings_height":re.sub("階建","",loca2[1]),
                      "buildings_undergrand":loca3,
                      "top_floor":dum("最上階",item_dict["location"]),
                      "corner_room":dum("角部屋",item_dict["location"]),
                     })
    del item_dict["location"]
    item_dict.update({"immediate":dum("即入居可",item_dict["other"])})
    del item_dict["other"]

    direction_list = ['dummy_data','北','北東','東','南東','南','南西','西','北西']
    stove_list = ['dummy_data','コンロ1口','コンロ2口','コンロ3口']
    bath_style_list = ['バス無し','共同バス','専用バス']
    structure_list = ['dummy_data',
                      'ALC（軽量気泡コンクリート）',
                      'HPC（プレキャスト・コンクリート（重量鉄骨））',
                      'PC（プレキャスト・コンクリート（鉄筋コンクリート））',
                      'RC（鉄筋コンクリート）',
                      'SRC（鉄骨鉄筋コンクリート）',
                      'ブロック',
                      'PC（プレキャスト・コンクリート（鉄筋コンクリート））',
                      'RC（鉄筋コンクリート）',
                      'SRC（鉄骨鉄筋コンクリート）',
                      'ブロック',
                      '軽量鉄骨',
                      '鉄筋ブロック',
                      '鉄骨造',
                      '木造',
                      'その他',
                     ]
    status_list = ['dummy_data','居住中','空室','新築・未完成','賃貸中']
    transaction_list = ['dummy,data','一般媒介','専属専任媒介','専任媒介','貸主','代理','仲介']


    item_dict.update({"shower":dum("シャワー",item_dict["bath"]),
                      "bath_drier":dum("浴室乾燥機",item_dict["bath"]),
                      "washlet":dum("温水洗浄便座",item_dict["bath"]),
                      "bathhouse":dum("脱衣所",item_dict["bath"]),
                      "toilet_style":dum("専用トイレ",item_dict["bath"]),
                      "water_heater":dum("給湯",item_dict["kitchen"]),
                      "system_kitchen":dum("システムキッチン",item_dict["kitchen"]),
                      "counter_kitchen":dum("カウンターキッチン",item_dict["kitchen"]),
                      "independent_kitchen":dum("独立キッチン",item_dict["kitchen"]),
                      "L_kitchen":dum("L字キッチン",item_dict["kitchen"]),
                      "refrigerator":dum("冷蔵庫あり",item_dict["kitchen"]),
                      "gas_stove":dum("ガスコンロ",item_dict["kitchen"]),
                      "IH_stove":dum("IHコンロ",item_dict["kitchen"]),
                      "electric_stove":dum("電気コンロ",item_dict["kitchen"]),
                      "elderly":dum2("高齢者限定","高齢者歓迎","高齢者不可",item_dict["qualification"]),
                      "company":dum2("法人限定","法人希望","法人不可",item_dict["qualification"]),
                      "single":dum2("単身者限定","単身者希望","単身者不可",item_dict["qualification"]),
                      "student":dum2("学生限定","学生歓迎","学生不可",item_dict["qualification"]),
                      "company":dum2("法人限定","法人歓迎","法人不可",item_dict["qualification"]),
                      "office":dum3("事務所利用可","事務所利用不可",item_dict["qualification"]),
                      "instrument":dum3("楽器可","楽器不可",item_dict["qualification"]),
                      "togather":dum3("二人入居可","二人入居不可",item_dict["qualification"]),
                      "share":dum3("ルームシェア可","ルームシェア不可",item_dict["qualification"]),
                      "foreigner":dum3("外国人入居可","外国人入居不可",item_dict["qualification"]),
                      "pet":dum3("ペット可","ペット不可",item_dict["qualification"]),
                      "male":dum4("男性限定",item_dict["qualification"]),
                      "female":dum4("女性限定",item_dict["qualification"]),
                      "direction":dum_mul(direction_list,item_dict["direction"]),
                      "stove_num":dum_mul(stove_list,item_dict["kitchen"]),
                      "bath_style":dum_mul(bath_style_list,item_dict["bath"]),
                      "structure":dum_mul(structure_list,item_dict["structure"]),
                      "status":dum_mul(status_list,item_dict["status"]),
                      "transaction_type":dum_mul(transaction_list,item_dict["transaction_type"]),    
                     })
    del item_dict["qualification"]
    del item_dict["kitchen"]
    del item_dict["bath"]
    del item_dict["handover"]
    del item_dict["period"]


    rent_split= item_dict["rent"].split('（')
    rent = rent_split[0]
    rent = re.sub(",","",rent)
    administration_fee = rent_split[1]
    administration_fee = re.sub("）","",rent)
    rent = del_yen(rent)
    rent2 = rent
    administration_fee = del_yen(administration_fee)
    rent = float(rent)/10000
    rent = round(rent,1)
    item_dict.update({"rent":rent,"administration_fee":administration_fee})

    deposit = re.sub("/\(.*?\)/","",item_dict["deposit"])
    key_money = re.sub("\(.*?\)","",item_dict["key_money"])


    if("要／" in item_dict["insurance"]):
        item_dict["insurance"] = re.sub("要／","",item_dict["insurance"])
        item_dict["insurance"] = re.sub("円","",item_dict["insurance"])
        item_dict["insurance"] = re.sub(",","",item_dict["insurance"])
        



    def convert_dummies(dummy_list,num):
        ret = [0 for i in range(len(dummy_list))]
        for i in range(len(dummy_list)):
            ret[i] = 0
            if(num == i):
                ret[i] = 1
        return ret


    def convert_dummies2(dummy_list,num):
        ret = [0 for i in range(len(dummy_list)+1)]
        for i in range(1,len(dummy_list)+1):
            ret[i] = 0
            if(num == i):
                ret[i] = 1
        return ret[1:]


    def write_dummy(dummy_list,num,dic):
        for i in range(len(dummy_list)):
            dic.update({dummy_list[i]:num[i]})
        return dic


    dum_elderly = ["elderly_0","elderly_1","elderly_2"]
    dum_company = ["company_0","company_1","company_2"]
    dum_single = ["single_0","single_1","single_2"]
    dum_student = ["student_0","student_1","student_2"]
    dum_direction = ["direction_1","direction_2","direction_3","direction_4","direction_5","direction_6","direction_7","direction_8"]
    dum_structure = ["structure_1","structure_2","structure_3","structure_4","structure_5","structure_6","structure_7","structure_8","structure_9","structure_10","structure_11"]
    dum_status = ["status_1","status_2","status_3","status_4"]
    dum_transaction_type = ["transaction_type_1","transaction_type_2","transaction_type_3","transaction_type_4","transaction_type_5","transaction_type_6"]
    dum_bath_style = ["bath_style_0","bath_style_1","bath_style_2"]
    item_dict = write_dummy(dum_elderly,convert_dummies(dum_elderly,item_dict["elderly"]),item_dict)
    item_dict = write_dummy(dum_company,convert_dummies(dum_company,item_dict["company"]),item_dict)
    item_dict = write_dummy(dum_single,convert_dummies(dum_single,item_dict["single"]),item_dict)
    item_dict = write_dummy(dum_student,convert_dummies(dum_student,item_dict["student"]),item_dict)
    item_dict = write_dummy(dum_direction,convert_dummies2(dum_direction,item_dict["direction"]),item_dict)
    item_dict = write_dummy(dum_structure,convert_dummies2(dum_structure,item_dict["structure"]),item_dict)
    item_dict = write_dummy(dum_status,convert_dummies2(dum_status,item_dict["status"]),item_dict)
    item_dict = write_dummy(dum_transaction_type,convert_dummies2(dum_transaction_type,item_dict["transaction_type"]),item_dict)
    item_dict = write_dummy(dum_bath_style,convert_dummies(dum_bath_style,item_dict["bath_style"]),item_dict)

    del item_dict["elderly"]
    del item_dict["company"]
    del item_dict["single"]
    del item_dict["student"]
    del item_dict["direction"]
    # del item_dict["structure"]
    # del item_dict["status"]
    # del item_dict["transaction_type"]
    del item_dict["bath_style"]






    brokerage_fee = convert_yen(rent2, item_dict["brokerage_fee"])
    brokerage_fee = re.sub("\（.*?\）","",brokerage_fee)
    brokerage_fee = re.sub(",","",brokerage_fee)

    depreciation = convert_yen(rent2, item_dict["depreciation"])
    depreciation = re.sub("\（.*?\）","",depreciation)
    depreciation = re.sub(",","",depreciation)


    item_dict.update({"deposit":convert_yen(rent2, deposit),
                      "key_money":convert_yen(rent2, key_money),
                      "brokerage_fee":convert_yen(rent2, brokerage_fee),
                      "depreciation":convert_yen(rent2, depreciation),
                      "insurance":convert_yen(rent2, item_dict["insurance"]),
                      "renewal_fee":convert_yen(rent2, item_dict["renewal_fee"]),
                     })



    series = Series([
    item_dict['traffic'],
    item_dict['address'],
    item_dict['rent'],
    item_dict['area'],
    item_dict['deposit'],
    item_dict['key_money'],
    item_dict['brokerage_fee'],
    item_dict['date'],
    item_dict['layout'],
    item_dict['layout_detail'],
    item_dict['depreciation'],
    item_dict['facility'],
    item_dict['flooring'],
    item_dict['guarantee'],
    item_dict['guarantor'],
    item_dict['insurance'],
    item_dict['renewal_fee'],
    item_dict['administration_fee'],
    item_dict['remark'],
    item_dict['locality'],
    item_dict['buildings_height'],
    item_dict['buildings_undergrand'],
    item_dict['surroundings'],
    item_dict['other_expence'],
    item_dict['parking'],
    item_dict['parking_detail'],
    item_dict['reform'],
    item_dict['total_units'],
    item_dict['status'],
    item_dict['structure'],
    item_dict['transaction_type'],
    item_dict['balcony'],
    item_dict['air_conditioner'],
    item_dict['auto_lock'],
    item_dict['bath_toilet'],
    item_dict['reheating'],
    # item_dict['south'],
    item_dict['wash_basin'],
    item_dict['washing_machine'],
    item_dict['top_floor'],
    item_dict['corner_room'],
    item_dict['immediate'],
    item_dict['upper'],
    item_dict['shower'],
    item_dict['bath_drier'],
    item_dict['washlet'],
    item_dict['toilet_style'],
    item_dict['bathhouse'],
    item_dict['water_heater'],
    item_dict['system_kitchen'],
    item_dict['counter_kitchen'],
    item_dict['independent_kitchen'],
    item_dict['L_kitchen'],
    item_dict['refrigerator'],
    item_dict['gas_stove'],
    item_dict['IH_stove'],
    item_dict['electric_stove'],
    item_dict['stove_num'],
    item_dict['office'],
    item_dict['instrument'],
    item_dict['togather'],
    item_dict['share'],
    item_dict['foreigner'],
    item_dict['pet'],#------------------------------
    item_dict['elderly_0'],
    item_dict['elderly_1'],
    item_dict['elderly_2'],
    item_dict['company_0'],
    item_dict['company_1'],
    item_dict['company_2'],
    item_dict['single_0'],
    item_dict['single_1'],
    item_dict['single_2'],
    item_dict['student_0'],
    item_dict['student_1'],
    item_dict['student_2'],
    item_dict['male'],
    item_dict['female'],
    item_dict['direction_1'],
    item_dict['direction_2'],
    item_dict['direction_3'],
    item_dict['direction_4'],
    item_dict['direction_5'],
    item_dict['direction_6'],
    item_dict['direction_7'],
    item_dict['direction_8'],
    item_dict['structure_1'],
    item_dict['structure_2'],
    item_dict['structure_3'],
    item_dict['structure_4'],
    item_dict['structure_5'],
    item_dict['structure_6'],
    item_dict['structure_7'],
    item_dict['structure_8'],
    item_dict['structure_9'],
    item_dict['structure_10'],
    item_dict['structure_11'],
    item_dict['status_1'],
    item_dict['status_2'],
    item_dict['status_3'],
    item_dict['status_4'],
    item_dict['transaction_type_1'],
    item_dict['transaction_type_2'],
    item_dict['transaction_type_3'],
    item_dict['transaction_type_4'],
    item_dict['transaction_type_5'],
    item_dict['transaction_type_6'],
    item_dict['bath_style_0'],
    item_dict['bath_style_1'],
    item_dict['bath_style_2'],
    item_dict['url'],
    # item_dict['name'],
    ]
    ,index = [
    'traffic',
    'address',
    'rent',
    'area',
    'deposit',
    'key_money',
    'brokerage_fee',
    'date',
    'layout',
    'layout_detail',
    'depreciation',
    'facility',
    'flooring',
    'guarantee',
    'guarantor',
    'insurance',
    'renewal_fee',
    'administration_fee',
    'remark',
    'locality',
    'buildings_height',
    'buildings_undergrand',
    'surroundings',
    'other_expence',
    'parking',
    'parking_detail',
    'reform',
    'status',
    'structure',
    'transaction_type',
    'total_units',
    'balcony',
    'air_conditioner',
    'auto_lock',
    'bath_toilet',
    'reheating',
    # 'south',
    'wash_basin',
    'washing_machine',
    'top_floor',
    'corner_room',
    'immediate',
    'upper',
    'shower',
    'bath_drier',
    'washlet',
    'toilet_style',
    'bathhouse',
    'water_heater',
    'system_kitchen',
    'counter_kitchen',
    'independent_kitchen',
    'L_kitchen',
    'refrigerator',
    'gas_stove',
    'IH_stove',
    'electric_stove',
    'stove_num',
    'office',
    'instrument',
    'togather',
    'share',
    'foreigner',
    'pet',
    'elderly_0',
    'elderly_1',
    'elderly_2',
    'company_0',
    'company_1',
    'company_2',
    'single_0',
    'single_1',
    'single_2',
    'student_0',
    'student_1',
    'student_2',
    'male',
    'female',
    'direction_1',
    'direction_2',
    'direction_3',
    'direction_4',
    'direction_5',
    'direction_6',
    'direction_7',
    'direction_8',
    'structure_1',
    'structure_2',
    'structure_3',
    'structure_4',
    'structure_5',
    'structure_6',
    'structure_7',
    'structure_8',
    'structure_9',
    'structure_10',
    'structure_11',
    'status_1',
    'status_2',
    'status_3',
    'status_4',
    'transaction_type_1',
    'transaction_type_2',
    'transaction_type_3',
    'transaction_type_4',
    'transaction_type_5',
    'transaction_type_6',
    'bath_style_0',
    'bath_style_1',
    'bath_style_2',
    'url',
    # 'name'

           ])
    
    return (building_name,series)