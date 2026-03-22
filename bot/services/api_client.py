"""LMS API client with Bearer token authentication.

Makes HTTP requests to the backend with proper error handling.
All errors are returned as descriptive strings — no raw tracebacks.
"""

import httpx
from typing import Any


class LMSAPIClient:
    """Client for the LMS backend API."""

    def __init__(self, base_url: str, api_key: str) -> None:
        """Initialize the API client.

        Args:
            base_url: Backend base URL (e.g., http://localhost:42002)
            api_key: API key for authentication
        """
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self._headers = {"Authorization": f"Bearer {api_key}"}

    async def get(self, endpoint: str, params: dict[str, Any] | None = None) -> dict | list | None:
        """Make a GET request to the backend.

        Args:
            endpoint: API endpoint (e.g., "/items/", "/analytics/pass-rates")
            params: Optional query parameters

        Returns:
            JSON response as dict/list, or None on error

        Raises:
            ConnectionError: If backend is unreachable
            httpx.HTTPStatusError: If backend returns an error status
        """
        url = f"{self.base_url}{endpoint}"
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, headers=self._headers, params=params, timeout=10.0)
                response.raise_for_status()
                return response.json()
            except httpx.ConnectError as e:
                raise ConnectionError(f"connection refused ({self.base_url}). Check that the services are running.") from e
            except httpx.HTTPStatusError as e:
                raise httpx.HTTPStatusError(f"HTTP {e.response.status_code} {e.response.reason_phrase}. The backend service may be down.", request=e.request, response=e.response) from e

    def format_error_message(self, error: Exception) -> str:
        """Format an exception as a user-friendly error message.

        Args:
            error: The exception that occurred

        Returns:
            User-friendly error message including the actual error
        """
        if isinstance(error, ConnectionError):
            return f"Backend error: {error}"
        elif isinstance(error, httpx.HTTPStatusError):
            return f"Backend error: {error}"
        else:
            return f"Backend error: {type(error).__name__}: {error}"
