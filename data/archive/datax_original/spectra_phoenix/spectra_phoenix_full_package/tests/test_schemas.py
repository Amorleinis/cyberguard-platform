from spectra_phoenix_producer.schemas import EVENT_MODEL_MAP
from spectra_phoenix_producer.events import get_event_template
import pytest

@pytest.mark.parametrize("event_type", list(EVENT_MODEL_MAP.keys()))
def test_event_templates(event_type):
    event = get_event_template(event_type)
    model_cls = EVENT_MODEL_MAP[event_type]
    validated = model_cls.parse_obj(event)
    assert validated.event_type == event_type
