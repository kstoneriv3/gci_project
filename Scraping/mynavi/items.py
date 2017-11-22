# -*- coding: utf-8 -*-

# Define here the models for your scraped items
import scrapy


class MynaviItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

class RealEstate(scrapy.Item):
    # 交通
    traffic = scrapy.Field()
            
    # 所在地
    address = scrapy.Field()
            
    # 賃料
    rent = scrapy.Field()

    # 敷金・礼金
    deposit = scrapy.Field()

    # 間取り
    layout= scrapy.Field()

    # 面積
    area =scrapy.Field()

    # 方角
    direction = scrapy.Field()

    # 築年月
    date = scrapy.Field()

    # 備考
    remark = scrapy.Field()

    # 建物構造
    structure = scrapy.Field()

    # 所在階/階数
    locality = scrapy.Field()

    # 間取り詳細
    layout_detail = scrapy.Field()

    # 駐車場
    parkings = scrapy.Field()

    # 物件id
    id = scrapy.Field()

    # 引き渡し
    handover = scrapy.Field()

    # 現況
    status = scrapy.Field()

    # 取引態様
    transaction_type = scrapy.Field()

    # 住宅保険
    insurance = scrapy.Field()

    # 保証会社
    guarantee = scrapy.Field()

    # 更新料
    renewal_fee = scrapy.Field()
    
    # 償却･敷引
    depreciation = scrapy.Field()

    # 敷金割り増し
    premium = scrapy.Field()

    # 契約期間
    period = scrapy.Field()

    # 仲介手数料
    brokerage_fee = scrapy.Field()

    # 権利金
    right_money = scrapy.Field()

    # バルコニー面積
    balcony = scrapy.Field()

    # 総戸数
    total_units = scrapy.Field()

    # 周辺環境
    surroundings = scrapy.Field()

    # その他費用
    other_expence = scrapy.Field()

    # その他月額費用
    other_monthlyexpence = scrapy.Field()

    # 保証人代行
    guarantor = scrapy.Field()

    # リフォーム
    reform = scrapy.Field()

    # 位置/方角
    location = scrapy.Field()

    # バス・トイレ/キッチン
    bath = scrapy.Field()

    # 設備/サービス
    facility = scrapy.Field()

    # 入居条件
    qualification = scrapy.Field()

    # その他
    other = scrapy.Field()

    # バス・トイレ別
    bath_toilet = scrapy.Field()

    # 追焚機能
    reheating = scrapy.Field()

    # 南向き
    south = scrapy.Field()

    # 室内洗濯機置場
    washing_machine = scrapy.Field()

    # エアコン
    air_conditioner = scrapy.Field()

    # オートロック
    auto_lock = scrapy.Field()

    # 2階以上
    upper = scrapy.Field()

    # 駐車場
    parking = scrapy.Field()

    # フローリング
    flooring = scrapy.Field()

    # 洗面台独立
    wash_basin = scrapy.Field()    

    # URL
    url = scrapy.Field()