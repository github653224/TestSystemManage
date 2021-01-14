import json
import time
import os

import jwt
from django.core.cache import cache
from django.db.models import Q
from django.http import JsonResponse, HttpResponse
from io import BytesIO
import xlsxwriter
from rest_framework import status
from rest_framework.response import Response
# Create your views here.
from django.views import View
from rest_framework.mixins import CreateModelMixin
from rest_framework.pagination import PageNumberPagination
from rest_framework_jwt.settings import api_settings
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet, GenericViewSet

from .models import TestCase, TestCaseResult, TestTask, CateFolder, ParentCateName, User, TeskDetail
from .serializer import TestCaseSerializer, TestCaseResultLogSerializer, TestCaseResultSerializer, TestTaskSerializer, \
    FirstLevelTreeSerializer, FolderSerializer, UserSerializer, ParentNameSerializer
from django.utils.decorators import method_decorator
from .utils import login_required, datetime_strftime
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.views.decorators.csrf import csrf_exempt


class TestCasePaginator(PageNumberPagination):
    page_size = 8
    page_size_query_param = "page_size"
    page_query_param = "page"


@method_decorator(login_required, name='list')
@method_decorator(login_required, name='retrieve')
@method_decorator(login_required, name='destroy')
@method_decorator(login_required, name='update')
class TestCaseAPI(ModelViewSet):
    """
    list: 返回所有测试用例详情

    retrieve: 返回当前ID测试用例的详情

    update: 更改当前用例

    destroy: 删除当前用例
    """
    queryset = TestCase.objects.all().order_by("id")
    pagination_class = TestCasePaginator
    serializer_class = TestCaseSerializer


class TestCaseResultPaginator(PageNumberPagination):
    page_size = 8
    page_size_query_param = "page_size"
    page_query_param = "page"


class TestCaseResultAPI(ModelViewSet):
    """
    list: 返回所有测试用例自动化执行结果
    update: 更改当前用例执行结果

    """
    queryset = TestCaseResult.objects.all().order_by('-create_time')
    pagination_class = TestCaseResultPaginator
    serializer_class = TestCaseResultSerializer


class TestCaseResultLogApi(ModelViewSet):
    """
    create: 创建完整执行结果
    retrieve: 返回当前ID测试用例自动化执行的详情(包含执行日志)
    """
    queryset = TestCaseResult.objects.all().order_by('-create_time')
    pagination_class = TestCaseResultPaginator
    serializer_class = TestCaseResultLogSerializer


class TestTaskPaginator(PageNumberPagination):
    page_size = 8
    page_size_query_param = "page_size"
    page_query_param = "page"


@method_decorator(login_required, name='list')
@method_decorator(login_required, name='retrieve')
@method_decorator(login_required, name='destroy')
@method_decorator(login_required, name='update')
class TestTaskApi(ModelViewSet):
    """
    list: 返回所有测试任务详情

    retrieve: 返回当前ID测试任务的详情

    update: 更改当前任务

    destroy: 删除当前任务
    """
    queryset = TestTask.objects.all().order_by('-create_time')
    pagination_class = TestTaskPaginator
    serializer_class = TestTaskSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        contain_case = request.data.get('contain_cases')
        task_name = request.data.get('taskname')
        run_time = request.data.get('run_time')
        task = TestTask.objects.get(Q(taskname__exact=task_name) & Q(run_time__exact=run_time))
        for i in contain_case:
            taskd = TeskDetail(caseid=i, taskid=task.id)
            taskd.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class TestResultPicGenerate(View):
    """
    get: 获取当前任务的执行结果EXCEL 需要提供query_param 为 taskname
    """

    @login_required
    def get(self, request):
        task_name = request.GET.get("taskname")
        all_list = list()
        if task_name:
            query_set = TestCaseResult.objects.filter(taskname=task_name)
            if query_set:
                detail_li = list()
                for i in query_set:
                    marker = eval(i.marker)
                    marker.pop("TestCase")
                    marker.pop("TEST_AUTOMATION")
                    marker.pop('pytestmark')
                    key_words_li = list()
                    for xx in marker:
                        key_words_li.append(xx)
                    belongs = ''
                    api_name = '',
                    case_name = i.case_name
                    methods = '',
                    seconds = i.request_time
                    for j in key_words_li:
                        if 'post' in j.lower() or 'get' in j.lower():
                            kes = j.split("_")
                            methods = kes[-1]
                            kes.pop(-1)
                            kes.pop(0)
                            api_name = '/'.join(z for z in kes)
                            api_name = '/' + api_name
                        if '/' in j:
                            belongs = j.split('/')[2]

                    detail_li.append((belongs, api_name, case_name, methods, task_name, seconds))
                x_io = BytesIO()
                work_book = xlsxwriter.Workbook(x_io)
                work_sheet = work_book.add_worksheet('details')
                row = 0
                col = 0
                header = ['模块', '接口', '用例名称', '请求方式', '任务名', '请求响应时间']
                for i in header:
                    work_sheet.write(row, col, i)
                    col += 1
                row = 1
                for i in detail_li:
                    for j in range(6):
                        work_sheet.write(row, j, i[j])
                    row += 1
                work_book.close()
                res = HttpResponse()
                res["Content-Type"] = "application/octet-stream"
                res["Content-Disposition"] = 'filename="test_results.xlsx"'
                res.write(x_io.getvalue())
                return res


@method_decorator(login_required, name='list')
@method_decorator(login_required, name='retrieve')
@method_decorator(login_required, name='destroy')
@method_decorator(login_required, name='update')
class SystemView(ModelViewSet):
    """
    list: 返回所有用例所属系统

    retrieve: 返回当前ID用例所属系统的详情

    update: 更改当前所属系统

    destroy: 删除当前所属系统
    """
    queryset = ParentCateName.objects.all()
    serializer_class = ParentNameSerializer


@login_required
def get_folder(request):
    """
    根据系统获取当前系统下的文件夹 query_param为 system> 所属系统id
    :param request:
    :return:
    """
    system = request.GET.get('system')
    if not system:
        return HttpResponse(status=403, content="Bad Request")
    obj = CateFolder.objects.filter(parent__exact=int(system))
    if not obj:
        return HttpResponse(status=403, content="Bad Request")
    serializer = FolderSerializer(obj, many=True)
    return JsonResponse(serializer.data, safe=False)


@login_required
def get_case_by_folder(request):
    """
    获取文件夹下所有用例
    """
    folder = request.GET.get("folder")
    if not folder:
        return HttpResponse(status=403, content="Bad Request")
    obj = TestCase.objects.filter(case_belongs__exact=int(folder))
    if not obj:
        return HttpResponse(status=403, content="Bad Request")
    serializer = TestCaseSerializer(obj, many=True)
    return JsonResponse(serializer.data, safe=False)


class CaseSearch(APIView):
    """
    post: 根据post中JSON查询用例
    """

    @login_required
    def post(self, request):
        try:
            req_body = json.loads(request.body)
        except Exception as e:
            return
        cases = req_body.get("cases")
        if isinstance(cases, str):
            cases = eval(cases)
        if isinstance(cases, list):
            query_set = TestCase.objects.filter(case_name__in=cases)
            if query_set:
                serializer = TestCaseSerializer(query_set, many=True)
                return JsonResponse(serializer.data, safe=False)


@method_decorator(login_required, name='delete')
class TokenAPIView(APIView):
    """
    post: 根据用户名及密码获取jwt_token
    put: 创建用户并返回jwt_token
    delete: 注销
    均需要前端设置返回值至cookie
    """
    def post(self, request, ):
        username = request.data.get("username")
        password = request.data.get("password")
        if username and password:
            user = User.objects.get(username=username)
            if not user:
                return HttpResponse(status=401, content='不存在的User')
            if not user.check_password(password):
                return HttpResponse(status=401, content='密码错误')
            jwt_token = self.__token__(user)
            return JsonResponse({'username': user.username, 'token': jwt_token}, safe=False)
        else:
            return HttpResponse(status=403, content="Not Found")

    @staticmethod
    def __token__(user):
        token_dict = {
            'iat': time.time(),
            'name': user.username
        }
        headers = {
            'alg': 'HS256'
        }
        jwt_token = jwt.encode(token_dict, user.password, algorithm='HS256',
                               headers=headers).decode('ascii')
        cache.set(user.username, jwt_token)
        return jwt_token

    def put(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            username = request.data.get("username")
            user = User.objects.get(username=username)
            jwt_token = self.__token__(user)
            return JsonResponse({'username': user.username, 'token': jwt_token}, safe=False)
        else:
            return HttpResponse(status=403, content='Bad Param')

    def delete(self, request):
        username = request.COOKIES.get('username', None)
        if username:
            cache.delete(username)
            return HttpResponse(status=204, content='ok')


@method_decorator(login_required, name='get')
class TestTaskDetail(APIView):
    """
    post: 根据任务ID 获取任务详情，返回当前任务包含的所有用例
    """
    def get(self, request):
        testTask = request.GET.get('taskid')
        if not testTask:
            return HttpResponse(status=404, content="Not Found")
        query_set = TeskDetail.objects.filter(taskid__exact=int(testTask))
        if not query_set:
            return HttpResponse(status=404, content="Not Found")
        case_id_list = [i.id for i in query_set]
        cases = TestCase.objects.filter(id__in=case_id_list)
        serializer = TestCaseSerializer(cases, many=True)
        return JsonResponse(serializer.data, safe=False)


@login_required
def get_QueryCase(request):
    """查询用例"""
    system = request.GET.get('system')
    folder = request.GET.get("folder")
    case_name = request.GET.get('case_name')
    query_condition = {'system': Q(case_belongs__in=CateFolder.objects.filter(parent=system)),
                       'folder': Q(case_belongs__exact=folder),
                       'case_name': Q(case_name__contains=case_name)}
    query_param = []
    if system:
        query_param.append(query_condition.get('system'))
    if folder:
        query_param.append(query_condition.get('folder'))
    if case_name:
        query_param.append(query_condition.get('case_name'))
    query_param = tuple(query_param)
    queryset = TestCase.objects.filter(*query_param)
    if queryset:
        serializer = TestCaseSerializer(queryset, many=True)
        return JsonResponse(serializer.data, safe=False)
    else:
        return HttpResponse(status=404, content=FileNotFoundError)


@csrf_exempt
def uploadImage(request):
    """上传文件，保存在本地，可以自行修改为base64存数据库"""
    if request.method.upper() == 'POST':
        image = request.FILES.get('image')
        png_path = os.path.join(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'images'),
                                '%s.png' % datetime_strftime('%Y-%m-%d_%H%M%S'))
        path = default_storage.save(png_path, ContentFile(image.read()))
        return JsonResponse({'url': 'http://ip:port/images/%s' % path.split("/")[-1]}, safe=False)


