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
