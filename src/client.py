"""
API Client Library - Auto-generated from PRD.md
"""

from typing import Dict, Any, Optional
import requests
from src.config import Config


class APIClient:
    """HTTP client for OpenAlex API Python Client using requests."""

    def __init__(self, config: Config):
        self.config = config
        self.base_url = config.get('base_url', 'https://api.openalex.org')
        self.session = requests.Session()
        self.api_key = self.config.get('api_key', '')
        self._setup_auth()

    def _setup_auth(self):
        # OpenAlex authenticates via query string, not headers.
        return

    def _request(self, method: str, endpoint: str, params: Optional[Dict] = None, data: Optional[Dict] = None) -> Dict[str, Any]:
        url = f"{self.base_url}{endpoint}"
        request_params = dict(params or {})
        if self.api_key:
            request_params['api_key'] = self.api_key
        response = self.session.request(method=method, url=url, params=request_params or None, json=data, timeout=30)
        try:
            response.raise_for_status()
        except requests.HTTPError as exc:
            # Avoid leaking query-string credentials in exception messages.
            status = response.status_code
            reason = response.reason
            raise requests.HTTPError(f"{status} {reason} for {method} {url}") from exc
        if not response.text:
            return {}
        return response.json()

    def get(self, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        return self._request('GET', endpoint, params=params)

    def post(self, endpoint: str, data: Dict) -> Dict[str, Any]:
        return self._request('POST', endpoint, data=data)

    def put(self, endpoint: str, data: Dict) -> Dict[str, Any]:
        return self._request('PUT', endpoint, data=data)

    def delete(self, endpoint: str) -> Dict[str, Any]:
        result = self._request('DELETE', endpoint)
        return result if result else {"status": "deleted"}
