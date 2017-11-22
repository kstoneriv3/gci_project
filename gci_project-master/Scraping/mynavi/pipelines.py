# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
# from pymongo import MongoClient
# import MySQLdb

class MynaviPipeline(object):
    def process_item(self, item, spider):
        return item


# class MongoPipeline(object):

#     def __init__(self, mongo_uri, mongo_db, mongolab_user, mongolab_pass):
#         # インスタンス生成時に渡された引数で、変数初期化
#         self.mongo_uri = mongo_uri
#         self.mongo_db = mongo_db
#         self.mongolab_user = mongolab_user
#         self.mongolab_pass = mongolab_pass

#     @classmethod  # 引数にクラスがあるので、クラス変数にアクセスできる
#     def from_crawler(cls, crawler):
#         return cls(
#             mongo_uri=crawler.settings.get('MONGO_URI'), # settings.py て定義した変数にアクセスする
#             mongo_db=crawler.settings.get('MONGO_DATABASE', 'items'),
#             mongolab_user=crawler.settings.get('MONGOLAB_USER'),
#             mongolab_pass=crawler.settings.get('MONGOLAB_PASS')
#         ) # def __init__ の引数になる

#     def open_spider(self, spider): # スパイダー開始時に実行される。データベース接続
#         self.client = MongoClient(self.mongo_uri)
#         self.db = self.client[self.mongo_db]
#         self.db.authenticate(self.mongolab_user, self.mongolab_pass)

#     def close_spider(self, spider): # スパイダー終了時に実行される。データベース接続を閉じる
#         self.client.close()

#     def process_item(self, item, spider):
#         # self.db[self.collection_name].update(
#         #     {u'link': item['link']},
#         #     {"$set": dict(item)},
#         #     upsert = True
#         # ) # linkを検索して、なければ新規作成、あればアップデートする
#         # 
        

#         return item






# class MongoPipeline(object):
#     def open_spider(self, spider):
#         self.client = MongoClient('localhost', 27017)
#         self.db = self.client['gunma_test']
#         self.collection = self.db['items']

#     def close_spider(self, spider):
#         self.client.close()

#     def process_item(self, item, spider):
#         self.collection.insert_one(dict(item))
#         return item

# class MySQLPipeline(object):
#     def open_spider(self, spider):
#         settings = spider.settings
#         params = {
#             'host': settings.get('MYSQL_HOST', 'localhost'),
#             'db': settings.get('MYSQL_DATABASE', 'gunma'),
#             'user': settings.get('MYSQL_USER', 'makoto'),
#             'passwd': settings.get('MYSQL_PASSWORD', 'password'),
#             'charset': settings.get('MYSQL_CHARSET', 'utf8'),
#         }

#         self.conn = MySQLdb.connect(**params)
#         self.c = self.conn.cursor()

#         # self.c.execute('''
#         #     CREATE TABLE IF NOT EXISTS items (
#         #         id INTEGER NOT NULL AUTO_INCREMENT,
#         #         title CHAR(200) NOT NULL,
#         #         PRIMERY KEY(id);
#         #     )
#         # ''')
#         self.conn.commit()

#     def close_spider(self,spider):
#         self.conn.close()

#     def process_item(self, item, spider):
#         self.c.execute('INSERT INTO items (traffic ,address ,rent ,deposit ,layout ,area ,direction ,date ,remark ,stracture ,locality ,layout_detail ,parkings ,id_a ,hangover ,status ,transaction_type ,insrance ,guarantee ,renewal_fee ,depreciation ,premium ,period ,brokerage_fee ,right_money ,balcony ,total_units ,surroundings ,other_expence ,other_monthlyexpence ,guarantor ,reform ,location ,bath ,facility ,qualification ,other ,bath_toilet ,reheating ,south ,washing_machine ,air_conditioner ,upper ,parking ,flooring ,wash_basin ,url) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)', dict(item))
#         self.conn.commit()
#         return item