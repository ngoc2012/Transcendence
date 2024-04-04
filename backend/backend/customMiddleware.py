from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
import jwt, os
from django.conf import settings
from django.contrib.auth import authenticate, login, get_user_model, logout
from datetime import datetime, timedelta
import requests, pyotp, secrets, os, random, jwt, string, pytz

class JWTMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # print(request.META)
        if '/admin/' in request.path or request.path in self.get_unauthenticated_paths():
            return None

        access_token = request.COOKIES.get('access_token')
        if access_token:
            print('access token enter')
            try:
                decoded = jwt.decode(access_token, settings.JWT_SECRET_KEY, algorithms=["HS256"])
                jwtid = decoded.get('user_id')
                if jwtid:
                    User = get_user_model()
                    user = User.objects.get(id=jwtid)
                    if decoded == jwt.decode(user.acc, settings.JWT_SECRET_KEY, algorithms=["HS256"]):
                        request.user = user
                    else:
                        print('key not the same as in db')
                else:
                    return JsonResponse({'error': 'User not found'}, status=404)
            except jwt.ExpiredSignatureError:
                refresh_token = request.COOKIES.get('refresh_token')
                if refresh_token:
                    print('refresh token enter')
                    try:
                        decoded = jwt.decode(refresh_token, settings.JWT_REFRESH_SECRET_KEY, algorithms=["HS256"])
                        new_accces_token, new_refresh_token = self.generate_jwt_tokens(decoded.get('user_id'))
                        request.new_access_token = new_accces_token
                        request.new_refresh_token = new_refresh_token
                        User = get_user_model()
                        user = User.objects.get(id=decoded.get('user_id'))
                        request.user = user
                        user.acc = new_accces_token
                        user.ref = new_refresh_token
                        user.save()
                        return None
                    except jwt.ExpiredSignatureError:
                        return JsonResponse({'error': 'Refresh token expired'}, status=401)
                    except jwt.InvalidTokenError:
                        return JsonResponse({'error': 'Invalid refresh token'}, status=401)
                else:
                    return JsonResponse({'error': 'Authentication credentials were not provided or are expired.'}, status=401)
            except jwt.InvalidTokenError:
                return JsonResponse({'error': 'Invalid token'}, status=401)
        else:
            return JsonResponse({'error': 'Authorization header is missing or invalid'}, status=401)

        return None

    def generate_jwt_tokens(self, user_id):
        access_token = jwt.encode({
            'user_id': user_id,
            'exp': datetime.now(pytz.utc) + timedelta(minutes=1)
        }, settings.JWT_SECRET_KEY, algorithm='HS256')

        refresh_token = jwt.encode({
            'user_id': user_id,
            'exp': datetime.now(pytz.utc) + timedelta(days=7)
        }, settings.JWT_REFRESH_SECRET_KEY, algorithm='HS256')

        return access_token, refresh_token
    
    def get_unauthenticated_paths(self):
            return [
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
    
class TokenRefreshResponseMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if hasattr(request, 'new_access_token') and hasattr(request, 'new_refresh_token'):
            response.set_cookie('access_token', request.new_access_token, httponly=True, secure=True)
            response.set_cookie('refresh_token', request.new_refresh_token, httponly=True, secure=True)

        return response