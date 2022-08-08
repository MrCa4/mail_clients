import imaplib
import shlex
import ssl
import re
from typing import Union

from my_utils import imap_utf7
from my_utils.log_error_handler_util import log_and_error_handler_decorator_maker, class_decorator_method

@class_decorator_method(log_and_error_handler_decorator_maker)
class IMAP4Client:

    def __init__(self, username: str, password: str, server: str, port: Union[str, int]):
        self.error_object = imaplib.IMAP4.error
        self.warning_object = imaplib.IMAP4.error
        self.imap_connection = None
        self.username = username
        self.password = password
        self.server = server
        self.port = int(port)
        self.debug = None

    def connection(self) -> dict:
        i = 0
        while i < 10:
            try:
                if self.port.__eq__(993):
                    # self.imap_connection = imaplib.IMAP4_SSL(self.server, ssl_context=ssl.create_default_context())
                    ssl_context = ssl.create_default_context()
                    ssl_context.check_hostname = False
                    ssl_context.verify_mode = ssl.CERT_NONE
                    self.imap_connection = imaplib.IMAP4_SSL(self.server, ssl_context=ssl_context)
                elif self.port.__eq__(143):
                    self.imap_connection = imaplib.IMAP4(self.server)
                else:
                    return {'result': False, 'action_type': 'connection', 'error': 'Bad server port: ' + str(self.port)}
                return {'result': True, 'action_type': 'connection', 'data': 'Ok'}
            except:
                i += 1
        return {'result': False, 'action_type': 'connection', 'data': 'Error_connection'}

    def auth(self) -> dict:
        response_code, response = self.imap_connection.login(self.username, self.password)
        if response_code.__eq__('OK'):
            return {'result': True, 'action_type': 'auth', 'data': 'Ok'}
        else:
            return {'result': False, 'action_type': 'auth', 'error': (response_code, response)}

    def list_mailbox(self) -> dict:
        directories_list = []
        for directory in self.imap_connection.list()[1]:
            directories_list.append(shlex.split(imap_utf7.decode(directory.decode()))[-1])
        return {'result': True, 'action_type': 'mailbox_list', 'data': directories_list}

    def select_mailbox_folder(self, **kwargs) -> dict:
        typ, dat = self.imap_connection.select(mailbox=kwargs.get('mailbox'), readonly=True)
        if typ.__eq__('OK'):
            return {'result': True, 'action_type': 'select_mailbox'}
        else:
            return {'result': False, 'action_type': 'select_mailbox', 'error': (typ, dat)}

    def get_mails_id(self) -> dict:
        mails_id_list = self.imap_connection.search(None, "ALL")[1][0].decode().split()
        return {'result': True, 'action_type': 'get_mails_ids', 'data': mails_id_list}

    def get_message_ids(self, **kwargs) -> dict:
        result, data = self.imap_connection.fetch(kwargs.get('imap_id'), '(BODY[HEADER.FIELDS (MESSAGE-ID)])')
        message_id = data[0][1].decode('UTF-8').split(": ")[1]
        return {'result': True, 'action_type': 'get_message_ids', 'data': message_id}

    def get_message_custom_header(self, **kwargs) -> dict:
        header_raw = self.imap_connection.fetch(kwargs.get('mail_id'),
                                                '(BODY[HEADER.FIELDS (' + kwargs.get("header") + ')])')[1][0][1].decode(
            'UTF-8')
        header = re.sub(r'[\r\n\,<>]', "", header_raw)
        return {'result': True, 'action_type': 'get_message_custom_header_' + str(kwargs.get("header")), 'data': header}

    def __get_message_header(self, mail_id: str) -> dict:
        mail_header = self.imap_connection.fetch(mail_id, '(BODY.PEEK[HEADER])')[1][0][1]
        return {'result': True, 'action_type': 'get_mail_header', 'data': mail_header}

    def __get_message_data(self, mail_id: str) -> dict:
        mail_data = self.imap_connection.fetch(mail_id, '(BODY.PEEK[TEXT])')[1][0][1]
        return {'result': True, 'action_type': 'get_message_data', 'data': mail_data}

    def get_message(self, **kwargs) -> dict:
        mail_data = self.imap_connection.fetch(kwargs.get('mail_id'), '(RFC822)')[1][0][1]
        return {'result': True, 'action_type': 'get_message_data', 'data': mail_data}

    def __download_message(self, mail_id: str) -> dict:
        message = {'header': self.__get_message_header(mail_id).decode().replace("\n", ""),
                   'data': self.__get_message_data(mail_id).replace("\n", "")}
        return {'result': True, 'action_type': 'message_data', 'data': message}
