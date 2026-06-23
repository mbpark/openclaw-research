# Category 3: Systems Design

## Task 3.1: Minimal HTTP Server with Middleware

**Description:**
Implement a minimal HTTP server supporting routing, middleware chain, and error handling.

**Interface:**
```python
from typing import Callable, Optional, Dict
from dataclasses import dataclass
from enum import Enum


class HttpMethod(Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"


@dataclass
class Request:
    method: HttpMethod
    path: str
    headers: Dict[str, str]
    body: bytes = b""
    path_params: Dict[str, str] = None


@dataclass
class Response:
    status: int
    headers: Dict[str, str] = None
    body: bytes = b""


RequestHandler = Callable[[Request], Response]
Middleware = Callable[[Request, RequestHandler], Response]


class Router:
    def get(self, path: str) -> Callable:
        """Register GET handler."""
        ...

    def post(self, path: str) -> Callable:
        """Register POST handler."""
        ...

    def handle(self, request: Request) -> Response:
        """Route request to appropriate handler."""
        ...


class Server:
    def __init__(self):
        self._middleware: list = []
        self._handlers: dict = {}

    def use(self, middleware: Middleware):
        """Add middleware."""
        ...

    def get(self, path: str, handler: RequestHandler):
        """Register GET route."""
        ...

    def handle_request(self, request: Request) -> Response:
        """Process request through middleware chain."""
        ...
```

**What to evaluate:**
- Correct request parsing
- Middleware chain composition
- Error handling at each level
- Routing edge cases

**Scoring:** __ / 6
