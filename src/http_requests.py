from aiolimiter import AsyncLimiter
from base64 import b64decode
import os
from tenacity import AsyncRetrying, retry, stop_after_attempt, wait_random_exponential
import httpx
from typing import Dict, Optional
from httpx import Response


from src.http_response import ResponseWrapper
from src.logger import logger



class BaseRequest:
    """
    Represents a base HTTP request.

    Args:
        url (str): The URL of the request.
        method (str, optional): The HTTP method of the request. Defaults to "GET".
        headers (Dict, optional): The headers of the request. Defaults to None.
        cookies (Dict, optional): The cookies of the request. Defaults to None.
        params (Dict, optional): The query parameters of the request. Defaults to None.
        data (Dict, optional): The request body data. Defaults to None.
        json (Dict, optional): The request body JSON. Defaults to None.
        verify (bool, optional): Whether to verify SSL certificates. Defaults to True.
        proxies (Dict, optional): The proxies to use for the request. Defaults to None.
    """

    TIMEOUT: int = 20
    RETRIES: int = 3
    DEFAULT_HEADERS: dict = {
        'User-Agent': "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9'
    }


    def __init__(
            self, url: str, 
            method: str = "GET", 
            headers: Dict = None,
            cookies: Dict = None,
            params: Dict = None,
            data: Dict = None,
            json: Dict = None,
            verify: bool = False,
            proxies: Dict = None,
            timeout: int = None
        ):
        self.url = url
        self.method = method
        self.headers = headers or self.DEFAULT_HEADERS
        self.cookies = cookies
        self.params = params
        self.data = data
        self.json = json
        self.verify = verify
        self.proxies = proxies
        self.timeout = timeout or self.TIMEOUT


    def __repr__(self):
        return f"{self.__class__.__name__}(url={self.url}, method={self.method})"


    def handle_failure(self, e: Exception) -> Response:
        """
        Handles a failure during the request.
        """
        logger.error(f"All retries failed to {self.url}: {e}", exc_info=True)
        return Response(status_code=420, url=self.url, text=str(e))



class Request(BaseRequest):
    """
    Represents an HTTP request.

    Methods:
        send: Sends the HTTP request and returns the response.
        process_request: Processes the HTTP request and returns a ResponseWrapper object.
    """

    @retry(stop=stop_after_attempt(BaseRequest.RETRIES), wait=wait_random_exponential(multiplier=1, min=4, max=10), reraise=True)
    def send(self) -> Response:
        """
        Sends the HTTP request and returns the response.
        """

        with httpx.Client(verify=self.verify, timeout=self.timeout, proxies=self.proxies) as client:
            response = client.request(
                url=self.url, 
                method=self.method, 
                headers=self.headers, 
                cookies=self.cookies, 
                params=self.params, 
                data=self.data, 
                json=self.json, 
            )
            response.raise_for_status()
            logger.debug(f"Request sent to {self.url}: {response.status_code}")
            return response


    def process_request(self) -> Optional[ResponseWrapper]:
        """
        Processes the HTTP request and returns a ResponseWrapper object.
        """

        try:
            response = self.send()
        except Exception as e:
            logger.error(e, exc_info=True)
            return None
        else:
            return ResponseWrapper(response)




class AsyncRequest(BaseRequest):
    """
    Represents an asynchronous HTTP request.

    Attributes:
        RATE_LIMIT (AsyncLimiter): The rate limiter for the request.

    Methods:
        send: Sends the request asynchronously and returns the response.
        process_request: Processes the HTTP request and returns a ResponseWrapper object
    """

    RATE_LIMIT: AsyncLimiter = AsyncLimiter(100, 60)


    async def send(self) -> Response:
        """
        Sends the HTTP request asynchronously.
        """

        async with httpx.AsyncClient(verify=self.verify, timeout=self.timeout, proxies=self.proxies) as client:
            async for attempt in AsyncRetrying(stop=stop_after_attempt(self.RETRIES), wait=wait_random_exponential(multiplier=1, min=4, max=10), reraise=True):
                with attempt:
                    async with self.RATE_LIMIT:
                        response = await client.request(
                            url=self.url, 
                            method=self.method, 
                            headers=self.headers, 
                            cookies=self.cookies, 
                            params=self.params, 
                            data=self.data, 
                            json=self.json, 
                        )
                        response.raise_for_status()
                        logger.debug(f"Request sent to {self.url}: {response.status_code}")
                        return response


    async def process_request(self) -> Optional[ResponseWrapper]:
        """
        Processes the HTTP request and returns a ResponseWrapper object.
        """

        try:
            response = await self.send()
        except Exception as e:
            logger.error(e, exc_info=True)
            return None
        else:
            return ResponseWrapper(response)




class Zyte_Request(Request):
    """
    Represents a request to the Zyte API.

    Args:
        zyte_api_key (str): The API key for accessing the Zyte API.
        browser (bool, optional): Whether to use browser rendering for the request. Defaults to False.

    Attributes:
        ZYTE_ENDPOINT (str): The endpoint URL for the Zyte API.

    Methods:
        send: Sends the HTTP request and returns the response.
        prepare_payload: Prepares the payload for the request.
        process_request: Processes the request and returns a wrapped response.
    """

    ZYTE_ENDPOINT: str = "https://api.zyte.com/v1/extract"


    def __init__(self, zyte_api_key: str = None, browser: bool = False, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.zyte_api_key = zyte_api_key or os.getenv("ZYTE_API_KEY")
        self.browser = browser


    @retry(stop=stop_after_attempt(BaseRequest.RETRIES), wait=wait_random_exponential(multiplier=1, min=4, max=10), reraise=True)
    def send(self) -> Response:
        """
        Sends the request synchronously and returns the response.
        """

        json_payload = self.prepare_payload()
        
        with httpx.Client(verify=self.verify, timeout=self.timeout) as client:
            response = client.post(self.ZYTE_ENDPOINT, auth=(self.zyte_api_key, ""), json=json_payload)
            response.raise_for_status()
            logger.debug(f"Request sent to {self.url}: {response.status_code}")

            if self.browser:
                http_response_body = response.json()["browserHtml"]
            else:
                http_response_body = b64decode(response.json()["httpResponseBody"]).decode()

            return Response(
                status_code=response.status_code, 
                request=client.build_request(url=self.url, method=self.method), 
                text=http_response_body
            )
        

    def prepare_payload(self) -> dict:
        """
        Prepares the payload for the request.
        """

        if self.browser:
            return {"url": self.url, "browserHtml": True}
        else:
            return {
                "url": self.url,
                "httpResponseBody": True,
                "httpRequestMethod": self.method
            }
        


class Zyte_AsyncRequest(AsyncRequest):
    """
    Represents a request to the Zyte API.

    Args:
        zyte_api_key (str): The API key for accessing the Zyte API.
        browser (bool, optional): Whether to use browser rendering for the request. Defaults to False.

    Attributes:
        ZYTE_ENDPOINT (str): The endpoint URL for the Zyte API.
        RATE_LIMIT: The rate limiter for the request.

    Methods:
        send: Sends the request asynchronously and returns the response.
        prepare_payload: Prepares the payload for the request.
        process_request: Processes the request and returns a wrapped response.
    """

    ZYTE_ENDPOINT: str = "https://api.zyte.com/v1/extract"


    def __init__(self, zyte_api_key: str = None, browser: bool = False, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.zyte_api_key = zyte_api_key or os.getenv("ZYTE_API_KEY")
        self.browser = browser


    async def send(self) -> Response:
        """
        Sends the request asynchronously and returns the response.
        """

        json_payload = self.prepare_payload()

        async with httpx.AsyncClient(verify=self.verify, timeout=self.timeout) as client:
            async for attempt in AsyncRetrying(stop=stop_after_attempt(self.RETRIES), wait=wait_random_exponential(multiplier=1, min=4, max=10), reraise=True):
                with attempt:
                    async with self.RATE_LIMIT:
                        response = await client.post(self.ZYTE_ENDPOINT, auth=(self.zyte_api_key, ""), json=json_payload)
                        response.raise_for_status()
                        logger.debug(f"Request sent to {self.url}: {response.status_code}")

                        if self.browser:
                            http_response_body = response.json()["browserHtml"]
                        else:
                            http_response_body = b64decode(response.json()["httpResponseBody"]).decode()

                        return Response(
                            status_code=response.status_code, 
                            request=client.build_request(url=self.url, method=self.method), 
                            text=http_response_body
                        )


    def prepare_payload(self) -> dict:
        """
        Prepares the payload for the request.
        """

        if self.browser:
            return {"url": self.url, "browserHtml": True}
        else:
            return {
                "url": self.url,
                "httpResponseBody": True,
                "httpRequestMethod": self.method
            }
