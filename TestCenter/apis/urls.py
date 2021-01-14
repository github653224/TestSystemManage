from django.urls import path
from .views import TestCaseAPI, TestCaseResultAPI, TestCaseResultLogApi, TestTaskApi,  \
    TestResultPicGenerate, TokenAPIView, get_folder, get_case_by_folder, SystemView, TestTaskDetail,get_QueryCase,uploadImage

urlpatterns = [
    path('testcase/', TestCaseAPI.as_view({'get': 'list', 'post': 'create', })),
    path('testcase/<int:pk>/', TestCaseAPI.as_view({'get': 'retrieve', 'put': 'update', "delete": 'destroy'})),
    path("caseresult/", TestCaseResultAPI.as_view({'get': 'list', 'post': 'create'})),
    path("caselog/<int:pk>/", TestCaseResultLogApi.as_view({'get': "retrieve"})),
    path("caselog/", TestCaseResultLogApi.as_view({'post': 'create'})),
    path("testtask/", TestTaskApi.as_view({'get': 'list', 'post': 'create'})),
    path("testtask/<int:pk>/", TestTaskApi.as_view({"get": 'retrieve', 'patch': 'update', 'delete': 'destroy'})),
    path('taskimgs/', TestResultPicGenerate.as_view()),
    path('token/', TokenAPIView.as_view()),
    path('getSystem/', SystemView.as_view({'get': 'list'})),
    path('getFolder/', get_folder),
    path('getCase/', get_case_by_folder),
    path('getTaskDetailCase/', TestTaskDetail.as_view()),
    path('querycase/', get_QueryCase),
    path('uploadFile/', uploadImage)
]
