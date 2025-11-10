import time
from schemas import EVENT_MODEL_MAP
from typing import Dict, Any

def get_event_template(event_type: str) -> Dict[str, Any]:
    now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    templates = {
        "process_start": {
            "event_type": "process_start",
            "process": {
                "pid": 1234,
                "cmdline": "/usr/bin/python app.py",
                "parent_pid": None,
                "user": "root"
            },
            "host": {
                "id": "host-1",
                "os": "Linux",
                "patch_level": "2025.08.01"
            },
            "timestamp": now
        },
        "process_stop": {
            "event_type": "process_stop",
            "process": {
                "pid": 1234,
                "cmdline": "/usr/bin/python app.py",
                "parent_pid": None,
                "user": "root"
            },
            "host": {
                "id": "host-1",
                "os": "Linux",
                "patch_level": "2025.08.01"
            },
            "timestamp": now
        },
        "file_access": {
            "event_type": "file_access",
            "file": {
                "path": "/var/log/app.log",
                "sha256": "dummyhash123"
            },
            "process": {
                "pid": 1234,
                "cmdline": "/usr/bin/grep error /var/log/app.log"
            },
            "host": {
                "id": "host-1",
                "os": "Linux",
                "patch_level": "2025.08.01"
            },
            "timestamp": now
        },
        "network_connection": {
            "event_type": "network_connection",
            "process": {
                "pid": 1234,
                "cmdline": "/usr/bin/curl http://example.com"
            },
            "host": {
                "id": "host-1",
                "os": "Linux",
                "patch_level": "2025.08.01"
            },
            "endpoint": {
                "ip": "192.168.1.10",
                "port": 80
            },
            "timestamp": now
        },
        "alert": {
            "event_type": "alert",
            "alert": {
                "id": "alert-123",
                "severity": "high",
                "description": "Suspicious activity detected"
            },
            "host": {
                "id": "host-1",
                "os": "Linux",
                "patch_level": "2025.08.01"
            },
            "timestamp": now
        }
    }
    return templates.get(event_type, {})

def prompt_edit(field_name: str, current_value: Any):
    val = input(f"{field_name} [{current_value}]: ")
    if val.strip() == "":
        return current_value
    # Try to cast int
    if isinstance(current_value, int):
        try:
            return int(val)
        except ValueError:
            print("Invalid int input, keeping original.")
            return current_value
    if current_value is None and val.lower() in ("none", "null", ""):
        return None
    return val

def recursive_edit(data: Any, path=""):
    if isinstance(data, dict):
        for k in data:
            full_path = f"{path}.{k}" if path else k
            data[k] = recursive_edit(data[k], full_path)
        return data
    elif isinstance(data, list):
        print(f"List editing not supported yet at {path}")
        return data
    else:
        return prompt_edit(path, data)

def interactive_edit(event: Dict[str, Any]) -> Dict[str, Any]:
    print("Edit event fields (press Enter to keep current values):")
    return recursive_edit(event)
