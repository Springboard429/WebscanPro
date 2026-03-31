from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Set, Dict

@dataclass
class InputField:
    name: str
    type: str
    value: str = ''
    required: bool = False

    def to_dict(self) -> dict:
        return {'name': self.name, 'type': self.type, 'value': self.value, 'required': self.required}

@dataclass
class FormInfo:
    action: str
    method: str
    inputs: List[InputField] = field(default_factory=list)
    name: str = ''

    def to_dict(self) -> dict:
        return {
            'action': self.action,
            'method': self.method,
            'inputs': [i.to_dict() for i in self.inputs],
            'name': self.name
        }


@dataclass
class DiscoveredURL:
    url: str
    status_code: int = 0
    title: str = ''
    depth: int = 0
    discovered_from: str = ''

    def to_dict(self) -> dict:
        return {
            'url': self.url,
            'status_code': self.status_code,
            'title': self.title,
            'depth': self.depth
        }

@dataclass
class ScanResult:
    target: str
    urls: List[DiscoveredURL] = field(default_factory=list)
    forms: List[FormInfo] = field(default_factory=list)
    parameters: Set[str] = field(default_factory=set)
    session: Dict[str, str] = field(default_factory=dict)
    scan_time: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict:
        return {
            'target': self.target,
            'scan_time': self.scan_time.isoformat(),
            'session': self.session,
            'urls': [u.to_dict() for u in self.urls],
            'forms': [f.to_dict() for f in self.forms],
            'parameters': list(self.parameters)
        }
