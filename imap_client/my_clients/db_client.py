import sqlite3
from my_utils.log_error_handler_util import log_and_error_handler_decorator_maker, class_decorator_method


@class_decorator_method(log_and_error_handler_decorator_maker)
class DBClient:

    def __init__(self, db_file):
        self.error_object = sqlite3.Error
        self.warning_object = sqlite3.Warning
        self.conn = sqlite3.connect(db_file)
        self.cursor = self.conn.cursor()

    def create_new_mail_user(self, *args, **kwargs) -> dict:
        self.cursor.execute(
            "INSERT INTO `users` (`username`,`password`,`server`,`port`, `save_path`) VALUES (?,?,?,?,?)",
            (kwargs.get('username'), kwargs.get('password'), kwargs.get('server'),
             int(kwargs.get('port')), kwargs.get('save_path')))

        new_user_id = self.cursor.execute("SELECT `id` FROM `users` WHERE `username` = (?)",
                                          (kwargs.get('username'),)).fetchall()[0][0]
        for folder_name in kwargs.get('folder_list'):
            self.cursor.execute("INSERT INTO `folders` (`user_id`,`folder_name`,`last_msg_id`) VALUES (?,?,?)",
                                (new_user_id, folder_name, '0'))
        self.conn.commit()
        return {'result': True, 'action_type': 'create_new_mail_user', 'data': 'Ok'}

    def change_user_password(self, *args, **kwargs) -> dict:
        self.cursor.execute(
            "UPDATE `users` SET `password`=(?) WHERE `username`=(?)",
            (kwargs.get('username'), kwargs.get('password')))

        new_user_password = self.cursor.execute("SELECT `password` FROM `users` WHERE `username` = (?)",
                                                (kwargs.get('username'),)).fetchall()[0][0]
        if kwargs.get('password').__eq__(new_user_password):
            self.conn.commit()
            return {'result': True, 'action_type': 'create_new_mail_user', 'data': 'Ok'}
        return {'result': False, 'action_type': 'create_new_mail_user', 'data': 'Password not update'}

    def get_user_folders_info(self, **kwargs) -> dict:

        username = kwargs.get('username')
        user_info = self.__get_user_info(username=username)
        user_id = user_info.get('id')
        folder_info = self.__get_folders_info(user_id=user_id)
        data = {'user_info': user_info, 'folder_info': folder_info}
        return {'result': True, 'action_type': 'get_user_info_from_db', 'data': data}

    def set_folder_message_id(self, **kwargs) -> dict:
        username = kwargs.get('username')
        folder = kwargs.get('folder')
        msg_id = kwargs.get('msg_id')
        user_info = self.__get_user_info(username=username)
        user_id = user_info.get('id')
        self.cursor.execute(
            "UPDATE `folders` SET `last_msg_id`= (?) WHERE `user_id` = (?) AND `folder_name` = (?)",
            (msg_id, user_id, folder))
        self.conn.commit()
        data = {'user_id': user_id, 'folder': folder, 'msg_id': msg_id}
        return {'result': True, 'action_type': 'set_folder_message_id', 'data': data}

    def get_folder_message_id(self, **kwargs) -> dict:
        username = kwargs.get('username')
        folder = kwargs.get('folder')
        user_info = self.__get_user_info(username=username)
        user_id = user_info.get('id')
        message_id_result = self.cursor.execute(
            "SELECT `last_msg_id` FROM `folders` WHERE `folder_name` = (?) AND `user_id` = (?)",
            (folder, user_id)).fetchall()[0][0]
        data = {'user_id': user_id, 'folder': folder, 'msg_id': message_id_result}
        return {'result': True, 'action_type': 'get_user_info_from_db', 'data': data}

    def __get_user_info(self, **kwargs) -> dict:
        username = kwargs.get('username')
        user_info = self.cursor.execute(
            "SELECT `id`,`username`, `password`,`server`,`port`, `save_path` FROM `users` WHERE `username` = (?)",
            (username,)
        ).fetchall()

        data = {'id': user_info[0][0], 'username': user_info[0][1], 'password': user_info[0][2],
                'server': user_info[0][3], 'port': user_info[0][4], 'save_path': user_info[0][5]}

        return data

    # TODO change return to dict
    def __get_folders_info(self, **kwargs) -> tuple:
        user_id = kwargs.get('user_id')
        folders_info = self.cursor.execute(
            "SELECT `folder_name`, `last_msg_id` FROM `folders` WHERE `user_id` = (?)",
            (user_id,)
        ).fetchall()
        return folders_info
