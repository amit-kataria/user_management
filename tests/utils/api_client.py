import logging
import requests
import json
from typing import Optional, Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class APIClient:
    """
    A wrapper around requests to behave like RestAssured.
    Handles base URL, authentication headers, and logging.
    """

    def __init__(self, base_url: str, token: Optional[str] = None):
        self.base_url = base_url.rstrip("/")
        self.token = token
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        if self.token:
            self.headers["Authorization"] = f"Bearer {self.token}"

    def set_token(self, token: str):
        """Update the bearer token."""
        self.token = token
        self.headers["Authorization"] = f"Bearer {self.token}"

    def _log_request(self, method: str, url: str, params: Optional[Dict], data: Any):
        logger.info(f"REQUEST: {method} {url}")
        if params:
            logger.info(f"PARAMS: {json.dumps(params, default=str)}")
        if data:
            if isinstance(data, dict) or isinstance(data, list):
                logger.info(f"BODY: {json.dumps(data, default=str)}")
            else:
                logger.info(f"BODY: {str(data)}")

    def _log_response(self, response: requests.Response):
        logger.info(f"RESPONSE: {response.status_code} {response.reason}")
        try:
            body = response.json()
            logger.info(f"BODY: {json.dumps(body, indent=2, default=str)}")
        except ValueError:
            logger.info(f"BODY: {response.text}")

    def request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict] = None,
        data: Any = None,
        **kwargs,
    ) -> requests.Response:
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        self._log_request(method, url, params, data)

        try:
            # Handle JSON body automatically
            json_data = None
            if data is not None and isinstance(data, (dict, list)):
                json_data = data
                data = None

            response = requests.request(
                method=method,
                url=url,
                params=params,
                data=data,
                json=json_data,
                headers=self.headers,
                **kwargs,
            )
            self._log_response(response)
            return response
        except Exception as e:
            logger.error(f"Request failed: {e}")
            raise

    def get(
        self, endpoint: str, params: Optional[Dict] = None, **kwargs
    ) -> requests.Response:
        return self.request("GET", endpoint, params=params, **kwargs)

    def post(self, endpoint: str, data: Any = None, **kwargs) -> requests.Response:
        return self.request("POST", endpoint, data=data, **kwargs)

    def put(self, endpoint: str, data: Any = None, **kwargs) -> requests.Response:
        return self.request("PUT", endpoint, data=data, **kwargs)

    def delete(
        self, endpoint: str, params: Optional[Dict] = None, data: Any = None, **kwargs
    ) -> requests.Response:
        return self.request("DELETE", endpoint, params=params, data=data, **kwargs)

    def patch(self, endpoint: str, data: Any = None, **kwargs) -> requests.Response:
        return self.request("PATCH", endpoint, data=data, **kwargs)
