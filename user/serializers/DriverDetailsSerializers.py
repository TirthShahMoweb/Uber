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
                    if field_value.size > 5 * 1024:
                        raise serializers.ValidationError(f"{doc_type.document_label} size must be less than or equal to 5 KB.")
                    document = DocumentRequired.objects.create(
                    document_name=doc_type, document_image=field_value)

                if doc_type.field_type == "text":
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


class DocumentRequiredSerializer(serializers.ModelSerializer):
    document_name = serializers.CharField(source='document_name.document_label')  # Directly use document_label

    class Meta:
        model = DocumentRequired
        fields = ['id', 'document_text', 'document_image', 'document_name']


class VerificationPendingSerializer(serializers.ModelSerializer):
    driver_name = serializers.CharField()
    profile_pic = serializers.ImageField(source = 'user.profile_pic')
    verification_documents = DocumentRequiredSerializer(many=True)

    class Meta:
        model = DriverDetail
        fields = ('id', 'driver_name', 'verification_documents' , 'profile_pic' ,'dob')
        ref_name = "DriverDetailsVerificationPending"
        depth = 2

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['approval_url'] = reverse('driver-verification-approval', args=[instance.id])
        return representation


class ResubmissionSerializer(serializers.ModelSerializer):
    aadhar_photo = serializers.ImageField(required=False)
    licence_number = serializers.CharField(required=False)
    profile_pic = serializers.ImageField(required=False)

    class Meta:
        model = DriverDetail
        fields = ('aadhar_photo', 'licence_number', 'dob', 'profile_pic')

    def validate(self, data):
        if DriverDetail.objects.filter(user=self.context['user'], status='pending').exists():
                raise serializers.ValidationError("You have already resubmitted your data. You cannot apply again.")
        return data