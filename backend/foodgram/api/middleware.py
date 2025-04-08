from django.http import HttpResponse

from api.models import BlacklistedTokens


class JWTBlacklistMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        auth_header = request.headers.get("Authorization")

        if auth_header and auth_header.startswith("Token "):
            token = auth_header.split(" ")[1]
            if BlacklistedTokens.objects.filter(token=token).exists():
                return HttpResponse(status=401)

        return self.get_response(request)
