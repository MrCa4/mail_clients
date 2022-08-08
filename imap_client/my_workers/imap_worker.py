from my_utils import datetime_util, message_subject_extractor_util
from my_clients.imap_client import IMAP4Client
from my_utils.file_util import FileUtil
from my_utils.helper_utils import check_result, result_data, result_returner, METHOD_NAME
from my_utils.log_error_handler_util import log_and_error_handler_decorator_maker, class_decorator_method


@class_decorator_method(log_and_error_handler_decorator_maker)
class ImapWorker(IMAP4Client):

    def __init__(self, **kwargs):
        super().__init__(kwargs.get('username'),
                         kwargs.get('password'),
                         kwargs.get('server'),
                         int(kwargs.get('port')))
        self.db_instance = kwargs.get('db_instance')
        self.username = kwargs.get('username')
        self.limit = int(kwargs.get('mail_limit'))
        self.save_path= kwargs.get('save_path')
        self.error_object = Exception
        self.warning_object = Exception

    def get_email_common(self, **kwargs) -> dict:
        auth_result = self.auth_user(**kwargs)
        if auth_result.get('result'):
            folders_result = self.get_folders_list()
            if folders_result.get('result'):
                for folder in folders_result.get('data'):
                    msg_list_prepare = self.prepare_message_list(**kwargs,
                                                                 folder=folder)
                    if msg_list_prepare.get('result') and \
                            len(msg_list_prepare.get('data')).__gt__(0):
                        self.get_messages(**kwargs,
                                          folder=folder,
                                          imap_ids=msg_list_prepare.get('data'))
                    else:
                        continue
                return {'result': True, 'action_type': 'get_email_common', 'data': 'Operation completed'}
            else:
                return folders_result
        else:
            return auth_result

    def auth_user(self, **kwargs) -> dict:

        """ NOTE: Try connect to server """

        imap_connection = self.connection()
        if imap_connection.get('result'):
            imap_auth = self.auth()
            return imap_auth
        else:
            return imap_connection

    def get_folders_list(self, **kwargs):
        imap_list_mailbox = self.list_mailbox()
        if imap_list_mailbox.get('result'):
            folder_list = imap_list_mailbox.get('data')
            return {'result': True, 'action_type': 'get_folders_list', 'data': folder_list}
        else:
            return imap_list_mailbox

    def get_folders(self, **kwargs) -> dict:
        imap_auth_result = self.auth_user()
        print(imap_auth_result)
        if imap_auth_result.get('result'):
            return self.get_folders_list(**kwargs)

    def prepare_message_list(self, **kwargs):
        folder = kwargs.get('folder')
        imap_select_mailbox = self.select_mailbox_folder(mailbox=folder)
        if imap_select_mailbox.get('result'):
            imap_get_mail_id = self.get_mails_id()

            """NOTE: Get messages imap id"""

            if imap_get_mail_id.get('result'):
                imap_ids = imap_get_mail_id.get('data')
                # NOTE: Check if it more than 1 and less then our limit and set current imap id list
                if len(imap_ids).__gt__(1) and len(imap_ids) < self.limit:
                    pass
                elif len(imap_ids) > self.limit:
                    imap_ids = imap_ids[-self.limit:]
                elif len(imap_ids) == 0:
                    return imap_get_mail_id
                folder_message_id_list = list()

                """ NOTE: From current imap id list try to get unique Message-id from message headers
                    and set new list with this unique ids """

                for imap_mail_id in imap_ids:
                    get_message_ids_result = self.get_message_custom_header(mail_id=imap_mail_id,
                                                                            header='MESSAGE-ID')
                    if get_message_ids_result.get('result'):
                        folder_message_id_list.append(get_message_ids_result.get('data'))

                """ NOTE: Get last unique id from last session and modify imap id list to get only new msg"""

                last_message_id_in_folder = self.db_instance.get_folder_message_id(username=self.username,
                                                                                   folder=folder)

                if not last_message_id_in_folder.get('result') \
                        or last_message_id_in_folder.get('data').get('msg_id') not in folder_message_id_list:
                    pass
                else:
                    if len(imap_ids).__eq__(
                            folder_message_id_list.index(last_message_id_in_folder.get('data').get('msg_id')) + 1):
                        return {'result': False, 'action_type': 'prepare_message_list', 'data': 'No new message'}
                    else:

                        imap_ids = imap_ids[folder_message_id_list.index(
                            last_message_id_in_folder.get('data').get('msg_id')) + 1:]
                return {'result': True, 'action_type': 'prepare_message_list', 'data': imap_ids}
            else:
                return imap_get_mail_id
        else:
            return imap_select_mailbox

    def get_messages(self, **kwargs) -> dict:

        imap_ids = kwargs.get('imap_ids')
        get_msg = list()
        no_get_msg = list()
        folder = kwargs.get('folder')

        for msg in imap_ids:

            """ NOTE: For every new msg download content and save it in specify format """

            if str(msg).__eq__(imap_ids[len(imap_ids) - 1]):
                msg_id = self.get_message_custom_header(mail_id=msg, header='MESSAGE-ID')
                if not msg_id.get('result'):
                    continue
                else:
                    self.db_instance.set_folder_message_id(username=self.username,
                                                           folder=folder,
                                                           msg_id=msg_id.get('data'))
                    pass
            get_message_result = self.get_message(mail_id=msg)
            if get_message_result.get('result'):
                self.__save_message(**kwargs, msg=get_message_result.get('data'), )

        return {'result': True, 'action_type': 'save_message', 'data': {'get_ids': get_msg, 'no_get_ids': no_get_msg}}

    def __save_message(self, **kwargs) -> dict:
        folder = kwargs.get('folder')
        msg = kwargs.get('msg')
        util = message_subject_extractor_util.MessageParserUtil()
        date = datetime_util.DateTimeUtil.modify(util.get_message_subject(msg, 'Date'))
        subject = util.get_message_subject(msg, 'Subject')
        author = util.get_message_subject(msg, 'From')
        msg_id = util.get_message_subject(msg, 'Message-ID')
        file_name = str(date) + "_" + str(subject) + '_' + str(author) + "_" + str(msg_id) + ".eml"
        print(file_name)
        FileUtil.write_file(self.save_path,
                            self.username,
                            folder.replace("|", "_"),
                            file_name=file_name,
                            data=msg,
                            file_option='wb', )

        return {'result': True, 'action_type': 'save_message', 'data': file_name}
