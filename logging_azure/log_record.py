from typing import Dict, Any, Callable, Optional
from requests import Response
from grequests import AsyncRequest
from dataclasses import dataclass, field
from dataclasses_json import DataClassJsonMixin


@dataclass
class AzureLogRecord(DataClassJsonMixin):
    id: str
    level: str
    time: str
    message: str
    module: str
    file_name: str
    line_number: int
    thread_name: str
    process_name: str
    process_pid: int
    func_name: str

    log_request: Optional[AsyncRequest] = None
    log_response: Optional[Response] = None

    def __hash__(self):
        return hash(self.id)
