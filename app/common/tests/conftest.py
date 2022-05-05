import pytest
import requests


@pytest.fixture
def api_response_json():
    return {"status": 1,
            "data": [
                {"id": "1",
                 "name": "first name",
                 "level": "1"},
                {"id": "2",
                 "name": "second name",
                 "level": "2"},
            ]}


# @pytest.fixture
# def api_error_response_json():
#     return {"status": 0, "message": "Нет доступа к указанной таблице."}


# @pytest.fixture(autouse=True)
# def disable_network_calls(monkeypatch):
#     def stunted_get():
#         raise RuntimeError("Network access not allowed during testing!")
#     monkeypatch.setattr(requests, "get", lambda *args, **kwargs: stunted_get())
