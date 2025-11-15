import json
import random
import sys
import traceback
from datetime import datetime
from typing import Any, AsyncIterable, Dict, Literal, Optional
from uuid import UUID as REAL_UUID

import factory.random
import pytest
from aiohttp.pytest_plugin import AiohttpClient
from freezegun import freeze_time

import prozorro_cdb.api.database.store as database_store

from .constants import API_HOST, MOCK_DATETIME, MOCK_SEED, PUBLIC_API_HOST


@pytest.fixture(scope="function")
def deterministic_environment(monkeypatch):
    # freeze time
    freezer = freeze_time(MOCK_DATETIME)
    freezer.start()

    #  seed randomness
    random.seed(MOCK_SEED)
    factory.random.reseed_random(MOCK_SEED)

    # mock uuid4
    # works only with `import uuid` not `from uuid import uuid4`
    real_uuid_module = sys.modules["uuid"]
    original_uuid4 = real_uuid_module.uuid4
    counter = 0

    def fake_uuid4():
        nonlocal counter
        # Pymongo uses uuid to generate session ids that should not be mocked
        for frame in traceback.extract_stack():
            if "pymongo" in frame.filename:
                return original_uuid4()

        counter += 1
        return REAL_UUID(f"88888888-4444-5555-6666-{counter:012x}")

    monkeypatch.setattr(real_uuid_module, "uuid4", fake_uuid4)
    monkeypatch.setattr(
        database_store,
        "get_public_modified",
        lambda: datetime.now().timestamp(),
    )

    yield

    # cleanup
    freezer.stop()


@pytest.fixture(scope="function")
def forwarded_client(aiohttp_client):
    async def factory(app):
        client = await aiohttp_client(app)

        orig_request = client._request

        async def _request(method, url, **kwargs):
            kwargs["headers"] = kwargs.get("headers") or {}
            kwargs["headers"].setdefault("X-Forwarded-Host", PUBLIC_API_HOST if method == "GET" else API_HOST)
            return await orig_request(method, url, **kwargs)

        client._request = _request
        return client

    return factory


@pytest.fixture(scope="function")
async def api(event_loop, sub_app, forwarded_client) -> AsyncIterable[AiohttpClient]:
    api_client = await forwarded_client(sub_app)

    yield api_client

    for collection in sub_app.db.collections.values():
        await collection.flush()

    sub_app.db.drop_instance()


@pytest.fixture
def request_to_http(api):
    async def _inner(
        filename: str,
        method: Literal["post", "put", "get", "patch", "delete"],
        url: str,
        headers: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
    ):
        # Request
        request_headers = []
        if headers is not None:
            for key, value in headers.items():
                request_headers.append(f"{key}: {value}")
        request_headers_text = "\n".join(request_headers)

        request_body = ""
        if json_data is not None:
            request_body = json.dumps(json_data, ensure_ascii=False, indent=2)

        # Response
        response = await getattr(api, method.lower())(
            url,
            headers=headers,
            json=json_data,
        )

        status_line = f"HTTP/1.0 {response.status} {response.reason}"
        response_headers = "\n".join(f"{k}: {v}" for k, v in response.headers.items() if k not in ("Date", "Server"))

        response_text = await response.text()
        try:
            parsed = json.loads(response_text)
            response_text = json.dumps(parsed, ensure_ascii=False, indent=2)
        except json.JSONDecodeError:
            pass

        # Write to file
        with open(filename, "w", encoding="utf-8") as f:
            f.write(f"{method.upper()} {url} HTTP/1.0\n")
            if request_headers_text:
                f.write(request_headers_text + "\n")
            f.write("\n")
            if request_body:
                f.write(request_body + "\n\n")
            f.write("\n")
            f.write(status_line + "\n")
            if response_headers:
                f.write(response_headers + "\n")
            f.write("\n")
            f.write(response_text)

        return response

    return _inner
