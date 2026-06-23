"""
Task 3.1: Minimal HTTP Server with Middleware

Implements HTTP server with request routing, middleware chain, and error handling.
"""

from typing import Callable, Optional, Dict, List, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum


class HttpMethod(Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"


class HTTPException(Exception):
    """Base HTTP exception."""
    def __init__(self, status: int, message: str):
        self.status = status
        self.message = message
        super().__init__(message)


@dataclass
class Request:
    method: HttpMethod
    path: str
    headers: Dict[str, str]
    body: bytes = b""
    path_params: Optional[Dict[str, str]] = None
    query_params: Optional[Dict[str, str]] = None

    def __post_init__(self):
        self.path_params = self.path_params or {}
        self.query_params = self.query_params or {}


@dataclass
class Response:
    status: int
    headers: Optional[Dict[str, str]] = None
    body: bytes = b""

    def __post_init__(self):
        self.headers = self.headers or {}


@dataclass
class Route:
    method: HttpMethod
    path_pattern: str
    handler: Callable


class RequestHandler:
    """Routes requests through middleware chain."""

    def __init__(self):
        self._routes: Dict[Tuple[HttpMethod, str], Route] = {}
        self._middleware: List[Callable] = []
        self._error_handler: Optional[Callable] = None

    def use(self, middleware: Callable):
        """Register middleware. Middleware: (request, next_fn) -> response"""
        self._middleware.append(middleware)

    def add_route(self, method: HttpMethod, path: str, handler: Callable):
        """Register a route."""
        self._routes[(method, path)] = Route(method, path, handler)

    def set_error_handler(self, handler: Callable):
        """Set custom error handler."""
        self._error_handler = handler

    def get_handler(self, method: HttpMethod, path: str) -> Optional[Callable]:
        """Find handler for method and path."""
        return self._routes.get((method, path))

    def handle_request(self, request: Request) -> Response:
        """Process request through middleware chain."""
        try:
            route = self.get_handler(request.method, request.path)
            if not route:
                raise HTTPException(404, "Not Found")
            handler = route.handler

            # Apply middleware to handler
            wrapped_handler = handler
            for mw in self._middleware:
                wrapped_handler = self._wrap_with_middleware(mw, wrapped_handler)

            return wrapped_handler(request)

        except HTTPException as e:
            return self._handle_error(request, e)
        except Exception as e:
            return self._handle_error(request, e)

    def _wrap_with_middleware(self, middleware, handler):
        """Wrap a handler with middleware."""
        def wrapper(request: Request) -> Response:
            return middleware(request, handler)
        return wrapper

    def _handle_error(self, request: Request, error: Exception) -> Response:
        """Handle errors during request processing."""
        if self._error_handler:
            try:
                return self._error_handler(request, error)
            except Exception:
                return self._default_error_response()

        if isinstance(error, HTTPException):
            if error.status == 404:
                return self._default_not_found(request)

        return self._default_error_response()

    def _default_error_response(self) -> Response:
        """Default error response."""
        return Response(
            status=500,
            headers={"Content-Type": "application/json"},
            body=b'{"error": "Internal Server Error"}'
        )

    def _default_not_found(self, request: Request) -> Response:
        """Default 404 response."""
        return Response(
            status=404,
            headers={"Content-Type": "application/json"},
            body=b'{"error": "Not Found"}'
        )


def test_http_server():
    """Test HTTP server functionality."""
    handler = RequestHandler()

    def test_endpoint(request: Request) -> Response:
        return Response(
            status=200,
            body=b"Test Response",
            headers={"Content-Type": "text/plain"}
        )

    def middleware_fn(request: Request, handler_func):
        """Simple middleware."""
        request.headers["X-Test"] = "true"
        response = handler_func(request)
        response.headers["X-Middleware"] = "true"
        return response

    handler.use(middleware_fn)
    handler.add_route(HttpMethod.GET, "/test", test_endpoint)

    request = Request(
        method=HttpMethod.GET,
        path="/test",
        headers={}
    )

    response = handler.handle_request(request)
    assert response.status == 200
    assert b"Test Response" in response.body
    assert response.headers.get("X-Middleware") == "true"

    # Test 404
    request = Request(
        method=HttpMethod.GET,
        path="/nonexistent",
        headers={}
    )
    response = handler.handle_request(request)
    assert response.status == 404

    print("Tests passed")


if __name__ == "__main__":
    test_http_server()
