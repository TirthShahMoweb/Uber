from rest_framework import status
from rest_framework.authentication import authenticate
from rest_framework.generics import RetrieveUpdateAPIView, CreateAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated, BasePermission

from ..models import User, Role, Permission, RolePermission
from ..serializers.UserSerializers import AdminRightsSerializer, AddTeamMemberSerializer, OtpVerificationSerializer, mobileNumberSerializer, AdminSerializer, updateProfileSerializer, ChangePasswordSerializer, ForgotPasswordSerializer, CustomUserSerializer, ResetPasswordSerializer , LoginSerializer
from Uber import settings

from django.core.mail import send_mail



class CanEditTeamMember(BasePermission):
    """
    Custom permission to allow only SuperAdmin to give Admin rights to user.
    """
    def has_permission(self, request, view):
        user = request.user
        user_type = user.user_type
        role = request.user.role
        if user_type != 'admin':
            return False

        permissions = RolePermission.objects.filter(role=role).first().permissions.values_list('permission_name', flat=True)
        required_permissions = "edit_team_member"
        if bool(required_permissions in list(permissions)):
            return True
        return False


class adminRights(RetrieveUpdateAPIView):
    '''
        Give rights to admin.
    '''
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, CanEditTeamMember]
    serializer_class = AdminRightsSerializer
    lookup_field = 'verification_code'

    def get_queryset(self):
        return User.objects.filter(verification_code=self.kwargs['verification_code'], user_type='admin')

    def get(self, request, *args, **kwargs):
        user = self.get_object()
        data = {
            "first_name": user.first_name,
            "last_name": user.last_name,
            "mobile_number": user.mobile_number,
            "role": user.role.role_name
        }
        return Response({"status": "success", "data": data}, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        verification_code = kwargs.get('verification_code', None)

        try:
            user = User.objects.get(verification_code=verification_code)
        except User.DoesNotExist:
            return Response({"status": "error", "message": "User not found with this verification code."}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            data = {
                "first_name": user.first_name,
                "last_name": user.last_name,
                "mobile_number": user.mobile_number,
                "role": user.role.name
            }
            return Response({"status": "success", "data": data}, status=status.HTTP_200_OK)
        else:
            return Response({"status": "error", "error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


# class AssignAdminRoleView(APIView):
#     '''
#         Assigning the Admin role to the associated user.
#     '''
#     authentication_classes = [JWTAuthentication]
#     permission_classes = [IsAuthenticated, IsHavingAdminRights]

#     def post(self, request):
#         try:
#             email = request.data["email"]
#             user = User.objects.get(email=email)
#         except User.DoesNotExist:
#             return Response({
#                         "status" : "error",
#                         "message" : "User not found"
#                         }, status=status.HTTP_404_NOT_FOUND)
#         serializer = AdminSerializer(user, data = request.data, partial=True)
#         if serializer.is_valid():
#             serializer.save()
#             user.user_type = 'admin'
#             user.save()
#             data = {"message": "Admin role updated successfully."}
#             return Response({"status" : "success" ,"data": data }, status=status.HTTP_200_OK)
#         return Response({"status" : "error","error" : serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class LoginView(CreateAPIView):
    '''
        Login API for user using CreateAPIView
    '''
    serializer_class = LoginSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']
            user = User.objects.filter(email=email).first()
            role_permissions = RolePermission.objects.filter(role=user.role)
            permissions = Permission.objects.filter(permissions__in=role_permissions).values('permission_name')
            if not user:
                return Response({
                    "status": "error",
                    "message": "Invalid Credentials."
                }, status=status.HTTP_400_BAD_REQUEST)

            refresh = RefreshToken.for_user(user)
            data = {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "permissions" : permissions
                # "role" : user.role

            }

            return Response({
                "status": "success",
                "data": data
            }, status=status.HTTP_200_OK)

        return Response({
            "status": "error",
            "error": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class Mobile_Number(CreateAPIView):
    '''
        Check if the user is logged in or not.
    '''
    serializer_class = mobileNumberSerializer

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            validated_data = serializer.validated_data
            result = serializer.save()

            data = {
                "data" : result["mobile_number"],
                "otp" : result['otp'],
                "message": result["message"]
            }
            return Response({
                "status": "success",
                "data": data,
            }, status=status.HTTP_200_OK)
        return Response({
            "status": "error",
            "error": serializer.errors,
        }, status=status.HTTP_400_BAD_REQUEST)


class AddTeamMemberView(CreateAPIView):

    serializer_class = AddTeamMemberSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, ]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            data = {
                "message": "Team Member added successfully.",
                "data": serializer.data
            }

            return Response({
                "status": "success",
                "data": data
            }, status=status.HTTP_201_CREATED)

        return Response({
            "status": "error",
            "error": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class OtpVerificationView(CreateAPIView):
    '''
        OTP verification using CreateAPIView.
    '''
    serializer_class = OtpVerificationSerializer  # Assign the serializer class

    def create(self, request, *args, **kwargs):
        data = request.data

        serializer = self.get_serializer(data=data)

        if serializer.is_valid():

            user = User.objects.filter(mobile_number = data['mobile_number']).first()
            refresh = RefreshToken.for_user(user)
            response_data = {"message": "OTP verify successfully"}
            return Response({
                "status": "success",
                "data": response_data,
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            }, status=status.HTTP_200_OK)

        return Response({
            "status": "error",
            "error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class SignupView(CreateAPIView):
    '''
        Signup API for User using CreateAPIView
    '''
    serializer_class = CustomUserSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()

            data = {
                "message": "Signup successful",
                "data": serializer.data
            }

            return Response({
                "status": "success",
                "data": data
            }, status=status.HTTP_201_CREATED)

        return Response({
            "status": "error",
            "error": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


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

    def get_object(self):
        return self.request.user


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