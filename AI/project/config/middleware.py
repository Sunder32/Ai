
from django.http import JsonResponse


class RateLimitMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_exception(self, request, exception):
        from django_ratelimit.exceptions import Ratelimited
        
        if isinstance(exception, Ratelimited):
            return JsonResponse({
                'error': 'Превышен лимит запросов',
                'message': 'Слишком много запросов. Пожалуйста, подождите немного.',
                'detail': 'Rate limit exceeded. Please try again later.'
            }, status=429)
        
        return None
