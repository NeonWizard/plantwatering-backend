# Modified copy of https://github.com/sseemayer/hug_middleware_cors/
# Allows all HTTP methods through CORS until
# https://github.com/sseemayer/hug_middleware_cors/issues/1 is resolved

from typing import Sequence


class CORSMiddleware(object):
    """A middleware for allowing cross-origin request sharing (CORS)

    Adds appropriate Access-Control-* headers to the HTTP responses returned from the hug API,
    especially for HTTP OPTIONS responses used in CORS preflighting.
    """
    __slots__ = ('api', 'allow_origins', 'allow_credentials', 'max_age')

    def __init__(self, api, allow_origins: Sequence[str]=['*'], allow_credentials: bool=True, max_age: int=None):
        self.api = api
        self.allow_origins = allow_origins
        self.allow_credentials = allow_credentials
        self.max_age = max_age

    def process_response(self, request, response, resource):
        """Add CORS headers to the response"""

        # return list of allowed origins
        response.set_header('Access-Control-Allow-Origin', ', '.join(self.allow_origins))

        # return whether credentials are allowed
        response.set_header('Access-Control-Allow-Credentials', str(self.allow_credentials).lower())

        # check if we are handling a preflight request
        if request.method == 'OPTIONS':

            # return allowed methods
            response.set_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE')

            # get all requested headers and echo them back
            requested_headers = request.get_header('Access-Control-Request-Headers')
            response.set_header('Access-Control-Allow-Headers', requested_headers)

            # return valid caching time
            if self.max_age:
                response.set_header('Access-Control-Max-Age', self.max_age)
