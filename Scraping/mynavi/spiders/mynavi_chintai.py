import re
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor

from mynavi.items import RealEstate

class MynaviChintaiSpider(CrawlSpider):
    name = 'mynavi_chintai'
    allowed_domains = ['chintai.mynavi.jp']
    start_urls = ['https://chintai.mynavi.jp/tokyo/106/']
    rules = [
        Rule(LinkExtractor(allow=r'/tokyo/106/p\d+')),

        Rule(LinkExtractor(allow=r'/tokyo/106/room.',unique=True), callback='parse_detail'),
    ]

    def parse_detail(self, response):

        # 物件項目取得
        menu = response.xpath('//tr/th').xpath('string()').extract()
        # 物件情報取得
        contents = response.xpath('//tr/td').xpath('string()').extract()

        #こだわりポイント（画像データ）
        detail = response.xpath('//tr/td/ul/li/img').extract()

        sort = ['' for i in range(38)]

        def modify_detail(detail):
            for i in range(10):
                if ('on.gif' in detail[i]):
                    detail[i] = '1'
                else:
                    detail[i] = '0'
            return detail

        detail = modify_detail(detail)



        # 間取り詳細が２段になっているときに、物件ID以降のデータがずれて取得されてしまう現象の修正
        def fix_a(menu,contents):
            str = '物件ID'
            index_id = menu.index(str)
            if contents[index_id].isdigit() == False:
                contents[index_id-2] = contents[index_id-2] + ' ' + contents[index_id]
                del contents[index_id]
            return contents

        contents = fix_a(menu,contents)

        def sorting(menu,contents):
            index = ['' for i in range(38)]
            ret = ['' for i in range(38)]
            item_list = [
             '交通',#0
             '所在地',#1
             '賃料管理費・共益費',#2
             '敷金(保証金)礼金(敷引・償却金)',#3
             '間取り',#4
             '面積',#5
             '方角',#6
             '築年月',#7
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
             'バス・トイレ/キッチン',#33
             '設備/サービス',#34
             '入居条件',#35
             'その他',#36
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

            if ret[13].isdigit() == False:
                ret[11] = ret[11] + ' ' + ret[13]
                del ret[13]

            return ret


        # 項目の並べ替え
        sort = sorting(menu, contents)


        item = RealEstate(
      
            # 最寄り駅 
            traffic = sort[0],
            
            # 所在地
            address = sort[1],
            
            # 賃料
            rent = sort[2],

            # 敷金・礼金
            deposit = sort[3],

            # 間取り
            layout= sort[4],

            # 面積
            area = sort[5],

            # 方角
            direction = sort[6],

            # 築年月
            date = sort[7],

            # 備考
            remark = sort[8],

            # 建物構造
            structure = sort[9],

            # 所在階/階数
            locality = sort[10],

            # 間取り詳細
            layout_detail = sort[11],

            # 駐車場
            parkings = sort[12],

            # 物件id
            id = sort[13],

            # 引き渡し
            handover = sort[14],

            # 現況
            status = sort[15],

            # 取引態様
            transaction_type = sort[16],

            # 住宅保険
            insurance = sort[17],

            # 保証会社
            guarantee = sort[18],

            # 更新料
            renewal_fee = sort[19],
            
            # 償却･敷引
            depreciation = sort[20],

            # 敷金割り増し
            premium = sort[21],

            # 契約期間
            period = sort[22],

            # 仲介手数料
            brokerage_fee = sort[23],

            # 権利金
            right_money = sort[24],

            # バルコニー面積
            balcony = sort[25],

            # 総戸数
            total_units = sort[26],

            # 周辺環境
            surroundings = sort[27],

            # その他費用
            other_expence = sort[28],

            # その他月額費用
            other_monthlyexpence = sort[29],

            # 保証人代行
            guarantor = sort[30],

            # リフォーム
            reform = sort[31],

            # 位置/方角
            location = sort[32],

            # バス・トイレ/キッチン
            bath = sort[33],

            # 設備/サービス
            facility = sort[34],

            # 入居条件
            qualification = sort[35],

            # その他
            other = sort[36],

            # バス・トイレ別
            bath_toilet = detail[0],

            # 追焚機能
            reheating = detail[1],

            # 南向き
            south = detail[2],

            # 室内洗濯機置場
            washing_machine = detail[3],

            # エアコン
            air_conditioner = detail[4],

            # オートロック
            auto_lock = detail[5],

            # 2階以上
            upper = detail[6],

            # 駐車場
            parking = detail[7],

            # フローリング
            flooring = detail[8],

            # 洗面台独立
            wash_basin = detail[9],

            # URL
            url = response.url

        )

        yield item

