import bcrypt
import requests
from django.http import HttpResponse
import json
import re
import jwt
import datetime
from django.conf import settings
from requests import HTTPError, Timeout


def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())


def compare_password(password, hashed_password):
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password[2:len(hashed_password) - 1].encode('utf-8'))


EMAIL_REGEX = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
PHONE_REGEX = r'^(\+?84|0)([3|5|7|8|9])+([0-9]{8})$'


def response_success(message = '', data = None, status_code = 200):
    if data is None:
        data = {}

    return HttpResponse(json.dumps({
        'status': 'Success',
        'status_code': status_code,
        'message': message,
        'data': data
    }), content_type = 'application/json', status = status_code)


def response_error(message = '', status_code = 400, error = None):
    if error is None:
        error = {}

    return HttpResponse(json.dumps({
        'status': 'Failed',
        'status_code': status_code,
        'message': message,
        'error': error
    }), content_type = 'application/json', status = status_code)


def is_valid_phone(number):
    return re.match(PHONE_REGEX, number) is not None


def is_valid_email(email):
    return re.fullmatch(EMAIL_REGEX, email) is not None


def generate_token(username):
    payload = {
        'username': username,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days = 7)
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm = 'HS256')

    return token


def serialize_model_instance(instance, exclude):
    data = {}
    for field in instance._meta.fields:
        field_name = field.name
        if field_name in exclude:
            continue
        field_value = getattr(instance, field_name)
        data[field_name] = field_value
    return data


def call_api(request, url, method = 'get', data = None, params = None):
    if params is None:
        params = {}
    try:
        url = url
        header = {
            "Content-Type": "application/json",
            "Authorization": request.META.get('HTTP_AUTHORIZATION', '')
        }

        result = None
        if method == 'get':
            result = requests.get(url, headers = header, params = params)
        elif method == 'patch':
            result = requests.patch(url, json = data, headers = header, params = params)
        result.raise_for_status()

        if result.json()['status'] == 'Success':
            return result.json()
        return response_error(result.json()['message'], result.json()['status_code'])

    except HTTPError as http_err:
        response_error(f"HTTP error occurred: {http_err}")
    except Timeout:
        response_error("The request timed out")
    except ConnectionError:
        response_error("Network connection error")
    except Exception as err:
        response_error(f"An error occurred: {err}")
