"""Tests for timeout and retry CLI configuration."""

import subprocess

import httpx
import pytest

from moviebox_api.constants import (
    DEFAULT_CONNECT_RETRIES,
    DEFAULT_CONNECT_TIMEOUT,
    DEFAULT_POOL_TIMEOUT,
    DEFAULT_READ_TIMEOUT,
    DEFAULT_RETRY_BACKOFF,
    DEFAULT_WRITE_TIMEOUT,
)
from moviebox_api.requests import Session


def run_system_command(command: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        "python -m moviebox_api " + command,
        shell=True,
        text=True,
        capture_output=True,
    )


class TestDefaultConstants:
    def test_default_connect_timeout(self):
        assert DEFAULT_CONNECT_TIMEOUT == 20.0

    def test_default_read_timeout(self):
        assert DEFAULT_READ_TIMEOUT == 60.0

    def test_default_write_timeout(self):
        assert DEFAULT_WRITE_TIMEOUT == 20.0

    def test_default_pool_timeout(self):
        assert DEFAULT_POOL_TIMEOUT == 20.0

    def test_default_connect_retries(self):
        assert DEFAULT_CONNECT_RETRIES == 5

    def test_default_retry_backoff(self):
        assert DEFAULT_RETRY_BACKOFF == 0.6


class TestTimeoutObjectCreation:
    def test_httpx_timeout_construction(self):
        timeout = httpx.Timeout(
            connect=DEFAULT_CONNECT_TIMEOUT,
            read=DEFAULT_READ_TIMEOUT,
            write=DEFAULT_WRITE_TIMEOUT,
            pool=DEFAULT_POOL_TIMEOUT,
        )
        assert timeout.connect == DEFAULT_CONNECT_TIMEOUT
        assert timeout.read == DEFAULT_READ_TIMEOUT
        assert timeout.write == DEFAULT_WRITE_TIMEOUT
        assert timeout.pool == DEFAULT_POOL_TIMEOUT

    def test_custom_timeout_construction(self):
        timeout = httpx.Timeout(connect=30.0, read=120.0, write=30.0, pool=30.0)
        assert timeout.connect == 30.0
        assert timeout.read == 120.0

    def test_transport_with_retries(self):
        transport = httpx.AsyncHTTPTransport(retries=DEFAULT_CONNECT_RETRIES)
        assert transport is not None

    def test_session_accepts_timeout_and_transport(self):
        timeout = httpx.Timeout(
            connect=DEFAULT_CONNECT_TIMEOUT,
            read=DEFAULT_READ_TIMEOUT,
            write=DEFAULT_WRITE_TIMEOUT,
            pool=DEFAULT_POOL_TIMEOUT,
        )
        transport = httpx.AsyncHTTPTransport(retries=DEFAULT_CONNECT_RETRIES)
        session = Session(timeout=timeout, transport=transport)
        assert session._timeout == timeout
        assert session._httpx_kwargs.get("transport") is transport

    def test_session_stores_httpx_kwargs(self):
        transport = httpx.AsyncHTTPTransport(retries=3)
        session = Session(transport=transport)
        assert session._httpx_kwargs.get("transport") is transport


@pytest.mark.parametrize(
    "command",
    [
        "download-movie --help",
        "download-series --help",
    ],
)
def test_timeout_options_in_help(command):
    result = run_system_command(command)
    assert result.returncode == 0
    output = result.stdout
    assert "--connect-timeout" in output
    assert "--read-timeout" in output
    assert "--write-timeout" in output
    assert "--pool-timeout" in output
    assert "--connect-retries" in output
    assert "--retry-backoff" in output
