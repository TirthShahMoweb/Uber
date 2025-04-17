from rest_framework.generics import ListAPIView
from rest_framework.filters import SearchFilter, OrderingFilter
from ..serializers.languageSerializers import LanguageListSerializer
from ..models import Language



class LanguageListView(ListAPIView):

    serializer_class = LanguageListSerializer
    queryset = Language.objects.all()

    filter_backends = [SearchFilter]
    search_fields = ['name']
