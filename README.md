# Python Logging Azure Workspace OMS Extension

## Configuration

The following environment variables are read to configure the extension and are required:

- `AZURE_LOG_CUSTOMER_ID`: Customer ID for the Azure Log Workspace
- `AZURE_LOG_SHARED_KEY`: Customer shared key for the Azure Log Workspace
- `AZURE_LOG_DEFAULT_NAME`: The default "log type" name to indicate where the logs are stored.
This will be suffixed with "_CL" within the Azure Log Workspace.

The following environment variables are read to tweak some parameters of the extension,
they all have default values and therefore are optional:

- `AZURE_LOG_MAX_CONCURRENT_REQUESTS`: *Default: 10* The maximum number of asyncronous requests to handle at once.
Used by `grequests`
- `AZURE_LOG_SEND_FREQUENCY`: *Default: 5* How many seconds the service thread should wait before sending pooled logs.
