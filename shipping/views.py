# coding=utf-8
from django.http.response import Http404
from rest_framework.decorators import link
from rest_framework.response import Response
from eloue.api import filters, mixins, viewsets
from . import helpers, models, serializers
from eloue.api.decorators import user_required


class ShippingPointViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows shipping points to be viewed.
    """

    serializer_class = serializers.ShippingPointSerializer
    pudo_serializer_class = serializers.PudoSerializer
    queryset = models.ShippingPoint.objects.all()
    filter_backends = (filters.OwnerFilter, filters.DjangoFilterBackend)
    owner_field = ('patronshippingpoint__patron', 'productshippingpoint__product__owner')

    def list(self, request, *args, **kwargs):
        params = serializers.ShippingPointListParamsSerializer(data=request.QUERY_PARAMS)
        if params.is_valid():
            params = params.data
            lat = params['lat']
            lng = params['lng']
            if lat is None or lng is None:
                lat, lng = helpers.get_position(params['address'])
            shipping_points = helpers.get_shipping_points(lat, lng, params['search_type'])
            result = self.pudo_serializer_class(data=shipping_points, many=True)
            if result.is_valid():
                return Response(result.data)
        return Response([])

    @link()
    def details(self, request, *args, **kwargs):
        point = self.get_object()
        shipping_point = helpers.get_shipping_point(
            point.site_id, point.position.x, point.position.y, point.type)
        if shipping_point:
            result = self.pudo_serializer_class(data=shipping_point)
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
    owner_field = ('patron', 'booking__owner')
    filter_fields = ('patron', )

    @user_required('patron')
    def delete(self, request, *args, **kwargs):
        super(PatronShippingPointViewSet, self).delete(*args, **kwargs)


class ProductShippingPointViewSet(viewsets.NonEditableModelViewSet):
    """
    API endpoint that allows product's shipping points to be viewed or edited.
    """
    serializer_class = serializers.ProductShippingPointSerializer
    queryset = models.ProductShippingPoint.objects.select_related('product')
    filter_backends = (filters.DjangoFilterBackend, )
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
