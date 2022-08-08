
from dateutil.parser import *
from datetime import *
import re


class DateTimeUtil:

    @staticmethod
    def get_today() -> str:
        return "2" + re.search('([1-9]+)-(\d)*', str(datetime.today().strftime('%Y-%m%d'))).group()

    @staticmethod
    def modify(msg_date: str) -> str:
        if 'empty' in msg_date:
            return "Unknown_date"
        now = parse(msg_date)
        return "2" + re.search('([1-9]+)-(\d)*', str(now.strftime('%Y-%m%d'))).group()

