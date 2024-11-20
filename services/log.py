import logging
from datetime import datetime

class FileLogger:
    def __init__(self, log_file='logs.txt'):
        self.log_file = log_file
        logging.basicConfig(filename=self.log_file, level=logging.INFO, format='%(message)s', filemode='a')

    def log(self, user_id, operation_type, data_affected, old_value=None, new_value=None):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        formatted_data = ', '.join(data_affected)
        log_message = f"{timestamp} | User: {user_id} | Operation: {operation_type} | Data: {formatted_data}"
        
        if operation_type == 'modify':
            log_message += f" | Old Value: {old_value} | New Value: {new_value}"
        
        logging.info(log_message)

# Example usage:
# logger = FileLogger()
# logger.log(user_id='user123', operation_type='read', data_affected='record_1')
# logger.log(user_id='user123', operation_type='write', data_affected='record_2')
# logger.log(user_id='user123', operation_type='modify', data_affected='record_3', old_value='old_data', new_value='new_data')