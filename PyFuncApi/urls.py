from django.urls import path, re_path

from . import views

app_name = 'PyFuncApi'
urlpatterns = [
    # API
    path('wakeup/', views.wakeup, name='wakeup'),
    path('api-exec/', views.api_exec_single, name='api-exec-single'),
    path('api-exec-async/', views.api_exec_async_single, name='api-exec-async-single'),
    path('api-exec-async-result/<str:result_id>', views.api_exec_async_result,
         name='api-exec-async-result'),
    re_path(r'admin/api/(.*)', views.api_operation, name='api-operation'),
    re_path(r'api/exec/(.*)', views.api_exec, name='api-exec'),
    re_path(r'api/exec-async/(.*)', views.api_exec_async, name='api-exec-async'),
]
