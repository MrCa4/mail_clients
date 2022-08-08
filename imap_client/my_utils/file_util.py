import os
import re
from my_utils.log_error_handler_util import class_decorator_method, log_and_error_handler_decorator_maker


@class_decorator_method(log_and_error_handler_decorator_maker)
class FileUtil:

    def __init__(self):
        self.error_object = Exception
        self.warning_object = Exception

    @staticmethod
    def write_file(*args, **kwargs) -> dict:
        file_path = ""
        for arg in args:
            file_path = os.path.join(file_path, arg)
        os.makedirs(file_path, exist_ok=True)
        file_name = re.sub(r'[$= \<\>;&?!|\/\[\]\(\):\s\'\"\r\n]', "_", kwargs.get('file_name'))
        with open(os.path.join(file_path, file_name), kwargs.get('file_option')) as file:
            file.write(kwargs.get('data'))
        return {'result': True, 'type': 'write_file', 'data': file_name}

    def write_log(self, file, log_string):
        with open(file, "a", encoding="UTF-8") as file:
            file.write(log_string)
