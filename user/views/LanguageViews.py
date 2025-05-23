from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.generics import ListAPIView

from ..models import Language
from ..serializers.languageSerializers import LanguageListSerializer


class LanguageListView(ListAPIView):
    '''
        Language List
    '''
    serializer_class = LanguageListSerializer
    queryset = Language.objects.all()

    filter_backends = [SearchFilter]
    search_fields = ['name']
