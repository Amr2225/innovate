from django.core.signing import Signer
from django.core.mail import send_mail


class SendEmail():
    def __init__(self, email):
        self.email = email
        self.token = None

    def _generateVerificationToken(self):
        signer = Signer()
        self.token = signer.sign(self.email)

    def _generateVerificationLink(self):
        return f"http://localhost:8000/verify-email/?token={self.token}"

    def send(self):
        self._generateVerificationToken()
        verificationLink = self._generateVerificationLink()

        send_mail(
            'Verify Your Email',
            f'Click the link to verify your email: {verificationLink}',
            'from@example.com',
            [self.email],
            fail_silently=False,
        )


def generateVerificationToken(email):
    signer = Signer()
    return signer.sign(email)


def generateVerificationLink(token):
    return f"http://localhost:8000/auth/verify-email/?token={token}"


def sendEmail(email, otp):
    print("OTP", otp)
    token = generateVerificationToken(email)
    verificationLink = generateVerificationLink(token)

    # send_mail(
    #     'Verify Your Email',
    #     f'Click the link to verify your email: {verificationLink}',
    #     'from@example.com',
    #     [email],
    #     fail_silently=False,
    # )

    send_mail(
        'Verify Your Email',
        f'This is your OTP to verify your email: {otp}',
        'from@example.com',
        [email],
        fail_silently=False,
    )
