from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
from django.contrib.auth import get_user_model
from datetime import datetime, timedelta
import jwt, pytz
from django.core.cache import cache
from django.http import HttpResponseRedirect

User = get_user_model()

class JWTMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if '/callback/' in request.path:
            return self.process_callback(request)

        if request.headers.get('X-Internal-Request') == 'true' or request.path in self.get_unauthenticated_paths() or '/game/close/' in request.path or '/admin/' in request.path:
            return None

        access_token = request.COOKIES.get('access_token')
        if not access_token:
            return HttpResponseRedirect('/login')

        try:
            decoded = jwt.decode(access_token, settings.JWT_SECRET_KEY, algorithms=["HS256"])
            user = self.get_user(decoded.get('user_id'))
            if not user:
                return HttpResponseRedirect('/login/')

            if decoded == jwt.decode(user.acc, settings.JWT_SECRET_KEY, algorithms=["HS256"]):
                request.user = user
                return None
        except jwt.ExpiredSignatureError:
            return self.handle_refresh_token(request)
        except jwt.InvalidTokenError:
            return HttpResponseRedirect('/login/')

    def get_user(self, user_id):
        user = cache.get(f'user_{user_id}')
        if not user:
            user = User.objects.get(id=user_id)
            cache.set(f'user_{user_id}', user, 300)
        return user

    def handle_refresh_token(self, request):
        refresh_token = request.COOKIES.get('refresh_token')
        if not refresh_token:
            return JsonResponse({'error': 'Authentication credentials were not provided or are expired.'}, status=401)
        
        try:
            decoded = jwt.decode(refresh_token, settings.JWT_REFRESH_SECRET_KEY, algorithms=["HS256"])
            user = self.get_user(decoded.get('user_id'))
            if user:
                user = User.objects.get(id=decoded.get('user_id'))
                cache.set(f'user_{user.id}', user, 300)
                new_access_token, new_refresh_token = self.generate_jwt_tokens(decoded.get('user_id'))
                user.acc = new_access_token
                user.ref = new_refresh_token
                user.save()
                request.new_access_token = new_access_token
                request.new_refresh_token = new_refresh_token
                request.user = user
                return None
            else:
                return HttpResponseRedirect('/login/')
        except jwt.ExpiredSignatureError:
            return HttpResponseRedirect('/login/')
        except jwt.InvalidTokenError:
            return HttpResponseRedirect('/login/')

    def generate_jwt_tokens(self, user_id):
        access_token = jwt.encode({
            'user_id': user_id,
            'exp': datetime.now(pytz.utc) + timedelta(minutes=5)
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
            '/game/need_update',
            '/game/join',
            '/validate-session/',
            '/auth_view/',
            '/twofa/',
            '/qrcode_2fa/',
            '/code_2fa/',
            '/mail_2fa/',
            '/verify_qrcode/',
            '/verify/',
            '/login42/'
        ]

    def process_callback(self, request):
        state = request.GET.get('state', None)
        if state and 'oauth_state_login'in request.session and state == request.session['oauth_state_login']:
            return None
        else:
            return  HttpResponseRedirect('/login/')
    
class TokenRefreshResponseMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if hasattr(request, 'new_access_token') and hasattr(request, 'new_refresh_token'):
            response.set_cookie('access_token', request.new_access_token, httponly=True, secure=True)
            response.set_cookie('refresh_token', request.new_refresh_token, httponly=True, secure=True)

        return response