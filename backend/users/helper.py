from datetime import timedelta, datetime
import datetime as dt
import os
from django.utils import timezone
from random import random
from django.core.signing import Signer
from django.core.mail import send_mail
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from rest_framework_simplejwt.settings import api_settings
import random


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
    # Check if OTP exists and is not expired
    if user.otp_created_at and user.otp_created_at + timedelta(minutes=user.otp_expiry_time_minutes) > timezone.now():
        return True

    # Generate new OTP
    otp = str(random.randint(100000, 999999))
    user.otp = otp
    user.otp_created_at = timezone.now()
    user.save()

    return True


def generateTokens(user):
    refresh = RefreshToken.for_user(user)

    if not user.email:
        access = AccessToken.for_user(user)

        national_id = user.national_id
        signer = Signer()

        del access['user_id']
        access['national_id'] = signer.sign(national_id)
        access['first_login'] = True
        access['exp'] = int(
            (datetime.now() + timedelta(minutes=10)).timestamp())

        return [str(access), None]

    if user.role == "Institution":
        refresh['name'] = user.name
        refresh['credits'] = user.credits
    else:
        refresh['name'] = user.full_name

    refresh['role'] = user.role
    refresh['email'] = user.email

    return [str(refresh), str(refresh.access_token)]
