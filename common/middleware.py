import json
from django.http import HttpResponseBadRequest

class JsonBodyMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Check if the request is JSON
        if request.content_type == 'application/json':
            try:
                # Parse the JSON body and attach it to the request
                request.data = json.loads(request.body.decode('utf-8'))
            except json.JSONDecodeError:
                return HttpResponseBadRequest("Invalid JSON data")
        else:
            # If it's not JSON, set request.data to None
            request.data = {}

        response = self.get_response(request)
        return response
