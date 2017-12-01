import pandas as pd
from sqlalchemy import create_engine

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

query = "SELECT TOP 1 * FROM raw_data_table"
raw_data = pd.read_sql(query, con=engine).iloc[:1,:110]

query = "SELECT TOP 1 * FROM analytical_data_table"
analytical_data = pd.read_sql(query, con=engine)