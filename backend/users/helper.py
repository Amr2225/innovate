from datetime import timedelta
import os
from django.utils import timezone
from random import random
from django.core.signing import Signer
from django.core.mail import send_mail
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.settings import api_settings


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


def generateOTP(user):
    if user.otp_created_at + timedelta(minutes=user.otp_expiry_time_minutes) <= timezone.now():
        otp = str(random.randint(100000, 999999))
        user.otp = otp
        user.otp_created_at = timezone.now()
        user.save()


def generateTokens(user, isFirstLogin=False):
    # if isFirstLogin:
    #     api_settings.SIGNING_KEY = os.environ.get("JWT_ACCESS_LOGIN")
    # else:
    #     api_settings.SIGNING_KEY = os.environ.get("JWT_MAIN")

    refresh = RefreshToken.for_user(user)

    if isFirstLogin:
        national_id = user.national_id
        signer = Signer()
        refresh['national_id'] = signer.sign(national_id)
        refresh['first_login'] = True
        del refresh['user_id']
        return [str(refresh), str(refresh.access_token)]

    if user.role == "Institution":
        refresh['name'] = user.name
        refresh['role'] = user.role
        refresh['credits'] = user.credits
        refresh['email'] = user.email
    else:
        refresh['full_name'] = user.full_name
        refresh['role'] = user.role

    return [str(refresh), str(refresh.access_token)]
