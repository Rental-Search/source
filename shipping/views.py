# coding=utf-8
from django.http.response import Http404
from rest_framework.decorators import link
from rest_framework.response import Response
from eloue.api import filters, mixins, viewsets
from . import helpers, models, serializers


class ShippingPointViewSet(viewsets.SimpleViewSet):
    """
    API endpoint that allows shipping points to be viewed.
    """

    serializer_class = serializers.ShippingPointSerializer

    def list(self, request, *args, **kwargs):
        params = serializers.ShippingPointListParamsSerializer(data=request.QUERY_PARAMS)
        if params.is_valid():
            params = params.data
            lat = params['lat']
            lng = params['lng']
            if lat is None or lng is None:
                lat, lng = helpers.get_position(params['address'])
            shipping_points = helpers.get_shipping_points(lat, lng, params['search_type'])
            result = self.serializer_class(data=shipping_points, many=True)
            if result.is_valid():
                return Response(result.data)
        return Response([])

    def retrieve(self, request, *args, **kwargs):
        params = serializers.ShippingPointRetrieveParamsSerializer(data=request.QUERY_PARAMS)
        if params.is_valid():
            params = params.data
            shipping_point = helpers.get_shipping_point(
                int(kwargs['pk']), params['lat'], params['lng'], params['search_type'])
            if shipping_point:
                result = self.serializer_class(data=shipping_point)
                if result.is_valid():
                    return Response(result.data)
        raise Http404


class PatronShippingPointViewSet(mixins.SetOwnerMixin, viewsets.NonEditableModelViewSet):
    """
    API endpoint that allows patron's shipping points to be viewed or edited.
    """
    serializer_class = serializers.PatronShippingPointSerializer
    queryset = models.PatronShippingPoint.objects.select_related('patron')
    filter_backends = (filters.OwnerFilter, filters.DjangoFilterBackend)
    owner_field = 'patron'
    filter_fields = ('patron', )


class ProductShippingPointViewSet(mixins.SetOwnerMixin, viewsets.NonEditableModelViewSet):
    """
    API endpoint that allows product's shipping points to be viewed or edited.
    """
    serializer_class = serializers.ProductShippingPointSerializer
    queryset = models.ProductShippingPoint.objects.select_related('product')
    filter_backends = (filters.OwnerFilter, filters.DjangoFilterBackend)
    owner_field = 'product__owner'
    filter_fields = ('product', )


class ShippingViewSet(viewsets.NonEditableModelViewSet):
    """
    API endpoint that allows shippings to be viewed or edited.
    """
    serializer_class = serializers.ShippingSerializer
    queryset = models.Shipping.objects.select_related('departure_point', 'arrival_point', 'booking')
    filter_backends = (filters.OwnerFilter, filters.DjangoFilterBackend)
    owner_field = ('booking__owner', 'booking__borrower')
    filter_fields = ('booking', )
