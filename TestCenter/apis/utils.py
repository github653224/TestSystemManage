from django.contrib.auth.models import User
from django.core.cache import cache
from django.http import HttpResponse
import datetime


def login_required(func):
    def wrapper(request, *args, **kwargs):
        username = request.COOKIES.get('username', None)
        token = request.COOKIES.get("token", None)
        if token and username:
            cache_token = cache.get(username)
            if not cache_token:
                return HttpResponse(status=401, content='未登录')
            else:
                if cache_token != token:
                    return HttpResponse(status=401, content="未登录")
                else:
                    return func(request, *args, **kwargs)
        else:
            return HttpResponse(status=401, content='未登录')

    return wrapper


def datetime_strftime(fmt="%Y-%m-%d %H:%M:%S"):
    """datetime格式化时间"""
    return datetime.datetime.now().strftime(fmt)