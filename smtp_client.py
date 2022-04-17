import smtplib
import socks
import ssl

_DEFAULT_CIPHERS = (
    'ECDH+AESGCM:DH+AESGCM:ECDH+AES256:DH+AES256:ECDH+AES128:DH+AES:ECDH+HIGH:'
    'DH+HIGH:ECDH+3DES:DH+3DES:RSA+AESGCM:RSA+AES:RSA+HIGH:RSA+3DES:!aNULL:'
    '!eNULL:!MD5')


class smtpclient:

    def __init__(self):
        self.smtpEx = smtplib.SMTPException
        self.result = list()

    def smtpConnect(self, host: str, port: int) -> list:
        try:
            self.smtp = smtplib.SMTP()
            self.smtp.connect(host, port)
            self.result.append(self.smtp)
        except smtplib.SMTPException:
            self.result.append("Exception smtp")
        finally:
            return self.result

    def smtpAuthSTARTTLS(self, function: function, host: str, login: str, password: str) -> function:
        context = ssl._create_unverified_context()
        self.smtp = smtplib.SMTP(host, 587)
        self.smtp.ehlo()
        self.smtp.starttls(context=context)
        return function(login, password)

    def smtpAuthSSL(self, function: function, host: str, login: str, password: str) -> function:
        self.smtp = smtplib.SMTP_SSL(host, 465)
        return function(login, password)

    def smtpAuthPLAIN(self, function: function, host: str, login: str, password: str) -> function:
        self.smtp = smtplib.SMTP(host, 25)
        return function(login, password)

    def smtpAuth(self, login: str, password: str) ->list:
        self.smtp.set_debuglevel(2)
        self.smtp.ehlo_or_helo_if_needed()
        result = None
        try:
            res = self.smtp.login(login, password)
            result = [res[0], res[1], login, password]
        except smtplib.SMTPHeloError:
            result = ["500", "Auth Hello Error", login, password]
        except smtplib.SMTPNotSupportedError:
            result = ["504", "Not supported method", login, password]
        except smtplib.SMTPAuthenticationError:
            result = ["535", "Bad login or password", login, password]
        finally:
            if result is None:
                result = ["000", "Unknown error"]
            return result

    def sendMail(self, fromAddr: str, toAddrs: str, msg: str, options, rcptOptions):
        self.smtp.sendmail(fromAddr, toAddrs, msg, options, rcptOptions)

    def getMsgFromString(self, fromAddr, toAddr, subject, messageText):
        self.msg = "\r\n".join((
            "From: {fromAddr}",
            "To: {toAddr}",
            "Subject:  {subject}",
            "",
            "{messageText}"
        )).format(fromAddr=fromAddr, toAddr=toAddr, subject=subject, messageText=messageText).encode('utf-8').strip()

    def smtpExit(self):
        self.smtp.quit()

    def smtpVerify(self, host: str) -> list:
        if self.smtp == None:
            self.smtp = smtplib.SMTP(host)
            ehlo = self.smtp.ehlo()
            ans = self.smtp.verify(host)
            return [ans, ehlo]
        else:
            ehlo = self.smtp.ehlo()
            ans = self.smtp.verify(host)
            return [ans, ehlo]

    def smtpCmd(self
                , cmd: str
                , args: Unioon[str, None] = None
                , host: Union[str, None] = None
                , smtp: Union[str, None] = None) -> list:
        if smtp is None:
            self.smtp = smtplib.SMTP(host)
            self.smtp.set_debuglevel(2)
            result = self.smtp.docmd(cmd, args)
            self.result.append(result)
        else:
            result = self.smtp.docmd(cmd, args)
            self.smtp.set_debuglevel(2)
            self.result.append(result)
        return self.result

    def smtpSetProxy(self, proxy_type: str, host: str, port: int) -> None:
        socks.setdefaultproxy(proxy_type, host, port)
        socks.wrapmodule(smtplib)

    def smtpSent(self, fromAddr: str, toAddr: str, msg: str) -> None:
        self.smtp.sendmail(fromAddr, toAddr, msg)


def main(argv):
    smtpObj = smtpclient()
    # smtpObj.smtpSetProxy(socks.PROXY_TYPE_SOCKS5, '127.0.0.1', 9150)
    smtpObj.smtpAuthSTARTTLS(smtpObj.smtpAuth, '<YOUR_SERVER>', '<YOUR_LOGIN>', '<YOUR_PASSWORD>')  # Ваш Логин Пароль
    smtpObj.getMsgFromString("<FROM>",
                             '<TO>',
                             '<SUBJECT>',
                             '<BODY>')
    smtpObj.smtpSent('<YOUR_LOGIN>', '<YOUR_RECIPIENT>', smtpObj.msg)
    smtpObj.smtpExit()


if __name__ == '__main__':
    main()
