from django.core.mail.backends.smtp import EmailBackend
import ssl

class UnsafeTLSBackend(EmailBackend):
    def open(self):
        if self.connection:
            return False

        import smtplib
        self.connection = smtplib.SMTP(
            self.host,
            self.port,
            timeout=self.timeout,
        )
        self.connection.ehlo()

        if self.use_tls:
            context = ssl._create_unverified_context()
            self.connection.starttls(context=context)
            self.connection.ehlo()

        if self.username and self.password:
            self.connection.login(self.username, self.password)

        return True