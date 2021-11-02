from typing import Dict
from sqlalchemy import create_engine
from settings import DatabaseInfo, SOURCE
from utils.database_core import connect_database, get_distinct_count, get_label_source_from_state
from utils.helper import get_logger


class TaskInfo(object):
    def __init__(self, task_id: str, schema: str, table: str,
                 from_target_table: str, row_count: int,
                 logger: get_logger, date_info = True, **kwargs):
        self.task_id = task_id
        self.schema = schema
        self.table = table
        self.from_target_table = from_target_table
        self.row_count = row_count
        self.logger = logger
        self.partial_table = table.split("_")[-1]
        self._from_schema = get_label_source_from_state(task_id)
        self.date_info = date_info
        self.start_time = kwargs.get('start_time')
        self.end_time = kwargs.get('end_time')

        connection = create_engine(DatabaseInfo.output_engine_info).connect()
        _exist_tables = [i[0] for i in connection.execute('SHOW TABLES').fetchall()]
        if 'task_info' not in _exist_tables:
            self.create_task_info(DatabaseInfo.output_schema, logger)
        connection.close()


    def generate_output(self):
        state_dict = self.get_status_info(self.task_id, self.schema, self.logger)
        _source_distinct_count = self.get_source_distinct_count(self._from_schema,
                                                                self.from_target_table,
                                                                self.partial_table,
                                                                self.date_info,
                                                                self.start_time,
                                                                self.end_time)
        _task_info_statement = {
            'task_id' : state_dict.get('task_id'),
            'input_data_size' : state_dict.get('length_receive_table'),
            'output_data_size' : self.row_count,
            'max_memory_usage' : state_dict.get('peak_memory'),
            'run_time' : state_dict.get('run_time'),
            'rate_of_label' : round((self.row_count / _source_distinct_count)*100)
        }

        self.insert_task_info(self.schema, self.logger, **_task_info_statement)

    def get_status_info(self, task_id, schema, logger) -> Dict:
        state_query = f'SELECT * FROM state WHERE task_id = "{task_id}"'
        func = connect_database
        try:
            with func(schema, output=True).cursor() as cursor:
                cursor.execute(state_query)
                result = cursor.fetchone()
                func(schema, output=True).close()
                logger.info(f'scrape state info')
                return result
        except Exception as e:
            logger.error(e)
            raise e

    def create_task_info(self, schema, logger):
        insert_sql = f'CREATE TABLE IF NOT EXISTS `task_info`(' \
                     f'`task_id` VARCHAR(32) NOT NULL,' \
                     f'`input_data_size` INT(20),' \
                     f'`output_data_size` INT(20),' \
                     f'`max_memory_usage` FLOAT(10),' \
                     f'`run_time` FLOAT(10),' \
                     f'`rate_of_label` FLOAT(10),' \
                     f')ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin ' \
                     f'AUTO_INCREMENT=1 ;'
        _connection = connect_database(schema, output=True)
        try:
            with _connection.cursor() as cursor:
                logger.info('connecting to database...')
                logger.info('creating table...')
                cursor.execute(insert_sql)
                _connection.close()
                logger.info(f'successfully created table.')
        except Exception as e:
            logger.error(e)
            raise e

    def insert_task_info(self, schema, logger, **kwargs):

        task_id = kwargs.get('task_id')
        input_data_size = kwargs.get('input_data_size')
        output_data_size = kwargs.get('output_data_size')
        max_memory_usage = kwargs.get('max_memory_usage')
        run_time = kwargs.get('run_time')
        rate_of_label = kwargs.get('rate_of_label')

        insert_sql = f'INSERT INTO task_info ' \
                     f'(task_id, input_data_size, output_data_size, ' \
                     f'max_memory_usage, run_time, rate_of_label) VALUES (' \
                     f'"{task_id}", ' \
                     f'"{input_data_size}", ' \
                     f'"{output_data_size}", ' \
                     f'"{max_memory_usage}", ' \
                     f'"{run_time}", ' \
                     f'"{rate_of_label}");'

        try:
            _connection = connect_database(schema, output=True)
            cursor = _connection.cursor()
            cursor.execute(insert_sql)
            _connection.commit()
            _connection.close()
            logger.info(f'successfully write into table task_info.')

        except Exception as e:
            logger.error(e)
            raise e

    def get_source_distinct_count(self, source_schema, table_name, partial_table,
                                  date_info, start_time, end_time):

        target_source_list = SOURCE.get(partial_table)
        if len(target_source_list) > 1:
            condition = tuple(target_source_list)
        else:
            condition = f'("{target_source_list[0]}")'

        source_distinct_count = get_distinct_count(source_schema, table_name,
                                                   condition=condition,
                                                   date_info=date_info,
                                                   start_time=start_time,
                                                   end_time=end_time)

        return source_distinct_count



