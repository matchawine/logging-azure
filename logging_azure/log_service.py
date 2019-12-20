import grequests
import datetime
import hashlib
import hmac
import base64
import json
from time import sleep
from injector import singleton, inject
from typing import Optional, List, Callable, Iterable, Dict, Any, Union
from threading import Thread
from uuid import uuid4
from .log_record import AzureLogRecord
from .configuration import AzureLogServiceConfiguration


@singleton
class AzureLogService:
    _X_HEADER = "x-ms-date:{date}"
    _RFC1123DATE = "%a, %d %b %Y %H:%M:%S GMT"
    _ENDPOINT_URI = "https://{customer_id}.ods.opinsights.azure.com{resource}?api-version=2016-04-01"
    _AUTHORIZATION_HEADER = "SharedKey {customer_id}:{encoded_hash}"
    _HASH_STRING = "{method}\n{content_length}\n{content_type}\n{x_headers}\n{resource}"
    _RESOURCE = "/api/logs"
    _MESSAGE = "{state} with response code: {status_code}"

    @inject
    def __init__(self, configuration: AzureLogServiceConfiguration):
        self._configuration: AzureLogServiceConfiguration = configuration
        self._jobs: List[AzureLogRecord] = list()
        self._worker: Thread = Thread(target=self._run_worker, daemon=True)
        self._worker.start()

    def add_record(self, record_data: Dict[str, Any]) -> None:
        new_record = AzureLogRecord(id=str(uuid4()), **record_data)
        self._jobs.append(new_record)

    def _clean_queue(self, worker_list: List[AzureLogRecord]) -> None:
        for record in worker_list:
            if record.log_response and record.log_response.status_code in range(200, 300):
                self._jobs.remove(record)

    def _run_worker(self) -> None:
        while True:
            worker_list = self._jobs.copy()
            requests = (self._build_request(record) for record in worker_list)
            self._handle_requests(tasks=requests)
            self._clean_queue(worker_list)
            sleep(self._configuration.send_frequency)

    def _handle_requests(
        self,
        tasks: Iterable[AzureLogRecord],
        stream: bool = False,
        exception_handler: Callable = None,
        gtimeout: Optional[int] = None,
    ) -> None:
        """Concurrently handles a collection of AzureLogRecords to convert the requests to responses.

        :param tasks: a collection of AzureLogRecord objects.
        :param stream: If True, the content will not be downloaded immediately.
        :param exception_handler: Callback function, called when exception occured. Params: Request, Exception
        :param gtimeout: Gevent joinall timeout in seconds. (Note: unrelated to requests timeout)
        """

        tasks = list(tasks)

        pool = grequests.Pool(self._configuration.max_concurrent_requests)
        jobs = [grequests.send(rec.log_request, pool, stream=stream) for rec in tasks]
        grequests.gevent.joinall(jobs, timeout=gtimeout)

        for record in tasks:
            if record.log_request.response is not None:
                record.log_response = record.log_request.response
            elif exception_handler and hasattr(record.log_request, "exception"):
                record.log_response = exception_handler(record.log_request, record.log_request.exception)
            else:
                record.log_response = None

    def _build_uri(self) -> str:
        resource = self._RESOURCE
        uri = self._ENDPOINT_URI.format(customer_id=self._configuration.customer_id, resource=resource)
        return uri

    def _build_signature(self, date: str, content_length: int, method: str, content_type: str, resource: str) -> str:
        """ Builds the API signature

        :param date: str: Current datetime in UTC
        :param content_length: int: Length of request body
        :param method: str: HTTP request method
        :param content_type: str: HTTP request content_type
        :param resource: str: API resource endpoint
        :return: str: Authorization header for the HTTP request
        """
        x_headers = self._X_HEADER.format(date=date)
        string_to_hash = self._HASH_STRING.format(
            method=method,
            content_length=content_length,
            content_type=content_type,
            x_headers=x_headers,
            resource=resource,
        )
        bytes_to_hash = string_to_hash.encode("utf-8")
        decoded_key = base64.b64decode(self._configuration.shared_key)
        encoded_hash = base64.b64encode(
            hmac.new(decoded_key, bytes_to_hash, digestmod=hashlib.sha256).digest()
        ).decode("utf-8")
        authorization = self._AUTHORIZATION_HEADER.format(
            customer_id=self._configuration.customer_id, encoded_hash=encoded_hash
        )
        return authorization

    def _build_headers(self, body: str, log_type: str) -> Dict[str, str]:
        """Build and send a request to the POST API
        :param body: str: JSON web monitor object
        :param log_type: str: Name of the Event/CustomLogs that is being submitted
        :return: int: 0 on success, 1 on error
        """

        rfc1123date = datetime.datetime.utcnow().strftime(self._RFC1123DATE)
        content_length = len(body)
        method = "POST"
        content_type = "application/json"
        resource = self._RESOURCE
        signature = self._build_signature(rfc1123date, content_length, method, content_type, resource)
        headers = {
            "content-type": content_type,
            "Authorization": signature,
            "Log-Type": log_type,
            "x-ms-date": rfc1123date,
        }
        return headers

    def _build_body(self, record: AzureLogRecord) -> Dict[str, Union[str, int]]:
        body = dict(
            level=record.level,
            time=record.time,
            message=record.message,
            module=record.module,
            file_name=record.file_name,
            line_number=record.line_number,
            thread_name=record.thread_name,
            process_name=record.process_name,
            process_pid=record.process_pid,
            func_name=record.func_name,
        )
        return body

    def _build_request(self, record: AzureLogRecord, log_type: Optional[str] = None) -> AzureLogRecord:
        log_type = log_type or self._configuration.default_log_type
        uri = self._build_uri()
        body = self._build_body(record)
        body_payload = json.dumps(body)
        headers = self._build_headers(body_payload, log_type)

        record.log_request = grequests.post(uri, data=body_payload, headers=headers)
        return record
