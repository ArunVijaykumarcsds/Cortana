"""ASGI middleware that rejects request bodies larger than the configured limit."""

from typing import Dict

from starlette.types import ASGIApp, Message, Receive, Scope, Send


MAX_REQUEST_SIZE = 2 * 1024 * 1024  # 2 MiB


class RequestSizeLimitMiddleware:
    """Enforce a body limit for both Content-Length and chunked requests."""

    def __init__(self, app: ASGIApp, max_size: int = MAX_REQUEST_SIZE):
        self.app = app
        self.max_size = max_size

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        headers: Dict[bytes, bytes] = dict(scope.get("headers", []))
        content_length = headers.get(b"content-length")
        if content_length is not None:
            try:
                if int(content_length) > self.max_size:
                    await self._send_too_large(send)
                    return
            except ValueError:
                # A malformed header cannot be trusted; the body is still checked below.
                pass

        body = bytearray()
        while True:
            message = await receive()
            if message["type"] != "http.request":
                if message["type"] == "http.disconnect":
                    return
                continue
            body.extend(message.get("body", b""))
            if len(body) > self.max_size:
                await self._send_too_large(send)
                return
            if not message.get("more_body", False):
                break

        delivered = False

        async def receive_body() -> Message:
            nonlocal delivered
            if delivered:
                return {"type": "http.request", "body": b"", "more_body": False}
            delivered = True
            return {"type": "http.request", "body": bytes(body), "more_body": False}

        await self.app(scope, receive_body, send)

    @staticmethod
    async def _send_too_large(send: Send) -> None:
        payload = b'{"error":"Request entity too large"}'
        await send(
            {
                "type": "http.response.start",
                "status": 413,
                "headers": [
                    (b"content-type", b"application/json"),
                    (b"content-length", str(len(payload)).encode("ascii")),
                ],
            }
        )
        await send({"type": "http.response.body", "body": payload})
