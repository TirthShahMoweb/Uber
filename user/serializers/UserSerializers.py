from django.contrib.auth.hashers import check_password
from django.utils.timezone import timedelta
from django.utils import timezone

from rest_framework import serializers
from ..models import User, AdminPermission, Permission

import secrets, random



class mobileNumberSerializer(serializers.Serializer):
    mobile_number = serializers.CharField(max_length=18)

    def validate(self, data):
        mobile_number = data["mobile_number"]
        if not mobile_number.startswith("+"):
            raise serializers.ValidationError({"status" : "error", "message" : "Mobile number must start with a '+' sign for the country code."})

        if not mobile_number[1:].isdigit():
            raise serializers.ValidationError({"status" : "error", "message" : "Mobile number must contain only numeric characters after '+'."})

        if not User.objects.filter(mobile_number=mobile_number).exists():
            raise serializers.ValidationError({"status" : "error", "message" : "Mobile number does not exist. Proceed to signup."})

        return data

    def create(self, validated_data):
        mobile_number = validated_data['mobile_number']
        otp = random.randint(0000, 9999)

        user, created = User.objects.get_or_create(
            mobile_number=mobile_number
        )
        user.user_type = 'driver'
        user.otp = otp
        user.save()

        return {"message": "OTP generated successfully", "otp": otp, "user": user}


class OtpVerificationSerializer(serializers.Serializer):
    otp = serializers.CharField(max_length=4)

    def validate(self, data):
        user = self.context["user"]
        otp = data["otp"]
        if not otp.isdigit():
            raise serializers.ValidationError({"status" : "error", "message" : "OTP must contain only numeric characters."})

        # Check if OTP is exactly 4 digits
        if len(otp) != 4:
            raise serializers.ValidationError({"status" : "error", "message" : "OTP must be exactly 4 digits long."})

        otp = int(otp)
        print(otp,type(otp))

        user = User.objects.filter(mobile_number = user).first()

        if user.otp != otp:
            raise serializers.ValidationError({"status" : "error", "message" : "Invalid OTP."})


        return data


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'gender', 'mobile_number', 'user_type')


    def validate(self, data):
        # if User.objects.filter(email=data['email']).exists():
        #     raise serializers.ValidationError({"email": "Email already exists"})

        if User.objects.filter(mobile_number=data['mobile_number']).exists():
            raise serializers.ValidationError({"status" : "error", "message" : "Mobile Number already exists."})
        # if data['user_type'] == 'driver':
            # if not data['profile_pic']:
            #     raise serializers.ValidationError({"profile_pic": "Profile Pic is required for Driver"})

        # if data['user_type'] == 'driver' or data['user_type'] == 'customer':
        #     if data['role']:
        #         raise serializers.ValidationError({"role": "Role is only for Admin."})

        if data['user_type'] == 'admin':
            raise serializers.ValidationError({"status" : "error", "message" : "You Can't select your self as Admin."})

        return data

    def create(self, validated_data):
        # password = validated_data.pop('password')
        # profile_pic = validated_data.pop('profile_pic', None)
        user = User.objects.create(**validated_data)
        user.verification_code = secrets.token_hex(32)
        user.verification_code_created_at = timezone.now()
        # user.set_password(password)

        # if profile_pic:
        #     user.profile_pic = profile_pic

        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()


class AdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('email', 'role')

    def validate(self, data):
        if not User.objects.filter(email = data["email"]).exists():
            raise serializers.ValidationError({"status" : "error", "message" : "Email not found."})
        return data


class ResetPasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField()
    new_password = serializers.CharField()
    confirm_password = serializers.CharField()

    def validate(self, data):
        user = self.context["user"]
        user = User.objects.get(mobile_number = user)
        if not check_password(data['old_password'], user.password):
            raise serializers.ValidationError({"status" : "error", "message" : "old Password is incorrect."})

        if data['old_password'] == data['new_password']:
            raise serializers.ValidationError({"status" : "error", "message" : "old Password and New Password is same."})


        if data['confirm_password'] != data['new_password']:
            raise serializers.ValidationError({"status" : "error", "message" : "New Password and Confirm Password is not same."})

        return data

    def create(self , validated_data):
        user = User.objects.get(mobile_number = self.context['user'])
        user.set_password(validated_data['new_password'])
        user.save()
        return validated_data


class updateProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'mobile_number', 'gender', 'user_type','profile_pic']


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate(self, data):
        if not User.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError({"status" : "error", "message" : "Email not found."})

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
            raise serializers.ValidationError({"status" : "error", "message" : "Reset password link has expired"})

        if not User.objects.filter(verification_code = self.context['verification_code']).exists():
            raise serializers.ValidationError({"status" : "error", "message" : "Invalid Reset Key"})

        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError({"status" : "error", "message" : "Password and Confirm Password is not same."})

        return data

    def create(self, validated_data):
        user = User.objects.get(verification_code=self.context['verification_code'])
        user.set_password(validated_data['password'])
        user.save()
        return validated_data


# class AdminRightsSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = AdminPermissions
#         fields = ('role_name',)