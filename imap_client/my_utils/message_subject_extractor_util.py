import email


class MessageParserUtil:

    def __init__(self):
        self.message_date = None
        self.message_subject = None

    def get_message_subject(self, msg: bytes, header: str) -> str:
        message = email.message_from_bytes(msg)
        msg_header = message.get(header)
        if msg_header is None:
            return "empty_" + header
        if 'utf' not in msg_header.lower() \
                and 'iso-8859' not in msg_header.lower() \
                and 'koi9-r' not in msg_header.lower() \
                and 'windows-1251' not in msg_header.lower():
            self.message_subject = msg_header
        else:
            self.message_subject = email.header.decode_header(message.get(header))[0][0]. \
                decode(email.header.decode_header(message.get(header))[0][1])
        return self.message_subject if len(self.message_subject) < 80 else self.message_subject[:80]
