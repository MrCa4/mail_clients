
import sys
import logging
from typing import Union

from my_clients.db_client import DBClient
from my_workers.imap_worker import ImapWorker
from my_utils.log_error_handler_util import log_and_error_handler_decorator_maker, class_decorator_method


@class_decorator_method(log_and_error_handler_decorator_maker)
class ImapMain:

    def __init__(self, username: str,
                 db_path: str,
                 save_path: Union[str, None] = None,
                 server: Union[str, None] = None,
                 port: Union[str, None] = None,
                 password: Union[str, None] = None,
                 date: Union[str, None] = None,
                 command: Union[str, None] = None,
                 limit: Union[str, int] = 100):

        self.error_object = Exception
        self.warning_object = Exception
        db_instance_result = DBClient(db_path)
        if db_instance_result is None:
            print('Bad connection to DB')
            return 1
        self.username = username
        self.db_instance = db_instance_result
        self.user_info = self.db_instance.get_user_folders_info(username=self.username)
        self.command = command.split(":")
        self.password = self.user_info.get('data').get('user_info').get('password') if password is None else password
        self.server = self.user_info.get('data').get('user_info').get('server') if server is None else server
        self.port = self.user_info.get('data').get('user_info').get('port') if port is None else port
        self.date = date
        self.save_path = self.user_info.get('data').get('user_info').get(
            'save_path') if save_path is None else save_path
        self.mail_limit = int(limit)
        self.imap_worker = ImapWorker(username=self.username,
                                      password=self.password,
                                      server=self.server,
                                      port=self.port,
                                      mail_limit=self.mail_limit,
                                      db_instance=self.db_instance,
                                      save_path=self.save_path)

    def start(self) -> Union[str, dict, list]:
        for task in self.command:
            print(task)
            if task.__eq__('create_user'):
                folder_list = self.imap_worker.get_folders()
                if folder_list.get('result'):
                    print(folder_list.get('data'))
                    create_user_result = self.db_instance.create_new_mail_user(
                        username=self.username,
                        password=self.password,
                        server=self.server,
                        port=self.port,
                        folder_list=folder_list.get('data'),
                        save_path=self.save_path)
                    if not create_user_result.get('result'):
                        print(create_user_result.get('data'))
                        return create_user_result.get('data')
                else:
                    print(folder_list.get('data'))
                    return folder_list.get('data')
            if task.__eq__('change_password'):
                create_user_result = self.db_instance.change_user_password(
                    username=self.username,
                    password=self.password)
                if not create_user_result.get('result'):
                    print(create_user_result.get('data'))
                    return create_user_result.get('data')
                pass
            if task.__eq__('delete_user'):
                pass
            if task.__eq__('get_user_info'):
                pass
            if task.__eq__('get_email'):
                self.imap_worker.get_email_common(username=self.username,
                                                  mail_limit=self.mail_limit,
                                                  db_instance=self.db_instance)
        return "End"


def help():
    print(""" =================== SIMPLE IMAP4 CLIENT =====================""")
    print("""Created by: @Mr_Ca4, version 0.2""")
    print("""Available commands:""")
    print("""create_user - create new user""")
    print("""get_email - get new email from user""")
    print("""help - get help message""")
    print(
        """Example: python.py imap_client.py command=create_user db_path=<db_path>
          username=<username>
          password=<password>
          server=<server>
          port=<port>
          save_path=<save_path>
          [limit=<limit #default 100]
          [log_path=<path_to_log_file>]""")
    print(
        """Example: python.py imap_client.py command=get_email db_path=<db_path>
         username=<username>[:<username>] [limit=<limit #default 100] [log_path=<path_to_log_file>]""")
    print(
        """Example: python.py imap_client.py command=create_user[:get_email] db_path=<db_path>
         username=<username>[:<username>] [limit=<limit #default 100]
        save_path=<save_path> password=<password> server=<server> port=<port> [log_path=<path_to_log_file>]""")


def main(my_kwargs):
    if my_kwargs.get('json_config_path'):
        #TODO json parser config file or message broker
        pass
    elif my_kwargs.get('log_path'):
        log_path = my_kwargs.get('log_path')
        logging.basicConfig(
            level=logging.INFO,
            filename=log_path,
            format="%(asctime)s - %(module)s - %(levelname)s - %(funcName)s: %(lineno)d - %(message)s",
            datefmt='%H:%M:%S',
        )
        pass
    elif my_kwargs.get('db_path') is None or \
            my_kwargs.get('username') is None or \
            my_kwargs.get('command') is None:
        print("Bad parameters")
        help()
        return 1
    for user in my_kwargs.get('username').split(':'):
        print(user)
        ia = ImapMain(username=user,
                        password=my_kwargs.get('password'),
                        server=my_kwargs.get('server'),
                        port=my_kwargs.get('port'),
                        command=my_kwargs.get('command'),
                        db_path=my_kwargs.get('db_path'),
                        save_path=my_kwargs.get('save_path'),
                        limit=my_kwargs.get('limit')
                        )

        ia.start()


if __name__ == '__main__':
    args = sys.argv
    kwargs = {}
    for arg in args[1:]:
        list_arg = arg.split('=')
        kwargs.update(dict({list_arg[0]: list_arg[1]}))
    main(kwargs)
