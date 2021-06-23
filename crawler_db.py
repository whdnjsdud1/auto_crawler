# -*- coding: utf-8 -*-

import pandas as pd
from sqlalchemy import create_engine
import pymysql
pymysql.install_as_MySQLdb()
import MySQLdb


def crawling_info_db():
    sns_info_df = pd.read_csv("crawler_data/naver_info_판교테크노밸리.csv",  engine='python', encoding='euc-kr')

    # MySQL Connector using pymysql
    pymysql.install_as_MySQLdb()
    import MySQLdb

    server_ip_address = 'chorock-test-2.cyurhelnwurz.ap-northeast-2.rds.amazonaws.com'
    database_id = 'chorock'
    database_password = 'chfhr123'
    schema_name = 'chorock_db'
    engine = create_engine("mysql+mysqldb://{database_id}:{database_password}@{server_ip_address}/{schema_name}?charset=utf8mb4"\
                           .format(database_id=database_id, database_password=database_password, server_ip_address=server_ip_address,
                                   schema_name=schema_name))

    conn = engine.connect()

    sns_info_df.to_sql(name='naver_kin', con=engine, if_exists='append', index=False)
    conn.close()

