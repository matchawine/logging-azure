import datetime
from logging import StreamHandler, LogRecord
from .service_provider import provide
from .log_service import AzureLogService


class AzureLogServiceHandler(StreamHandler):
    _RFC1123DATE = "%a, %d %b %Y %H:%M:%S GMT"

    def __init__(self):
        self._log_service: AzureLogService = provide(AzureLogService)
        super().__init__()

    def emit(self, record: LogRecord) -> None:
        message = self.format(record)
        rfc1123date = datetime.datetime.utcnow().strftime(self._RFC1123DATE)
        record_data = dict(
            level=record.levelname,
            message=message,
            time=rfc1123date,
            module=record.module,
            file_name=record.filename,
            line_number=record.lineno,
            thread_name=record.threadName,
            process_name=record.processName,
            process_pid=record.process,
            func_name=record.funcName,
        )
        self._log_service.add_record(record_data)
