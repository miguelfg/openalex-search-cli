"""
API Client Library - Auto-generated from PRD.md
"""

from typing import Any, Dict, Optional

import requests

from src.config import Config


class APIClient:
    """HTTP client for OpenAlex API Python Client using requests."""

    def __init__(self, config: Config):
        self.config = config
        self.base_url = config.get("base_url", "https://api.openalex.org")
        self.session = requests.Session()
        self.api_key = self.config.get("api_key", "")
        self._setup_auth()

    def _setup_auth(self):
        # OpenAlex authenticates via query string, not headers.
        return

    @staticmethod
    def _validate_endpoint(endpoint: str) -> None:
        # Root-cause guard: endpoints are built by interpolating untrusted input
        # (CLI ids, batch-file paths) into a path string. Keep requests on-host
        # and on-path so a crafted value can't retarget the request (and leak the
        # api_key) or escape into another resource.
        if (
            not endpoint.startswith("/")
            or endpoint.startswith("//")
            or ".." in endpoint
            or "%2f" in endpoint.lower()
            or any(c in endpoint for c in "?#")
            or any(c.isspace() for c in endpoint)
        ):
            raise ValueError(f"Unsafe endpoint: {endpoint!r}")

    def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict] = None,
        data: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        self._validate_endpoint(endpoint)
        url = f"{self.base_url}{endpoint}"
        request_params = dict(params or {})
        if self.api_key:
            request_params["api_key"] = self.api_key
        response = self.session.request(
            method=method, url=url, params=request_params or None, json=data, timeout=30
        )
        try:
            response.raise_for_status()
        except requests.HTTPError:
            # Avoid leaking query-string credentials in exception messages.
            status = response.status_code
            reason = response.reason
            raise requests.HTTPError(f"{status} {reason} for {method} {url}") from None
        if not response.text:
            return {}
        return response.json()

    def get(self, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        return self._request("GET", endpoint, params=params)
