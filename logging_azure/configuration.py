import os
from dataclasses import dataclass


@dataclass(frozen=True)
class AzureLogServiceConfiguration:
    customer_id: str
    shared_key: str
    default_log_type: str
    max_concurrent_requests: int
    send_frequency: int

    @staticmethod
    def build() -> "AzureLogServiceConfiguration":
        customer_id: str = os.getenv("AZURE_LOG_CUSTOMER_ID", "")
        shared_key: str = os.getenv("AZURE_LOG_SHARED_KEY", "")
        default_log_type: str = os.getenv("AZURE_LOG_DEFAULT_NAME", "")
        max_concurrent_requests: int = int(os.getenv("AZURE_LOG_MAX_CONCURRENT_REQUESTS", 10))
        send_frequency: int = int(os.getenv("AZURE_LOG_SEND_FREQUENCY", 5))

        return AzureLogServiceConfiguration(
            customer_id=customer_id,
            shared_key=shared_key,
            default_log_type=default_log_type,
            max_concurrent_requests=max_concurrent_requests,
            send_frequency=send_frequency,
        )
