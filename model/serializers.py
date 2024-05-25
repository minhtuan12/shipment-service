from django.conf import settings
from rest_framework import serializers
from helpers import call_api, response_error
from model.models import Shipment
from rest_framework import status


class ShipmentSerializer(serializers.ModelSerializer):
    order = serializers.SerializerMethodField()

    class Meta:
        model = Shipment
        exclude = ['deleted']

    def __init__(self, *args, **kwargs):
        super(ShipmentSerializer, self).__init__(*args, **kwargs)
        if not self.context.get('include_order', False):
            self.fields.pop('order', None)
        else:
            self.fields.pop('order_id', None)

    def get_order(self, obj):
        request = self.context.get('request')
        result = call_api(
            request,
            settings.ORDER_SERVICE_API_URL + '/api/orders',
            'get',
            None,
            {
                'q': obj.order_id
            }
        )

        try:
            belong_order = result['data'][0] if len(result['data']) > 0 else None
            if not belong_order:
                return response_error('Bad Request', status.HTTP_400_BAD_REQUEST)

            return belong_order
        except:
            return response_error('Bad Request', status.HTTP_400_BAD_REQUEST)
