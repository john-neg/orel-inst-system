import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_root(async_client: AsyncClient):
    response = await async_client.get("/")
    assert (
        response.status_code == 200
    ), "Check that root page '/' is available and returns 200 code"
