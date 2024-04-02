from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
import jwt, os
from django.conf import settings
from django.contrib.auth import authenticate, login, get_user_model, logout

class JWTMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # print(request.META)
        # print('request path:' + request.path)
        if '/admin/' in request.path:
            return None

        unauthenticated_paths = [
            '/',
            '/favicon.ico',
            '/get-csrf/',
            'pages/signup/',
            '/pages/signup/',
            '/new_player/',
            'pages/login/',
            '/pages/login/',
            '/login',
            '/login/',
            '/log_in/',
            '/lobby/',
            '/lobby',
            '/admin/',
            '/admin/login/',
            '/game/update',
            '/validate-session/',
        ]
        if request.path in unauthenticated_paths:
            return None

        # JWT token verification
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        if not auth_header or not auth_header.startswith('Bearer '):
            return JsonResponse({'error': 'Authorization header is missing or invalid'}, status=401)
        
        token = auth_header.split(' ')[1]
        try:
           decoded = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            return JsonResponse({'error': 'Token expired'}, status=401)
        except jwt.InvalidTokenError:
            return JsonResponse({'error': 'Invalid token'}, status=401)
        
        print(request.user)
        if request.user.is_authenticated:
            print('user is auth')
            if decoded.get('user_id') != request.user.id:
                print(decoded.get('user_id') + '| logout')
                logout(request)
                return JsonResponse({'error': 'Login needed'}, status=401)
        else:
            return JsonResponse({'error': 'Login needed'}, status=401)
        
        return None