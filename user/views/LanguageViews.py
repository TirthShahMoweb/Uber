from rest_framework.generics import ListAPIView

from ..serializers.LanguageSerializers import LanguageListSerializer
from ..models import Language



class LanguageListView(ListAPIView):

    serializer_class = LanguageListSerializer
    queryset = Language.objects.all()