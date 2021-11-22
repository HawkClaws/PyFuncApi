from django.urls import path, re_path

from . import views

app_name = 'PyFuncApi'
urlpatterns = [
    # API
    path('wakeup/', views.wakeup, name='wakeup'),
    # POSTされたPythonのコードを同期実行
    path('api/exec/', views.api_exec_single, name='api-exec-single'),
    # POSTされたPythonのコードを非同期実行
    path('api/exec-async/', views.api_exec_async_single, name='api-exec-async-single'),
    # 非同期実行の実行結果を取得
    path('api/exec-async-result/<str:result_id>', views.api_exec_async_result,
         name='api-exec-async-result'),
        
    # APIの情報を登録・取得します
    re_path(r'admin/api/(.*)', views.api_operation, name='api-operation'),
    # APIの情報を登録・取得します（コード実行チェックはしない）
    re_path(r'admin/api-nocheck/(.*)', views.api_operation_nocheck, name='api-operation'),
    # 登録済みのAPIを同期実行します
    re_path(r'api/exec/(.*)', views.api_exec, name='api-exec'),
    # 登録済みのAPIを非同期実行します
    re_path(r'api/exec-async/(.*)', views.api_exec_async, name='api-exec-async'),
]
