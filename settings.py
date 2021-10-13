import os
from dotenv import load_dotenv
from datetime import datetime
from pydantic import BaseModel
from typing import List

from utils.selections import ModelType, PredictTarget

SOURCE = {'WH_F0183': 'Comment',
          'WH_F0116': 'Dcard',
          'WH_F0001': 'Ptt',
          'WH_F0147': 'Youtube',
          'WH_F0157': 'Instagram',
          'WH_F0501': 'Tiktok',
          'WH_F0127': 'Twitter',
          'WH_F0045': 'fbfans',
          'WH_F0165': 'fbgroup',
          'WH_F0071': 'fbkol',
          'WH_F0167': 'fbprivategroup',
          'WH_F0038': 'plurk',
          'WH_F0002': 'forum',
          'WH_B0002': 'blog',
          'WH_CTN0026': 'news'}


class CeleryConfig:
    name = 'celery_worker'
    sql_uri = 'sqlite:///save.db'
    backend = 'db+sqlite:///save.db'
    broker = 'redis://localhost'
    timezone = 'Asia/Taipei'
    enable_utc = False
    result_expires = None

class DatabaseInfo:
    load_dotenv()
    host = os.getenv('HOST')
    port = int(os.getenv('PORT'))
    user = os.getenv('USER')
    password = os.getenv('PASSWORD')
    input_schema = os.getenv('INPUT_SCHEMA')
    output_schema = os.getenv('OUTPUT_SCHEMA')
    rule_schemas = os.getenv('RULE_SHEMAS')
    engine_info = f'mysql+pymysql://{user}:{password}@{host}:{port}/{output_schema}?charset=utf8mb4'

class CreateTaskRequestBody(BaseModel):
    model_type: str = 'keyword_model'
    predict_type: str = 'author_name'
    start_time: datetime = "2018-01-01 00:00:00"
    end_time: datetime = "2018-12-31 23:59:59"
    target_schema: str = "forum_data"
    target_table: str = "ts_page_content"

class TaskListRequestBody:
    order_column: str = 'date_done'
    number: int = 50
    offset: int = 1000
    sql_schema: str = 'sqlite:///save.db'
    table: str = 'celery_taskmeta'


class SampleResultRequestBody:
    order_column: str = "create_time"
    number: int = 50
    offset: int = 1000
    sql_schema: str = 'audience_result'
    table: List[str] = ['wh_panel_mapping_Comment',
                        'wh_panel_mapping_Dcard',
                        'wh_panel_mapping_Ptt',
                        'wh_panel_mapping_Youtube',
                        'wh_panel_mapping_Instagram',
                        'wh_panel_mapping_Tiktok',
                        'wh_panel_mapping_Twitter',
                        'wh_panel_mapping_fbfans',
                        'wh_panel_mapping_fbgroup',
                        'wh_panel_mapping_fbkol',
                        'wh_panel_mapping_fbprivategroup',
                        'wh_panel_mapping_plurk',
                        'wh_panel_mapping_forum',
                        'wh_panel_mapping_blog',
                        'wh_panel_mapping_news']

