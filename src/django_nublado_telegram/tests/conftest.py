import pytest
from types import SimpleNamespace


@pytest.fixture
def context():
    return SimpleNamespace(
        chat_data={}, bot_data={}, application=SimpleNamespace(bot_data={}), args=[]
    )


@pytest.fixture
def update():
    return SimpleNamespace(
        effective_chat=SimpleNamespace(
            id=123, title="Test Chat", type="group", username="test group"
        ),
        effective_message=SimpleNamespace(message_id=1),
    )
