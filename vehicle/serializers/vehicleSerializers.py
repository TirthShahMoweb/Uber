from django.urls import reverse

from rest_framework import serializers

from ..models import Vehicle, VehicleRequest, DocumentType
from user.models import DriverDetail



class VehicleSerializer(serializers.ModelSerializer):

    class Meta:
        model = VehicleRequest
        fields = ('vehicle_number', 'vehicle_type', 'vehicle_chassis_number', 'vehicle_engine_number',)


class VehicleImageSerializer(serializers.Serializer):
    vehicle_front_image = serializers.ImageField(required=True)
    vehicle_back_image = serializers.ImageField(required=True)
    vehicle_leftSide_image = serializers.ImageField(required=True)
    vehicle_rightSide_image = serializers.ImageField(required=True)
    vehicle_rc_front_image = serializers.ImageField(required=True)
    vehicle_rc_back_image = serializers.ImageField(required=True)
    vehicle_number = VehicleSerializer().fields['vehicle_number']
    vehicle_type = VehicleSerializer().fields['vehicle_type']
    vehicle_chassis_number = VehicleSerializer().fields['vehicle_chassis_number']
    vehicle_engine_number = VehicleSerializer().fields['vehicle_engine_number']

    def validate(self, data):
        user = self.context.get('user')
        try:
            driver = DriverDetail.objects.get(user=user)
        except DriverDetail.DoesNotExist:
            raise serializers.ValidationError("Driver details not found for this user.")

        vehicle_number = VehicleRequest.objects.all().values_list('vehicle_number', flat=True)
        if data['vehicle_number'] in vehicle_number:
            errors = {'vehicle_number': 'Vehicle number already exists.'}
            raise serializers.ValidationError(errors)

        vehicle_number = data['vehicle_number']
        if not vehicle_number:
            errors = {'vehicle_number': 'vehicle_number is required.'}
            raise serializers.ValidationError(errors)

        if len(vehicle_number) != 10:
            errors = {'vehicle_number': 'Vehicle number must be 10 characters long.'}
            raise serializers.ValidationError(errors)

        vehicle_type = data.get('vehicle_type')
        if not vehicle_type:
            errors = {'vehicle_type': 'vehicle_type is required.'}
            raise serializers.ValidationError(errors)

        vehicle_chassis_number = data.get('vehicle_chassis_number')
        if not vehicle_chassis_number:
            errors = {'vehicle_chassis_number': 'vehicle_chassis_number is required.'}
            raise serializers.ValidationError(errors)

        if len(vehicle_chassis_number) != 17:
            errors = {'vehicle_chassis_number': 'Vehicle chassis number must be 17 characters long.'}
            raise serializers.ValidationError(errors)

        if not vehicle_chassis_number.isalnum():
            errors = {'vehicle_chassis_number': 'Vehicle chassis number must contain only alphanumeric characters.'}
            raise serializers.ValidationError(errors)

        vehicle_engine_number = data.get('vehicle_engine_number')
        if not vehicle_engine_number:
            errors = {'vehicle_engine_number': 'vehicle_engine_number is required.'}
            raise serializers.ValidationError(errors)

        required_documents = [
            'vehicle_front_image', 'vehicle_back_image',
            'vehicle_leftSide_image', 'vehicle_rightSide_image',
            'vehicle_rc_front_image', 'vehicle_rc_back_image',
        ]

        for document_type in required_documents:
            if document_type not in data:
                errors = {document_type: f"{document_type} is required."}
                raise serializers.ValidationError(errors)

            if data[document_type].size > 5 * 1024 * 1024:
                errors = {document_type: f"{document_type} size exceeds 5MB."}
                raise serializers.ValidationError(errors)

            if data[document_type].content_type not in ['image/jpeg', 'image/png', 'image/jpg', 'image/webp']:
                errors = {document_type: f"{document_type} must be a JPEG, PNG, JPG or WEBP image."}
                raise serializers.ValidationError(errors)

        return data

    def create(self, validated_data):
        user = self.context['user']
        driver = DriverDetail.objects.get(user=user)
        required_documents = [
            'vehicle_front_image', 'vehicle_back_image',
            'vehicle_leftSide_image', 'vehicle_rightSide_image',
            'vehicle_rc_front_image', 'vehicle_rc_back_image',]
        documents = []
        for document_type in required_documents:
            doc = DocumentType.objects.create(
                document_type = document_type,
                document_image = validated_data[document_type],
                document_name = str(validated_data[document_type]),
                document_size = validated_data[document_type].size,
                document_mime_type = validated_data[document_type].content_type
            )
            documents.append(doc)

        vehicle_request = VehicleRequest.objects.create(driver=driver)
        vehicle_request.vehicle_number = validated_data['vehicle_number']
        vehicle_request.vehicle_type = validated_data['vehicle_type']
        vehicle_request.vehicle_chassis_number = validated_data['vehicle_chassis_number']
        vehicle_request.vehicle_engine_number = validated_data['vehicle_engine_number']
        vehicle_request.verification_documents.set(documents)
        vehicle_request.save()
        return vehicle_request


class AdminVehicleStatusListSerailzier(serializers.ModelSerializer):
    name = serializers.CharField(read_only=True)

    class Meta:
        model = VehicleRequest
        fields = ('id', 'name', 'vehicle_number', 'vehicle_type', 'status', 'created_at')


class VehicleListViewSerializer(serializers.ModelSerializer):
    name = serializers.CharField(read_only=True)

    class Meta:
        model = VehicleRequest
        fields = ('id', 'name', 'vehicle_number', 'vehicle_type', 'status', 'created_at', 'action_at',)


class VehicleDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentType
        fields = ['id', 'document_type', 'document_image']


class VehicleDetailsSerializer(serializers.ModelSerializer):
    documents = VehicleDocumentSerializer(many=True, source='verification_documents')
    action_by = serializers.CharField(source='action_by.get_full_name', allow_null=True)

    class Meta:
        model = VehicleRequest
        fields = ('vehicle_number', 'vehicle_type', 'vehicle_chassis_number', 'vehicle_engine_number', 'documents',
                  'status', 'action_at', 'rejection_reason', 'action_by')


class AdminVehicleApprovalSerializer(serializers.Serializer):
    is_approved = serializers.CharField(required = False)
    rejection_reason = serializers.CharField(required = False)


class DraftVehicleListViewSerializer(serializers.ModelSerializer):
    name = serializers.CharField(read_only=True)
    mobile_number = serializers.CharField(source='user.mobile_number', read_only=True)

    class Meta:
        model = DriverDetail
        fields = ('id', 'name', 'mobile_number', 'created_at', 'verified_at',)


class DriverVehiclesListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehicle
        fields = ('id', 'vehicle_number', 'vehicle_type')


class SelectVehilceSerializer(serializers.Serializer):
    vehicle_id = serializers.IntegerField(required=True)


# class ResubmissionVehicleSeralizer(serializers.ModelSerializer):
#     class Meta:
#         model = Vehicle
#         fields = ('vehicle_image', 'vehicle_rc', 'vehicle_type',)


# class ResubmissionVehicleSeralizer(serializers.ModelSerializer):
#     class Meta:
#         model = Vehicle
#         fields = ('vehicle_image', 'vehicle_rc', 'vehicle_type',)


# class DisplayVehicleSerializer(serializers.ModelSerializer):
    # class Meta:
    #     model = Vehicle
    #     # fields = '__all__'
    #     fields = ('id','driver','vehicle_image', 'vehicle_rc', 'vehicle_type',)

    # def to_representation(self, instance):
    #     representation = super().to_representation(instance)
    #     request = self.context['request']
    #     representation['vehicle_url'] = reverse('Select_vehicle', args=[instance.id])
    #     return representation