# Transcendence

## The game

[The Mechanics of Pong](https://dooglz.github.io/set09121/pong2)

## Start game

```console
python3 manage.py runserver 0.0.0.0:8000
```

## Bootstrap toolkit

[Introduction](https://getbootstrap.com/docs/4.6/getting-started/introduction/)

## Another games

2 players shoots each others for 3 minutes.

Bullets speed increase over times.

1 shot each second.

## Django

### Api
```
Transcendence
├── backend
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
├── pong
│   ├── __init__.py
│   ├── settings.py
│   ├── apps.py
│   └── views.py
└── manage.py
```

[Api urls in subfolder](https://stackoverflow.com/questions/10313475/moving-django-apps-into-subfolder-and-url-py-error)

### Static files
If your JavaScript file is in a location that is not served by Django's development server, you need to make sure it's configured as a static file. In your Django project, you should have a folder named `static` where you store your static files (CSS, JavaScript, images, etc.). Ensure that your JavaScript file is placed in the appropriate static folder.

Update your `settings.py` to include your static files:

```
# settings.py
import os

# ...

STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]

# ...
```

Add or update the `STATIC_ROOT` setting to point to a directory where you want to collect all your static files. For example:

```
# settings.py

# Your existing settings...

# Add or update this line
STATIC_ROOT = BASE_DIR / 'staticfiles'
```
Replace `'staticfiles'` with the desired directory path. `BASE_DIR` is a variable that represents the root directory of your Django project.

`STATICFILES_DIRS`: Specifies additional directories where Django should look for static files. These directories are searched when you use the `{% load static %}` template tag or the `static()` function in your templates. It is a list of strings representing paths.

```
# settings.py

STATICFILES_DIRS = [
    BASE_DIR / "myapp/static",
    "/var/www/static/",
]
```
`STATIC_ROOT`: Specifies the directory where Django will collect static files from all installed apps using the `collectstatic` management command. This is typically used in production to serve static files efficiently using a dedicated web server (e.g., Nginx or Apache).

```
# settings.py

STATIC_ROOT = BASE_DIR / 'staticfiles'
```

Make sure to run `python manage.py collectstatic` to collect static files into the `STATIC_ROOT` directory.

In your HTML file, you can then reference the JavaScript file using the `{% static %}` template tag:

```
<script src="{% static 'yourscript.js' %}"></script>
```

When Django runs in development mode (using `python manage.py runserver`), it can serve static files for you. `STATIC_URL` is the base URL under which these static files are accessible. For example, if `STATIC_URL` is set to `'/static/'`, a file named `style.css` in your `static` directory would be accessible at `http://localhost:8000/static/style.css`.


* Load the static template tag:

At the top of your template file (before using `{% static %}`), make sure you include the `{% load static %}` template tag.

```html
{% load static %}
<!DOCTYPE html>
<html>
...
```

### Cross-Site Request Forgery (CSRF) protection

By default, Django requires a valid CSRF token for any `POST` requests to be processed. This is a security feature to protect against CSRF attacks.

* Include CSRF Token in Your POST Request:
Make sure that your POST request includes the CSRF token. In a Django template, you can use the `{% csrf_token %}` template tag to include the CSRF token in your form.


```html
<form method="post" action="{% url 'my_post_endpoint' %}">
    {% csrf_token %}
    <!-- Your form fields go here -->
    <input type="submit" value="Submit">
</form>
```
If you are not using Django forms, you can include the CSRF token manually in your AJAX request or form data.

* Use the `@csrf_exempt` Decorator (Not Recommended for Production):
As mentioned earlier, you can use the `@csrf_exempt` decorator on your view to disable CSRF protection. However, this should be used with caution, especially in a production environment, as it opens your application to CSRF attacks.

python
```
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def my_post_view(request):
    # Your view logic
```
If you choose this approach, make sure that your application has other security measures in place to protect against CSRF attacks.

* Check if Middleware Order is Correct:
Ensure that the 'django.middleware.csrf.CsrfViewMiddleware' middleware is included in your MIDDLEWARE setting and its order is correct. It should typically come before other middleware classes.

```python
MIDDLEWARE = [
    # ...
    'django.middleware.csrf.CsrfViewMiddleware',
    # ...
]
```

* AJAX Requests Include CSRF Token:
If you are making AJAX requests, make sure to include the CSRF token in the request headers. You can retrieve the token from a cookie named `csrftoken` and include it in the `X-CSRFToken` header.

```javascript
var csrftoken = getCookie('csrftoken');

// Include the token in your AJAX request
$.ajax({
    type: 'POST',
    url: '/my-post-endpoint/',
    data: {/* Your data here */},
    headers: {'X-CSRFToken': csrftoken},
    success: function(response) {
        // Handle success
    },
    error: function(error) {
        // Handle error
    }
});
```

### ASGI

ASGI stands for Asynchronous Server Gateway Interface. It's a specification for asynchronous web servers and frameworks in Python. ASGI enables handling multiple connections asynchronously, making it suitable for applications that require real-time features, such as chat applications, live notifications, or multiplayer games.

#### Install `channels`

python3 -m pip install Django channels
[Channels](https://channels.readthedocs.io/en/latest/index.html)


#### Configuration

The routing configuration in the `asgi.py` file defines how WebSocket connections are routed to consumers. Here's an example routing configuration:

```python
# asgi.py

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from pong.consumers import PongConsumer

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pong_project.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            [
                # Add your WebSocket consumers here
                # For example:
                # re_path(r"ws/some_path/$", SomeConsumer.as_asgi()),
                re_path(r"ws/pong/$", PongConsumer.as_asgi()),
            ]
        )
    ),
})
```

* The `ProtocolTypeRouter` is used to define different protocols, such as HTTP and WebSocket.
* The `URLRouter` is responsible for routing WebSocket connections based on URL patterns.
* The `re_path` function is used to define a regular expression pattern for WebSocket paths.
* The `PongConsumer` is the consumer class that will handle WebSocket connections for the "ws/pong/" path.

You can add more consumers and paths as needed for your application. Each consumer handles the WebSocket connection, and you can define custom logic for handling messages, connecting, disconnecting, etc., within the respective consumer class (`PongConsumer` in this example).

#### consumers.py

# consumers.py

```python
import json
from channels.generic.websocket import AsyncWebsocketConsumer

class PongConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f"pong_{self.room_name}"

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        # Handle user input (if needed)
        pass

    async def update_state(self, event):
        state = event['state']

        # Send the updated game state back to all clients in the room
        await self.send(text_data=json.dumps({
            'state': state,
        }))

    async def player_join(self, event):
        # Notify all clients when a new player joins the room
        player_count = event['player_count']
        await self.send(text_data=json.dumps({
            'player_count': player_count,
        }))
```

These methods are invoked when the corresponding event types are specified in the `group_send` method. The `type` field in the message dictionary determines which method should be called on the consumer.

```python
# Server-side code triggering events

# Update game state
await self.channel_layer.group_send(
    self.room_group_name,
    {
        'type': 'update_state',
        'state': updated_state_data,
    }
)

# Notify player join
await self.channel_layer.group_send(
    self.room_group_name,
    {
        'type': 'player_join',
        'player_count': updated_player_count,
    }
)
```

### Sessions

Maintaining client sessions with Django models involves using a combination of models, views, and middleware. Here's a step-by-step guide:

1. **Create a Session Model:** Define a model to represent user sessions. This model should have fields for the session ID, user ID, and an expiration timestamp.

```python
from django.db import models

class Session(models.Model):
    session_id = models.CharField(max_length=40, primary_key=True)
    user = models.ForeignKey('users.User', on_delete=models.CASCADE)
    expires = models.DateTimeField()
```

2. **Create a Session View:** Define a view that generates and stores session tokens for new users. This view should receive the user's identity and generate a cryptographically signed token. Then, it should create a new session object in the database and store the token and user ID.

```python
from django.shortcuts import render, redirect
from django.contrib.auth import login
from .models import Session

def create_session(request):
    # Generate a cryptographically signed session token
    token = generate_session_token()

    # Create a new Session object and store the token and user ID
    session = Session(session_id=token, user=request.user)
    session.save()

    # Set the session token in the response cookies
    response = redirect('home')
    response.set_cookie('session_id', token)

    return response
```

3. **Use SessionMiddleware:** Configure Django's session middleware to automatically load session data from the cookie and associate it with the current request context. This middleware will read the session ID from the 'session_id' cookie and look up the corresponding session object in the database. If the session is valid, it will be associated with the request context.

In your project's settings.py file, add the following middleware configuration:

```python
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    ...
]
```

4. **Verify Session Tokens:** In your views that require a valid session, verify the session token from the request context. This can be done by retrieving the session object from the database using the session ID and checking if the token matches the session's `session_id` field.

```python
def protected_view(request):
    # Retrieve the session object from the request context
    session = request.session

    # Verify the session token
    if session.get('session_id') != Session.objects.get(session_id=session.get('session_id')).session_id:
        # Session verification failed, redirect to login
        return redirect('login')

    # Access user data or perform protected actions
    user = session.get('user')
    ...
```

By following these steps, you can effectively maintain client sessions in Django applications using session tokens and Django models. This approach offers enhanced security, scalability, and portability compared to traditional session cookie methods.

#### Session Expires

There are two main ways to check if a session has expired in Django:

**1. Using the `get_expiry_age()` method**

The `get_expiry_age()` method returns the number of seconds until the current session will expire. If the session has already expired, the method will return `0`.

```python
from django.contrib.sessions.backends.base import SessionBase

def is_session_expired(session: SessionBase) -> bool:
    if session.get_expiry_age() <= 0:
        return True
    else:
        return False
```

**2. Using the `set_expiry()` method**

The `set_expiry()` method sets the expiration time for the current session. By default, sessions will expire after 31536000 seconds (one year).

```python
from django.contrib.sessions.backends.base import SessionBase

def check_session_expiry(session: SessionBase) -> bool:
    seconds_left = session.get_expiry_age()
    if seconds_left < 30:
        return False
    else:
        return True
```

Here's an example of how to use these methods to check if a session has expired:

```python
from django.shortcuts import render
from django.contrib.sessions.backends.base import SessionBase

def my_view(request):
    session = request.session

    if is_session_expired(session):
        # Session has expired, redirect to login
        return redirect('login')

    if check_session_expiry(session):
        # Session is about to expire, set a new expiry time
        session.set_expiry(31536000)

```

By checking the session expiration status, you can ensure that your application is not serving expired sessions to users. This helps to maintain the security and integrity of your application's data and interactions with users.

#### SessionMiddleware

Using SessionMiddleware is more secure and efficient than sending session data directly in POST requests. Here are the key reasons why:

**Security:** SessionMiddleware handles the storage and retrieval of session data in an encrypted and secure manner. This protects sensitive user information from being tampered with or stolen. When you send session data directly in POST requests, it is transmitted in plain text, making it vulnerable to interception and misuse.

**Scalability:** SessionMiddleware handles session management centrally, reducing the load on individual views. This is particularly important for applications with a high volume of requests, as it improves server performance and scalability. When you send session data directly in POST requests, each view needs to handle the session management, which can lead to performance bottlenecks.

**Portability:** SessionMiddleware uses a standardized format for storing session data, making it easy to integrate with different web frameworks and technologies. When you send session data directly in POST requests, you are tied to the specific format used by your application, which can limit portability.

**Ease of Use:** SessionMiddleware simplifies session management by abstracting away the underlying details. This makes it easier to develop and maintain applications that rely on sessions. When you send session data directly in POST requests, you need to handle all of the session management logic yourself, which can be more complex and error-prone.

In summary, while sending session data directly in POST requests may seem simpler, using SessionMiddleware offers a more secure, efficient, and portable solution for managing user sessions in Django applications. It abstracts away the complexities of session management, reduces the risk of security vulnerabilities, and improves the overall performance of your application.


#### Django load javascript
To ensure that Django serves the JavaScript file with the correct content type when using the `<script>` tag in your template, you can use the `HttpResponse` class and set the `Content-Type` header accordingly.

Here's an example of how you can do this in a Django view:

```python
from django.http import HttpResponse

def your_view(request):
    # Your view logic here

    # Assuming 'main.js' is in the 'static' directory
    js_file_path = 'static/main.js'

    with open(js_file_path, 'r') as file:
        js_content = file.read()

    response = HttpResponse(js_content, content_type='application/javascript')
    return response
```

In this example, we use the `HttpResponse` class and set the `content_type` parameter to 'application/javascript'. This ensures that the response is interpreted as JavaScript by the browser.

However, a more Django-like way to achieve this is to use the `render` shortcut along with a template. Create a template file (e.g., `main.js`) that contains your JavaScript code:

```javascript
// main.js
console.log('Hello from main.js');
// Your JavaScript code goes here
```

Then, in your view, use the `render` shortcut:

```python
from django.shortcuts import render

def your_view(request):
    # Your view logic here

    return render(request, 'main.js', content_type='application/javascript')
```

This way, you separate your JavaScript code into a template file, and Django will take care of setting the correct content type for you. Make sure to adjust the paths and names according to your project structure.

### Other stuffs

[Disable logging](https://stackoverflow.com/questions/5255657/how-can-i-disable-logging-while-running-unit-tests-in-python-django)

### Other stuffs

## Javascript (SPA)

[How to include a JavaScript file in another JavaScript file?](https://www.scaler.com/topics/javascript/import-js-file-in-js/)

### SPA (Single-page application)
#### URL history

Use the pushState method to add a new state to the browser's history stack without causing a navigation.

```javascript
// Change the URL without reloading the page
function changeURLWithoutReload(newPath) {
    window.history.pushState({}, '', newPath);
}

// Example usage
changeURLWithoutReload('/new-page');

// You might also want to handle the popstate event to handle back/forward navigation
window.onpopstate = function(event) {
    // Handle the back/forward button click here
    console.log('Back/Forward button clicked');
};
```

#### Router
In case client does not access main page at startup

```javascript
// Check the URL on page load
window.onload = function() {
    const currentPath = window.location.pathname;

    // Use a switch statement or if-else conditions to handle different routes
    switch (currentPath) {
        case '/page1':
            // Load content for Page 1
            break;
        case '/page2':
            // Load content for Page 2
            break;
        default:
            // Handle unknown routes or redirect to a default route
            window.location.href = '/default';
            break;
    }
};
```
