from django.contrib.auth.hashers import check_password
from django.utils.timezone import timedelta
from django.utils import timezone

from rest_framework import serializers
from rest_framework.exceptions import APIException
from ..models import User, DriverRequest

import secrets, random



class CustomValidationError(APIException):
    status_code = 400
    default_detail = "Validation Error"

    def __init__(self, errors, message="Validation Error"):
        self.detail = {
            "status": "error",
            "message": message,
            "errors": errors
        }


class mobileNumberSerializer(serializers.Serializer):
    mobile_number = serializers.CharField(max_length=18)

    def validate(self, data):
        mobile_number = data["mobile_number"]
        if not mobile_number.startswith("+"):
            errors = {"mobile_number" : "Mobile number must start with a '+' sign for the country code."}
            raise CustomValidationError(errors)

        if not mobile_number[1:].isdigit():
            errors = {"mobile_number": "Mobile number must contain only numeric characters after '+'."}
            raise CustomValidationError(errors)

        if not User.objects.filter(mobile_number=mobile_number).exists():
            errors = {"mobile_number": "Mobile number does not exist!"}
            raise CustomValidationError(errors)


        return data

    def create(self, validated_data):
        mobile_number = validated_data['mobile_number']
        otp = random.randint(1000, 9999)
        user = User.objects.get(
            mobile_number=mobile_number
        )
        user.user_type = 'driver'
        user.otp = otp
        user.otp_created_at = timezone.now().time()
        user.save()
        return {"message": "OTP generated successfully", "mobile_number" : mobile_number, "otp": otp, "user": user}


class OtpVerificationSerializer(serializers.Serializer):
    mobile_number = serializers.CharField(max_length=13)
    otp = serializers.CharField(max_length=4)

    def validate(self, data):
        otp = data["otp"]
        mobile_number = data["mobile_number"]
        user = User.objects.get(mobile_number=mobile_number)
        otp_age = (timezone.now() - timedelta(minutes=2)).time()
        if user.otp_created_at < otp_age:
            errors = {"otp":"OTP has expired. Please request a new one."}
            raise CustomValidationError(errors)

        if not otp.isdigit():
            errors = {"OTP": "OTP must contain only numeric characters."}
            raise CustomValidationError(errors)

        if len(otp) != 4:
            errors = {"OTP": "OTP must be exactly 4 digits long."}
            raise CustomValidationError(errors)

        otp = int(otp)
        user = User.objects.filter(mobile_number = mobile_number).first()

        if DriverRequest.objects.filter(user = user).exists():
            if DriverRequest.objects.filter(user = user, status='pending').exists():
                errors = {"login":  "Your application is under verification."}
                raise CustomValidationError(errors)

        if user.otp != otp:
            errors = {"OTP":  "Invalid OTP."}
            raise CustomValidationError(errors)

        return data


class ResendOtpSerializer(serializers.Serializer):
    mobile_number = serializers.CharField(max_length=15)


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'gender', 'mobile_number', 'user_type')


    def validate(self, data):
        mobile_number = data["mobile_number"]
        if not mobile_number.startswith("+"):
            errors = {"mobile_number": "Mobile number must start with a '+' sign for the country code."}
            raise CustomValidationError(errors)

        if not mobile_number[1:3] == "91" :
            errors = {"mobile_number":  "Mobile number must start with +91."}
            raise CustomValidationError(errors)

        if len(mobile_number[3:]) != 10:
            errors = {"mobile_number": "Mobile number must be exactly 10 digits after the country code."}
            raise CustomValidationError(errors)

        if not mobile_number[1:].isdigit():
            errors = {"mobile_number": "Mobile number must contain only numeric characters after '+'."}
            raise CustomValidationError(errors)

        if User.objects.filter(mobile_number=mobile_number).exists():
            errors = {"mobile_number": "Mobile Number already exists."}
            raise CustomValidationError(errors)

        if data['user_type'] == 'admin':
            errors = {"mobile_number": "You Can't select your self as Admin."}
            raise CustomValidationError(errors)

        return data

    def create(self, validated_data):
        user = User.objects.create(**validated_data)
        user.verification_code = secrets.token_hex(32)
        user.verification_code_created_at = timezone.now()
        otp = random.randint(1000,9999)
        user.otp = otp
        user.otp_created_at = timezone.now().time()
        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, data):
        user = User.objects.filter(email = data['email']).first()
        if not user:
            errors = {"email" : "Email ID does not Exists."}
            raise CustomValidationError({"email": "Email ID does not exist."})

        if user.user_type != "admin":
            errors = {"user_type" : "User type is not admin. Not allowed to login."}
            raise CustomValidationError(errors)

        if not check_password(data['password'], user.password):
            errors = {"password" : "Invalid password or Email Id."}
            raise CustomValidationError(errors)
        return data


class AdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('email', 'role')

    def validate(self, data):
        if not User.objects.filter(email = data["email"]).exists():
            errors = {"email":  "Email not found."}
            raise CustomValidationError(errors)
        return data


class ResetPasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField()
    new_password = serializers.CharField()
    confirm_password = serializers.CharField()

    def validate(self, data):
        user = self.context["user"]
        user = User.objects.get(mobile_number = user)
        if not check_password(data['old_password'], user.password):
            errors = {"password":  "old Password is incorrect."}
            raise CustomValidationError(errors)

        if data['old_password'] == data['new_password']:
            errors = {"password":  "old Password and New Password is same."}
            raise CustomValidationError(errors)

        if data['confirm_password'] != data['new_password']:
            errors = {"password":  "New Password and Confirm Password is not same."}
            raise CustomValidationError(errors)

        return data

    def create(self , validated_data):
        user = User.objects.get(mobile_number = self.context['user'])
        user.set_password(validated_data['new_password'])
        user.save()
        return validated_data


class updateProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'mobile_number', 'gender', 'user_type',]


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate(self, data):
        if not User.objects.filter(email=data['email']).exists():
            errors = {"email":  "Email not found."}
            raise CustomValidationError(errors)

        return data

    def create(self, validated_data):
        user = User.objects.get(email=validated_data['email'])
        user.verification_code = secrets.token_hex(32)
        user.verification_code_created_at = timezone.now()
        user.save()
        return validated_data


class ChangePasswordSerializer(serializers.Serializer):
    password = serializers.CharField(max_length=128)
    confirm_password = serializers.CharField(max_length=128)

    def validate(self, data):
        user = User.objects.get(verification_code=self.context['verification_code'])
        verification_time = user.verification_code_created_at
        if timezone.now() > verification_time + timedelta(days=1):
            errors = {"password": "Reset password link has expired"}
            raise CustomValidationError(errors)

        if not User.objects.filter(verification_code = self.context['verification_code']).exists():
            errors = {"verification_code": "Invalid Reset Key"}
            raise CustomValidationError(errors)

        if data['password'] != data['confirm_password']:
            errors = {"verification_code":  "Password and Confirm Password is not same."}
            raise CustomValidationError(errors)

        return data

    def create(self, validated_data):
        user = User.objects.get(verification_code=self.context['verification_code'])
        user.set_password(validated_data['password'])
        user.save()
        return validated_data


class AdminRightsSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'mobile_number', 'role',)

    def validate(self, data):
        try:
            user = User.objects.get(verification_code=self.context['verification_code'])
        except User.DoesNotExist:
            errors = {"message": "User does not exist"}
            raise CustomValidationError(errors)

        if user.user_type != 'admin':
            errors = {"message": "Cant assign role to non-admin user"}
            raise CustomValidationError(errors)


class AddTeamMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'mobile_number', 'email', 'password', 'gender', 'role',)

    def validate(self, data):
        if User.objects.filter(email = data["email"]).exists():
            errors = {"email":"Email already exist."}
            raise CustomValidationError(errors)

        if User.objects.filter(mobile_number = data["mobile_number"]).exists():
            errors = {"mobile_number":"Mobile number already exist."}
            raise CustomValidationError(errors)

        if data['role'] == None:
            errors = {"Role":"Role is not defined."}
            raise CustomValidationError(errors)

        return data

    def create(self, validated_data):
        user = User.objects.create(**validated_data)
        user.user_type = 'admin'
        user.verification_code = secrets.token_hex(32)
        user.verification_code_created_at = timezone.now()
        return validated_data