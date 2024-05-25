import json

from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from rest_framework.decorators import api_view

from constants import PER_PAGE
from helpers import response_success, response_error
from model.models import Shipment, SHIPMENT_STATUS
from model.serializers import ShipmentSerializer
from shipment.decorators import verify_token, check_permission
from rest_framework import status as http_status


# Create your views here.
@verify_token
@api_view(['GET'])
def my_shipments(request):
    shipments = Shipment.objects.filter(deleted = 0, mobile = request.current_user['mobile']).order_by('-created_at')

    return response_success(
        'Success',
        ShipmentSerializer(
            shipments,
            many = True,
            context = {'request': request, 'include_order': True}
        ).data
    )


@verify_token
@api_view(['POST'])
def create_shipment(request):
    try:
        req = json.loads(request.body)
        current_user = request.current_user

        shipment = {
            'first_name': current_user['first_name'],
            'last_name': current_user['last_name'],
            'mobile': current_user['mobile'],
            'order_id': req['order_id'],
            'address': req['order_id'],
            'status': SHIPMENT_STATUS['PENDING']
        }
        Shipment.objects.create(**shipment)

        return response_success('Created Successfully', http_status.HTTP_201_CREATED)
    except:
        return response_error('Bad Request', http_status.HTTP_400_BAD_REQUEST)


@verify_token
@check_permission
@api_view(['GET'])
def get_all_shipments(request):
    q = request.GET.get('q')
    page_query = request.GET.get('page')
    sort_order = request.GET.get('sort_order')
    field = request.GET.get('field')
    status = request.GET.get('status')

    if sort_order and field:
        field = '-' + field if sort_order == 'desc' else field
    else:
        field = '-created_at'

    page = int(page_query) if page_query is not None else 1
    from_page = PER_PAGE * (page - 1)
    to_page = PER_PAGE

    shipments = Shipment.objects.filter(deleted = 0).order_by(field)

    if q is not None:
        search = q.strip()
        if q.isnumeric():
            shipments = shipments.filter(pk = search)
        else:
            shipments = shipments.filter(
                Q(first_name__icontains = search) |
                Q(last_name__icontains = search)
            )

    if status is not None:
        shipments = shipments.filter(status = status)

    shipments = shipments[from_page:to_page]

    response_data = {
        'page': page,
        'per_page': PER_PAGE,
        'total': len(shipments),
        'shipments': ShipmentSerializer(shipments, many = True).data
    }

    return response_success('Success', response_data)


@verify_token
@check_permission
@api_view(['PATCH'])
def update_status(request, id):
    try:
        new_status = json.loads(request.body)['status']
        if new_status not in SHIPMENT_STATUS.values():
            return response_error(f"Order status must be in {SHIPMENT_STATUS.values()}")

        shipment = Shipment.objects.get(pk = id, deleted = 0)
        shipment.status = new_status
        shipment.save()

        return response_success('Updated Successfully')
    except ObjectDoesNotExist:
        return response_error('Order does not exist', http_status.HTTP_404_NOT_FOUND)
    except:
        return response_error('Bad Request', http_status.HTTP_400_BAD_REQUEST)
