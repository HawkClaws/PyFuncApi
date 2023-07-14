from django.urls import path, re_path

from . import views

app_name = 'PyFuncApi'
urlpatterns = [
    # API
    path('wakeup/', views.wakeup, name='wakeup'),
    # POSTされたPythonのコードを同期実行
    path('api/exec/', views.api_exec_single, name='api_exec_single'),

    # 【廃止予定/互換性問題のため残す】POSTされたPythonのコードを同期実行(inputあり/inputはAPIコード内で処理取得)
    path('api/exec-input/', views.api_exec_single_with_input, name='api-api_exec_single_with_input-single'),
    # POSTされたPythonのコードを同期実行(inputあり/inputはAPIコード内で処理取得)
    path('api/exec_input/', views.api_exec_single_with_input, name='api-api_exec_single_with_input-single'),

    # POSTされたPythonのコードを非同期実行
    path('api/exec_async/', views.api_exec_async_single, name='api_exec_async_single'),
    
    # 非同期実行の実行結果を取得
    path('api/exec_async_result/<str:result_id>', views.api_exec_async_result,
         name='api_exec_async_result'),

    # APIソースコードのキャッシュをリフレッシュする
    path('refresh_cache/', views.refresh_cache, name='refresh_cache'),
    
    # 登録済みのAPIを同期実行します
    re_path(r'api/exec/(.*)', views.api_exec, name='api_exec'),


    #【廃止予定/互換性問題のため残す】登録済みのAPIを非同期実行します
    re_path(r'api/exec-async/(.*)', views.api_exec_async, name='api_exec_async'),
    # 登録済みのAPIを非同期実行します
    re_path(r'api/exec_async/(.*)', views.api_exec_async, name='api_exec_async'),

    # 登録済みのAPIを非同期実行し、結果を保存します
    re_path(r'api/exec_async_save/(.*)', views.api_exec_async_save, name='exec_async_save'),

    # APIの情報を登録・取得します
    re_path(r'admin/api/(.*)', views.api_operation, name='api'),
    # APIの情報を登録・取得します（コード実行チェックはしない）
    re_path(r'admin/api_nocheck/(.*)', views.api_operation_nocheck, name='api_nocheck'),

    # 登録済みのAPIをバッチ処理します(MQ受付し、任意の同時起動数で直列実行する task.pyを参照)
    re_path(r'api/exec_batch/(.*)', views.exec_batch, name='exec_batch'),
    # 登録済みのAPIをバッチ処理します(MQ受付し、任意の同時起動数で直列実行する task.pyを参照)
    re_path(r'api/exec_batch_save/(.*)', views.exec_batch_save, name='exec_batch_save'),
    #APIインポート
    #path('import_modules/', views.import_modules, name='import_modules'),
]
