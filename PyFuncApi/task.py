import traceback
import uuid
from apscheduler.schedulers.background import BackgroundScheduler
from pymongo import ASCENDING
from .repository.instance_mongo_repository import get_batch_task_repository

from .service.api_crud_service import get_code_data
from .service.http_request_serializer import unpickle_http_request
from .service.logging import logging, EXEC_TYPE, TRACE_ID
from .service.exec_service import async_method, HTTP_RESPONSE

# バッチ処理


def job_function():

    input_data = {}
    try:
        input_data = get_batch_task_repository().select_and_delete(
            {}, [("created_at", ASCENDING)])
        if input_data == None:
            return
    except Exception as e:
        logging({"exception": traceback.format_exc()},
                {EXEC_TYPE: "exec_batch"}, "error")
        return

    url = ""
    trace_id = ""
    try:
        url = input_data["url"]
        result_id = input_data["result_id"]
        trace_id = input_data["trace_id"]
        request = unpickle_http_request(input_data["http_request_data"])

        code_info = get_code_data(url)
        res = async_method(code_info["code"], request,
                           url, result_id, "exec_batch", trace_id)

    except Exception as e:
        logging({"exception": traceback.format_exc(), "url": url, "trace_id": trace_id},
                {EXEC_TYPE: "exec_batch"}, "error")


def start_batch_process():
    scheduler = BackgroundScheduler()
    scheduler.add_job(job_function, 'interval', minutes=1, max_instances=1)
    scheduler.start()


# 毎日23時59分に実行
# scheduler.add_job(periodic_execution, 'cron', hour=8, minute=30)

# 5分おきに実行
# scheduler.add_job(periodic_execution, 'interval', minutes=5)

# 1時間5秒おきに実行
# scheduler.add_job(periodic_execution, 'interval', hours=1, seconds=5)

# 1日おきに実行
# scheduler.add_job(periodic_execution, 'interval', days=1)

# 1週間おきに実行
# scheduler.add_job(periodic_execution, 'interval', weeks=1)

# 2022年4月1日19時〜20時の間、1分おきに実行
# scheduler.add_job(periodic_execution, 'interval', minutes=1,
# start_date="2022-04-01 19:00:00",
# end_date="2022-04-01 20:00:00")

# 毎時20分に実行
# scheduler.add_job(periodic_execution, 'cron', minute=20)

# 月曜から金曜の間、8時に実行
# scheduler.add_job(periodic_execution, 'cron', hour=8, day_of_week='mon-fri')
