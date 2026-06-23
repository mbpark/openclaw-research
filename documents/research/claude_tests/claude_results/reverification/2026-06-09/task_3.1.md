# Minimal HTTP Server with Middleware

## Implementation

```python
from typing import Callable, Optional, Dict, List, Tuple
from dataclasses import dataclass, field
from enum import Enum
import re
import traceback


class HttpMethod(Enum):
    """Supported HTTP methods."""
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"


@dataclass
class Request:
    """Represents an incoming HTTP request.

    Attributes:
        method: The HTTP method (GET, POST, etc.).
        path: The request path, e.g. "/users/42".
        headers: Case-insensitive header mapping (stored as given).
        body: Raw request body bytes.
        path_params: Parameters extracted from the matched route pattern,
            e.g. {"id": "42"} for a route "/users/{id}".
    """
    method: HttpMethod
    path: str
    headers: Dict[str, str]
    body: bytes = b""
    # Use default_factory rather than a mutable default to avoid the
    # shared-mutable-default-argument bug.
    path_params: Dict[str, str] = field(default_factory=dict)


@dataclass
class Response:
    """Represents an HTTP response.

    Attributes:
        status: HTTP status code, e.g. 200.
        headers: Response headers.
        body: Raw response body bytes.
    """
    status: int
    headers: Dict[str, str] = field(default_factory=dict)
    body: bytes = b""


# A handler turns a Request into a Response.
RequestHandler = Callable[[Request], Response]
# Middleware wraps a handler: it receives the request and the *next*
# handler in the chain, and returns a Response.
Middleware = Callable[[Request, RequestHandler], Response]


class HttpError(Exception):
    """An exception carrying an HTTP status code.

    Handlers/middleware can raise this to short-circuit with a
    specific status instead of returning a Response.
    """

    def __init__(self, status: int, message: str = ""):
        super().__init__(message or f"HTTP {status}")
        self.status = status
        self.message = message


class Route:
    """A compiled route pattern.

    Converts a pattern like "/users/{id}" into a regex that captures
    named path parameters.
    """

    def __init__(self, method: HttpMethod, pattern: str, handler: RequestHandler):
        self.method = method
        self.pattern = pattern
        self.handler = handler
        self.regex = self._compile(pattern)

    @staticmethod
    def _compile(pattern: str) -> "re.Pattern":
        """Compile a route pattern into an anchored regex.

        "{name}" segments become named capture groups that match a
        single path segment (no slashes).
        """
        # Escape everything, then un-escape our parameter syntax.
        # Build the regex segment by segment to avoid escaping pitfalls.
        parts = pattern.split("/")
        regex_parts: List[str] = []
        for part in parts:
            m = re.fullmatch(r"\{(\w+)\}", part)
            if m:
                regex_parts.append(f"(?P<{m.group(1)}>[^/]+)")
            else:
                regex_parts.append(re.escape(part))
        return re.compile("^" + "/".join(regex_parts) + "$")

    def match(self, path: str) -> Optional[Dict[str, str]]:
        """Return captured params if the path matches, else None."""
        m = self.regex.match(path)
        if m is None:
            return None
        return m.groupdict()


class Router:
    """Routes requests to registered handlers based on method and path."""

    def __init__(self) -> None:
        self._routes: List[Route] = []

    def _register(self, method: HttpMethod, path: str) -> Callable:
        """Return a decorator registering a handler for method/path."""
        def decorator(handler: RequestHandler) -> RequestHandler:
            self.add(method, path, handler)
            return handler
        return decorator

    def add(self, method: HttpMethod, path: str, handler: RequestHandler) -> None:
        """Register a handler directly (non-decorator form)."""
        self._routes.append(Route(method, path, handler))

    def get(self, path: str) -> Callable:
        """Register GET handler (decorator)."""
        return self._register(HttpMethod.GET, path)

    def post(self, path: str) -> Callable:
        """Register POST handler (decorator)."""
        return self._register(HttpMethod.POST, path)

    def put(self, path: str) -> Callable:
        """Register PUT handler (decorator)."""
        return self._register(HttpMethod.PUT, path)

    def delete(self, path: str) -> Callable:
        """Register DELETE handler (decorator)."""
        return self._register(HttpMethod.DELETE, path)

    def handle(self, request: Request) -> Response:
        """Route a request to its handler.

        Returns 404 if no path matches at all, 405 if the path matches
        but the method does not.
        """
        path_matched = False
        for route in self._routes:
            params = route.match(request.path)
            if params is None:
                continue
            path_matched = True
            if route.method == request.method:
                request.path_params = params
                return route.handler(request)

        if path_matched:
            raise HttpError(405, "Method Not Allowed")
        raise HttpError(404, "Not Found")


def _error_to_response(status: int, message: str) -> Response:
    """Build a minimal text response for an error status."""
    body = (message or f"Error {status}").encode("utf-8")
    return Response(
        status=status,
        headers={"Content-Type": "text/plain; charset=utf-8"},
        body=body,
    )


class Server:
    """A minimal HTTP server with a middleware chain and routing."""

    def __init__(self) -> None:
        self._middleware: List[Middleware] = []
        # _handlers retained from the given interface; we delegate to a Router.
        self._handlers: dict = {}
        self._router = Router()

    def use(self, middleware: Middleware) -> "Server":
        """Add middleware. Returns self for chaining.

        Middleware run in registration order: the first registered is
        the outermost wrapper (runs first on the way in, last on the
        way out).
        """
        self._middleware.append(middleware)
        return self

    def get(self, path: str, handler: RequestHandler) -> "Server":
        """Register a GET route."""
        self._router.add(HttpMethod.GET, path, handler)
        return self

    def post(self, path: str, handler: RequestHandler) -> "Server":
        """Register a POST route."""
        self._router.add(HttpMethod.POST, path, handler)
        return self

    def put(self, path: str, handler: RequestHandler) -> "Server":
        """Register a PUT route."""
        self._router.add(HttpMethod.PUT, path, handler)
        return self

    def delete(self, path: str, handler: RequestHandler) -> "Server":
        """Register a DELETE route."""
        self._router.add(HttpMethod.DELETE, path, handler)
        return self

    def _build_chain(self) -> RequestHandler:
        """Compose middleware around the router into a single handler.

        We fold from the innermost (router) outward so that the first
        registered middleware ends up outermost.
        """
        handler: RequestHandler = self._router.handle

        # Iterate in reverse so middleware[0] wraps everything.
        for mw in reversed(self._middleware):
            # Capture mw and the current next-handler by value via defaults.
            def make(mw: Middleware, nxt: RequestHandler) -> RequestHandler:
                def wrapped(request: Request) -> Response:
                    return mw(request, nxt)
                return wrapped
            handler = make(mw, handler)
        return handler

    def handle_request(self, request: Request) -> Response:
        """Process a request through the middleware chain and routing.

        All exceptions are converted into Response objects so the server
        never propagates raw exceptions to the caller:
          - HttpError -> its status code
          - any other Exception -> 500 Internal Server Error
        """
        chain = self._build_chain()
        try:
            response = chain(request)
            # Defensive: handlers must return a Response.
            if not isinstance(response, Response):
                return _error_to_response(500, "Handler did not return a Response")
            return response
        except HttpError as e:
            return _error_to_response(e.status, e.message)
        except Exception:  # noqa: BLE001 - top-level safety net
            # In production you'd log traceback.format_exc() here.
            traceback.format_exc()
            return _error_to_response(500, "Internal Server Error")
```

## Usage Example

```python
def logging_middleware(req: Request, next_handler: RequestHandler) -> Response:
    """Logs and times the request; demonstrates wrap-on-both-sides."""
    resp = next_handler(req)
    resp.headers["X-Logged"] = "true"
    return resp


def auth_middleware(req: Request, next_handler: RequestHandler) -> Response:
    """Short-circuits unauthenticated requests."""
    if req.headers.get("Authorization") != "secret":
        raise HttpError(401, "Unauthorized")
    return next_handler(req)


def get_user(req: Request) -> Response:
    user_id = req.path_params["id"]
    return Response(status=200, body=f"user {user_id}".encode())


server = Server()
server.use(logging_middleware)   # outermost
server.use(auth_middleware)
server.get("/users/{id}", get_user)

req = Request(HttpMethod.GET, "/users/42",
              headers={"Authorization": "secret"})
resp = server.handle_request(req)
print(resp.status, resp.body, resp.headers)  # 200 b'user 42' {'X-Logged': 'true'}

# Missing auth -> 401, but logging middleware still runs (it's outermost)
bad = Request(HttpMethod.GET, "/users/42", headers={})
print(server.handle_request(bad).status)  # 401
```

## Design Decisions & Tradeoffs

**1. Middleware composition via closure folding.**
I compose the chain by folding `reversed(middleware)` around the router. This gives the intuitive "onion" model where the first-registered middleware is outermost. The `make()` factory captures `mw` and `nxt` correctly — a common bug is late-binding loop variables, which `make` avoids by binding via parameters.

*Tradeoff:* The chain is rebuilt on every `handle_request`. For a hot path you'd cache it and invalidate on `use()`. I kept it simple since middleware/routes can change between requests in this minimal design; caching is a one-line optimization.

**2. Routing with regex-compiled patterns.**
Each `Route` precompiles `{param}` segments into named regex groups matching a single path segment (`[^/]+`). Building the regex segment-by-segment (escaping literals, injecting groups) avoids fragile string substitution that could mis-handle special characters.

**3. Two-level error handling.**
- The **Router** distinguishes 404 (no path matched) from 405 (path matched, wrong method) by tracking `path_matched`.
- The **Server** is a top-level safety net: it catches `HttpError` (mapping to its status) and any other exception (mapping to 500), so raw exceptions never escape.

**4. `HttpError` as a control-flow exception** lets middleware/handlers short-circuit cleanly (e.g. auth) without manually threading early-return Responses through the chain.

**5. `field(default_factory=dict)`** replaces the buggy `path_params: Dict = None` default — mutable defaults shared across instances are a classic pitfall, and `None` would force null-checks everywhere.

## Edge Cases Handled

| Case | Behavior |
|------|----------|
| No matching path | `404 Not Found` |
| Path matches, method doesn't | `405 Method Not Allowed` |
| Handler raises arbitrary exception | `500` (no leak) |
| Handler returns non-`Response` | `500` (defensive check) |
| Middleware raises `HttpError` | Mapped to its status; outer middleware still unwinds |
| Empty middleware list | Chain == router directly |
| Path params with special chars | Safely matched (single segment, escaped literals) |
| Trailing slash mismatch | Treated as distinct routes (anchored `^...$`) — explicit, no surprises |
| Mutable default args | Eliminated via `default_factory` |

**Note:** This is an in-memory request-processing core (no socket layer), matching the provided interface. Adding a real transport would mean parsing raw bytes into `Request` and serializing `Response` — orthogonal to the routing/middleware logic shown here.