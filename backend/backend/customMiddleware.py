from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
import jwt, os
from django.conf import settings
from django.contrib.auth import authenticate, login

# JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')
# JWT_REFRESH_SECRET_KEY = os.environ.get('JWT_REFRESH_SECRET_KEY')

class JWTMiddleware(MiddlewareMixin):
    def process_request(self, request):
        print('request path:' + request.path)
        unauthenticated_paths = [
            '/',
            '/favicon.ico',
            '/get-csrf/',
            'pages/signup/',
            'pages/login/',
            '/pages/login/',
            '/login',
            '/log_in/',
            '/lobby/',
            '/game/update'
        ]
        if request.path in unauthenticated_paths:
            return None

        # JWT token verification
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        if not auth_header or not auth_header.startswith('Bearer '):
            return JsonResponse({'error': 'Authorization header is missing or invalid'}, status=401)
        
        token = auth_header.split(' ')[1]
        try:
            jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            return JsonResponse({'error': 'Token expired'}, status=401)
        except jwt.InvalidTokenError:
            return JsonResponse({'error': 'Invalid token'}, status=401)
        
        print('JWT auth OK')
        return None