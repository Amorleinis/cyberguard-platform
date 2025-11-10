from pydantic import BaseModel, Field, validator
from typing import Optional

class Host(BaseModel):
    id: str
    os: Optional[str]
    patch_level: Optional[str]

class Process(BaseModel):
    pid: int
    cmdline: str
    parent_pid: Optional[int] = None
    user: Optional[str]

class File(BaseModel):
    path: str
    sha256: str

class Endpoint(BaseModel):
    ip: str
    port: int

class Alert(BaseModel):
    id: str
    severity: str
    description: str

class ProcessStartEvent(BaseModel):
    event_type: str = Field("process_start", const=True)
    process: Process
    host: Host
    timestamp: str

class ProcessStopEvent(BaseModel):
    event_type: str = Field("process_stop", const=True)
    process: Process
    host: Host
    timestamp: str

class FileAccessEvent(BaseModel):
    event_type: str = Field("file_access", const=True)
    file: File
    process: Process
    host: Host
    timestamp: str

class NetworkConnectionEvent(BaseModel):
    event_type: str = Field("network_connection", const=True)
    process: Process
    host: Host
    endpoint: Endpoint
    timestamp: str

class AlertEvent(BaseModel):
    event_type: str = Field("alert", const=True)
    alert: Alert
    host: Host
    timestamp: str

# Map event_type -> model class for validation
EVENT_MODEL_MAP = {
    "process_start": ProcessStartEvent,
    "process_stop": ProcessStopEvent,
    "file_access": FileAccessEvent,
    "network_connection": NetworkConnectionEvent,
    "alert": AlertEvent,
}
