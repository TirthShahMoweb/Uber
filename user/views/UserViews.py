from rest_framework import status
from rest_framework.authentication import authenticate
from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated, BasePermission

from ..models import User, AdminPermission, Role, Permission
from ..serializers.UserSerializers import OtpVerificationSerializer, mobileNumberSerializer, AdminSerializer, updateProfileSerializer, ChangePasswordSerializer, ForgotPasswordSerializer, CustomUserSerializer, ResetPasswordSerializer , LoginSerializer
from Uber import settings

from django.core.mail import send_mail


class IsHavingAdminRights(BasePermission):
    """
    Custom permission to allow only SuperAdmin to give Admin rights to user.
    """
    def has_permission(self, request, view):
        user = request.user
        role = request.user.role
        permissions = AdminPermission.objects.filter(role=role).first().permissions.values_list('permission_name', flat=True)
        required_permissions = {"Assign Admin Role"}
        if bool(set(permissions) and required_permissions):
            return True
        return user and user.is_superuser


# class adminRights(APIView):
#     '''
#         Give rights to admin.
#     '''
#     authentication_classes = [JWTAuthentication]
#     permission_classes = [IsAuthenticated, IsHavingAdminRights]

#     def post(self, request):
#         try:
#             role_name = request.data["role_name"]
#             role = Roles.objects.get(role_name=role_name)
#         except Roles.DoesNotExist:
            # return Response({"status" : "error", "message" : "Role does not exist"}, status=status.HTTP_404_NOT_FOUND)

#         permission_name = "Assign Admin Role"
#         permission = Permissions.objects.get(permission_name=permission_name)

#         serializer = AdminRightsSerializer(role, data = request.data, context={'permission':permission}, partial=True)
#         if serializer.is_valid():
#             serializer.save()


class AssignAdminRoleView(APIView):
    '''
        Assigning the Admin role to the associated user.
    '''
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsHavingAdminRights]

    def post(self, request):
        try:
            email = request.data["email"]
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({
                        "status" : "error",
                        "message" : "User not found"
                        }, status=status.HTTP_404_NOT_FOUND)
        serializer = AdminSerializer(user, data = request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            user.user_type = 'admin'
            user.save()
            data = {"message": "Admin role updated successfully."}
            return Response({"status" : "success" ,"data": data }, status=status.HTTP_200_OK)
        return Response({"status" : "error","error" : serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class Login(APIView):

    def post(self, request):
        '''
            Login API for user
        '''
        data = request.data
        serializer = LoginSerializer(data=data)

        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']

        user = authenticate(email=email, password=password)
        if not user:
                    return Response({"status" : "error","message" : "Invalid Credentials."}, status=status.HTTP_400_BAD_REQUEST)

        refresh = RefreshToken.for_user(user)
        data = { "refresh": str(refresh),
                "access": str(refresh.access_token)}
        return Response({
                "status" : "success",
                "data" : data
        }, status=status.HTTP_200_OK)


class Mobile_Number(APIView):
    '''
        Check if the user is logged in or not.
    '''
    def post(self, request):
        serializer = mobileNumberSerializer(data=request.data)
        if serializer.is_valid():
            validated_data = serializer.validated_data
            result = serializer.save()
            user = result["user"]
            refresh = RefreshToken.for_user(user)
            data = {
                "message" : result["message"], "refresh" : str(refresh), "access" : str(refresh.access_token)}
            return Response({
                "status" : "success",
                "data" : data
            }, status=status.HTTP_200_OK)

        return Response({"status" : "error", "error" : serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class OtpVerification(APIView):

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        '''
            OTP verification
        '''
        user = request.user
        data = request.data
        if not user or not user.is_authenticated:
            return Response({"status" : "error","message" : "Unauthorized access. Please provide a valid token."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = OtpVerificationSerializer(data = data, context={'user':user})
        if serializer.is_valid():
            data = {"message": "OTP verify successfully"}
            return Response({"status" : "success","data" : data})
        return Response({"status" : "error","error" : serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class Signup(APIView):

    def post(self,request):
        '''
            Signup API for User
        '''
        data = request.data
        serializer = CustomUserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            data = {"message": "Signup successful","data": serializer.data,"refresh": str(refresh),"access": str(refresh.access_token)}
            return Response({
                "status" : "success","data" : data}, status=status.HTTP_201_CREATED)

        return Response({"status" : "error","error" : serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class ResetPassword(APIView):

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        '''
            Reset Password
        '''
        user = request.user
        try:
            user = User.objects.get(mobile_number = user)
        except User.DoesNotExist:
            return Response({"status" : "error","message" : "User not Found."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = ResetPasswordSerializer(data=request.data, partial=True, context={'user':user})
        if serializer.is_valid():
            serializer.save()
            data = { "message": "Password updated successfully"}
            return Response({"status" : "success", "data" : data}, status=status.HTTP_200_OK)
        return Response({"status" : "error","error" : serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class updateprofile(RetrieveUpdateAPIView):
    '''
        Update Profile
    '''
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    serializer_class = updateProfileSerializer

    def get_queryset(self):

        user = self.request.user
        try:
            user = User.objects.get(user=user)
        except User.DoesNotExist:
            return Response({"status" : "error", "message" : "User not Found."}, status=status.HTTP_400_BAD_REQUEST)

        return User.objects.filter(mobile_number = user)


class forgot_password(APIView):

    def post(self, request):
        '''
            Forgot Password
        '''
        data = request.data
        serializer = ForgotPasswordSerializer(data=data)
        if serializer.is_valid():
            user = serializer.save()
            user = User.objects.get(email=user['email'])
            verification_code = user.verification_code
            link = f"http://127.0.0.1:8000/forgot-password/{verification_code}/"
            subject = "Reset password link"
            message = f'''
                        Click on the link to reset your password
                        {link}
                        '''
            user_email = [data['email']]

            send_mail(subject, message, settings.EMAIL_HOST_USER, user_email)
            data = {"message": "Reset password link sent to your email"}
            return Response({"status" : "success", "data": data}, status=status.HTTP_200_OK)
        return Response({"status" : "error", "error" : serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class change_password(APIView):

    def post(self, request, verification_code=None):
        '''
            Change Password
        '''
        data = request.data
        serializer = ChangePasswordSerializer(data=data, context={'verification_code':verification_code})
        if serializer.is_valid():
            serializer.save()
            data = {"message" : "Password changed successfully"}
            return Response({"status" : "success", "data" : data}, status=status.HTTP_200_OK)
        return Response({"status" : "error", "error" : serializer.errors}, status=status.HTTP_400_BAD_REQUEST)