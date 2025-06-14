import json
import traceback
from django.http import JsonResponse
from django.conf import settings


class CustomExceptionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_exception(self, request, exception):
        response_data = {
            "status": "error",
            "message": str(exception),
            "type": exception.__class__.__name__,
            "path": request.path,
        }

        # Only include traceback in development
        if settings.DEBUG:
            response_data["traceback"] = traceback.format_exc()

        print(response_data)

        return JsonResponse(response_data, status=500)
