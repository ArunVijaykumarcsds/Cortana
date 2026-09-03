import logging
import sys

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from pythonjsonlogger import jsonlogger

logger = logging.getLogger('cortana')
logger.setLevel(logging.INFO)
logger.propagate = False
if not logger.handlers:
    handler = logging.StreamHandler(sys.stdout)
    formatter = jsonlogger.JsonFormatter('%(asctime)s %(levelname)s %(name)s %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_info = {
            'method': request.method,
            'path': request.url.path,
            'client': request.client.host if request.client else None,
        }
        logger.info('request_start', extra=request_info)
        try:
            response: Response = await call_next(request)
        except Exception:
            # Stack traces can contain database URLs or request data.
            logger.error('unhandled_exception')
            raise
        response_info = {
            'status_code': response.status_code,
            'method': request.method,
            'path': request.url.path,
        }
        logger.info('request_end', extra=response_info)
        return response
