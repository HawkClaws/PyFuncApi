## このWebApiに関して
AWSLambdaのようなFaaS「PyFuncApi」を作った話  
https://qiita.com/HawkClaws/items/14032426758cd04f739d

## 定必須項目

mysite/settings.py

コード格納用のRealtimeDatabaseのURL(設定必須：URLのみ「.json」は除く)  
CODE_DATA_REPOSITORY_URL

非同期実行時の結果保存用のRealtimeDatabaseのURL(設定必須：URLのみ「.json」は除く)  
ASYNC_DATA_REPOSITORY_URL

##### 参考記事
REST APIで使用するFirebase Realtime Database  
https://qiita.com/HawkClaws/items/0273d328f171717d2a44

##### Example POST Code
```
from django.http import HttpResponse
text = request.GET.get('text')
response = HttpResponse(text)
```
