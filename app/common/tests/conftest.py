import pytest
import requests


@pytest.fixture
def api_good_json(monkeypatch):
    def mock_get(*args, **kwargs):
        return {"status": 1,
                "data": [
                    {"id": "1",
                     "name": "first name",
                     "level": "1"},
                    {"id": "2",
                     "name": "second name",
                     "level": "2"},
                ]}
    monkeypatch.setattr(requests, "get", mock_get)

@pytest.fixture
def api_bad_json():
    return {"status": 0, "message": "Нет доступа к указанной таблице."}


# @pytest.fixture(autouse=True)
# def disable_network_calls(monkeypatch):
#     def stunted_get():
#         raise RuntimeError("Network access not allowed during testing!")
#     monkeypatch.setattr(requests, "get", lambda *args, **kwargs: stunted_get())
