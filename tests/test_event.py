import typing as ty
from baozi import FrozenStruct, field
from datetime import datetime



class Event(FrozenStruct):
    version: ty.ClassVar[str] = "1.0.0"

    event_id: str
    entity_id: str
    timestamp: datetime = field(default_factory=datetime.now) 

    
def test_build_event():
    event = Event(event_id="1", entity_id="2")
    assert event.event_id == "1"
    assert event.entity_id == "2"
    assert isinstance(event.timestamp, datetime)
    assert isinstance(event.version, str)