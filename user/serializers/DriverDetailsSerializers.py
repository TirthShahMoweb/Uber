from django.urls import reverse

from rest_framework import serializers

from ..models import DriverDetail, DocumentRequired, User, DocumentType



class VerificationRequestSerializer(serializers.ModelSerializer):
    profile_pic = serializers.ImageField()

    class Meta:
        model = DriverDetail
        fields = ('dob', 'lang','profile_pic')

    def validate(self, data):
        if DriverDetail.objects.filter(user=self.context['user']).exists():
            raise serializers.ValidationError("You have already applied as a driver. You cannot apply again.")
        return data

    def create(self, validated_data):

        if validated_data["profile_pic"]:
            user = User.objects.filter(mobile_number=self.context['user']).first()
            user.profile_pic = validated_data["profile_pic"]
            user.save()

        documentType = DocumentType.objects.filter(deleted_at = None)
        documents = []
        for doc_type in documentType:
            field_name = doc_type.document_key
            data = self.initial_data
            if field_name in data:
                field_value = data[field_name]

                if doc_type.field_type == "image":
                    if type(field_value) is str:
                        raise serializers.ValidationError(f"{doc_type.document_label} must be an image.")

                    if field_value.size > 5 * 1024 * 1024 :
                        raise serializers.ValidationError(f"{doc_type.document_label} size must be less than or equal to 5 KB.")

                    document = DocumentRequired.objects.create(
                    document_name=doc_type, document_image=field_value)

                if doc_type.field_type == "text":
                    if type(field_value) is not str:
                        raise serializers.ValidationError(f"{doc_type.document_label} must be a string.")

                    document = DocumentRequired.objects.create(
                    document_name=doc_type, document_text=field_value)
                documents.append(document)
            elif doc_type.is_required:
                raise serializers.ValidationError(f"{doc_type.document_label} is Required.")

        driver = DriverDetail.objects.create(user=self.context['user'], dob=validated_data["dob"])

        if validated_data["lang"]:
            driver.lang.set(validated_data["lang"])

        driver.verification_documents.add(*documents)

        driver.save()
        return driver


class DocumentTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentType
        fields = ('document_key', 'document_label', 'field_type', 'is_required',)


class DriverSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source = 'user.first_name')
    last_name = serializers.CharField(source = 'user.last_name')
    mobile_number = serializers.CharField(source = 'user.mobile_number')
    class Meta:
        model = DriverDetail
        fields = ('id', 'first_name', 'last_name', 'mobile_number' , 'created_at', 'verified_at')


class DocumentRequiredSerializer(serializers.ModelSerializer):
    document_name = serializers.CharField(source='document_name.document_label')

    class Meta:
        model = DocumentRequired
        fields = ['id', 'document_text', 'document_image', 'document_name']


class DriverDraftSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'mobile_number','created_at',)

class AdminDriverApprovalSerializer(serializers.Serializer):
    is_approved = serializers.CharField(required = False)
    rejection_reason = serializers.CharField(required = False)


class DriverVerificationPendingSerializer(serializers.ModelSerializer):
    mobile_number = serializers.CharField(source = 'user.mobile_number')
    verification_code = serializers.CharField(source = 'user.verification_code')
    first_name = serializers.CharField(source = 'user.first_name')
    last_name = serializers.CharField(source = 'user.last_name')

    class Meta:
        model = DriverDetail
        fields = ('id', 'first_name', 'last_name', 'mobile_number' , 'status', 'created_at', 'verification_code')
        # ref_name = "DriverDetailsVerificationPending"
        # depth = 2

    # def to_representation(self, instance):
    #     representation = super().to_representation(instance)
    #     representation['approval_url'] = reverse('driver-verification-approval', args=[instance.id])
    #     return representation


class DriverDetailsApprovalPendingSerializer(serializers.ModelSerializer):
    profile_pic = serializers.ImageField(source = 'user.profile_pic')
    mobile_number = serializers.CharField(source = 'user.mobile_number')
    first_name = serializers.CharField(source = 'user.first_name')
    last_name = serializers.CharField(source = 'user.last_name')
    verification_documents = DocumentRequiredSerializer(many=True)

    class Meta:
        model = DriverDetail
        fields = ('mobile_number', 'first_name', 'last_name', 'verification_documents', 'profile_pic', 'status', 'created_at', 'rejection_reason')
        depth = 1

class ResubmissionSerializer(serializers.ModelSerializer):
    aadhar_photo = serializers.ImageField(required=False)
    licence_number = serializers.CharField(required=False)
    profile_pic = serializers.ImageField(required=False)

    class Meta:
        model = DriverDetail
        fields = ( 'dob', 'profile_pic')

    def validate(self, data):
        if DriverDetail.objects.filter(user=self.context['user'], status='pending').exists():
                raise serializers.ValidationError("You have already resubmitted your data. You cannot apply again.")
        return data

    def create(self, validated_data):
        if validated_data["profile_pic"]:
            user = User.objects.filter(mobile_number=self.context['user']).first()
            user.profile_pic = validated_data["profile_pic"]
            user.save()

        documentType = DocumentType.objects.filter(deleted_at = None)
        documents = []
        for doc_type in documentType:
            field_name = doc_type.document_key
            data = self.initial_data
            if field_name in data:
                field_value = data[field_name]

                if doc_type.field_type == "image":
                    if type(field_value) is str:
                        raise serializers.ValidationError(f"{doc_type.document_label} must be an image.")

                    if field_value.size > 5 * 1024 * 1024 :
                        raise serializers.ValidationError(f"{doc_type.document_label} size must be less than or equal to 5 KB.")

                    document = DocumentRequired.objects.create(
                    document_name=doc_type, document_image=field_value)

                if doc_type.field_type == "text":
                    if type(field_value) is not str:
                        raise serializers.ValidationError(f"{doc_type.document_label} must be a string.")

                    document = DocumentRequired.objects.create(
                    document_name=doc_type, document_text=field_value)
                documents.append(document)
            elif doc_type.is_required:
                raise serializers.ValidationError(f"{doc_type.document_label} is Required.")

        driver = DriverDetail.objects.get(user=self.context['user'])

        if validated_data["lang"]:
            driver.lang.set(validated_data["lang"])
        driver.verification_documents.add(*documents)

        driver.save()
        return driver
