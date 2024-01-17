
# myapp/views.py
import json
import requests
from django.shortcuts import render, redirect
from django.http import HttpResponse

def index(request):
    return render(request, 'index.html')

def callback(request):
    code = request.GET.get('code')

    try:
        token_response = requests.post('https://api.intra.42.fr/oauth/token', data={
            'grant_type': 'authorization_code',
            'client_id': '',
            'client_secret': '',
            'code': code,
            'redirect_uri': 'http://localhost:8000/callback',  # Adjust as needed
        })

        token_data = token_response.json()
        # print('Access Token:', token_data['access_token'])
        access_token = token_data['access_token']
        # Handle the token as needed, e.g., store it in a session
        
        user_response = requests.get('https://api.intra.42.fr/v2/me', headers={
            'Authorization': f'Bearer {access_token}',
        })


        user_data = user_response.json()
        print('User Information:', user_data)


        # return redirect('https://google.com')  # Redirect after successful token exchange
        return render(request, 'success.html', {'user_data': user_data})



    except requests.RequestException as request_error:
        print('Error during token exchange - Request Exception:', request_error)
        return HttpResponse('Internal Server Error', status=500)
    except json.JSONDecodeError as json_error:
        print('Error during token exchange - JSON Decode Error:', json_error)
        return HttpResponse('Internal Server Error', status=500)
    except KeyError as key_error:
        print('Error during token exchange - Key Error:', key_error)
        return HttpResponse('Internal Server Error', status=500)
    except Exception as e:
        print('Unknown error during token exchange:', e)
        return HttpResponse('Internal Server Error', status=500)
    
    except Exception as e:
        print('Error during token exchange:', e)
        return HttpResponse('Internal Server Error', status=500)


# http://localhost:8000/callback.html



# recuperer les informations envoyée via le token
# comprendre chaque secction sur django