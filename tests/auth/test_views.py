import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_login_view(async_client: AsyncClient):
    response = await async_client.get("/login")
    assert (
        response.status_code == 200
    ), "Check that login page '/' is available and returns 200 code"


@pytest.mark.asyncio
async def test_users_view(async_client: AsyncClient):
    response = await async_client.get("/users")
    assert (
        response.status_code == 200
    ), "Check that users page '/' is available and returns 200 code"
