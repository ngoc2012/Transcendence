export class Signup
{
    constructor(m) {
        this.main = m;
    }

    events(isPopState) {
        if (!isPopState)
            window.history.pushState({page: '/signup'}, '', '/signup');

        this.dom_login = document.querySelector("#login1");
        this.dom_password = document.querySelector("#password1");
        this.dom_email = document.querySelector("#email1");
        this.dom_name = document.querySelector("#name1");
        this.dom_signup = document.querySelector("#signup1");
        this.dom_cancel = document.querySelector("#cancel1");
        this.dom_enable2fa = document.querySelector("#enable2fa");

        this.dom_signup.addEventListener("click", () => this.signup());
        this.dom_cancel.addEventListener("click", () => this.cancel());

        this.dom_login.addEventListener("keydown", (event) => this.handle_key_press(event));
        this.dom_password.addEventListener("keydown", (event) => this.handle_key_press(event));
        this.dom_email.addEventListener("keydown", (event) => this.handle_key_press(event));
        this.dom_name.addEventListener("keydown", (event) => this.handle_key_press(event));
    }

    signup() {
        if (this.dom_login.value === '' || this.dom_password.value === '' || this.dom_name.value === '' || this.dom_email.value === '') {
            this.main.set_status('Field must not be empty', false);
            return;
        }

        let checkbox = this.dom_enable2fa.checked;
        let csrftoken = this.main.getCookie('csrftoken');

        $.ajax({
            url: '/new_player/',
            method: 'POST',
            headers: {
                'X-CSRFToken': csrftoken,
            },
            data: {
                "login": this.dom_login.value,
                "password": this.dom_password.value,
                "name": this.dom_name.value,
                "email": this.dom_email.value,
                "enable2fa": checkbox ? 'true' : 'false'
            },
            success: (info) => {
                if (info.error) {
                    let errors = JSON.parse(info.error);
                    let firstErrorMessage = '';
                    for (let field in errors) {
                        if (errors[field].length > 0) {
                            firstErrorMessage = errors[field][0].message;
                            break;
                        }
                    }
                    this.main.set_status('Error: ' + firstErrorMessage, false);
                } else {
                    this.main.email = info.email;
                    this.main.login = info.login;
                    this.main.name = info.name;
                    this.main.dom_name.innerHTML = info.name;
                    this.main.lobby.ws = info.ws;
                    var dom_log_in = document.getElementById('login');
                    if (dom_log_in) {
                        dom_log_in.style.display = "none";
                    }

                    var dom_signup = document.getElementById('signup');
                    if (dom_signup) {
                        dom_signup.style.display = "none";
                        var dom_logout = document.getElementById('logoutButton');
                        if (dom_logout) {
                            // dom_logout.classList.remove("hidden");
                            dom_logout.style.display = 'inline-block'
                            // dom_logout.addEventListener('click', () => this.main.logout());
                        }
                        else
                        {
                            dom_signup.insertAdjacentHTML('afterend', '<button id="logoutButton" class="btn btn-danger">Log Out</button>');
                            var dom_logout = document.getElementById('logoutButton');
                            dom_logout.addEventListener('click', () => this.main.logout());
                        }
                    }
                    if (checkbox)
                        this.display2FASetup(info.secret);
                    else
                        this.main.load('/lobby', () => this.main.lobby.events());
                }
            },
            error: (jqXHR, textStatus, errorThrown) => {
                let response = JSON.parse(jqXHR.responseText);
                let message = 'Registration failed: ';
                if (response && response.error) {
                    let errors = JSON.parse(response.error);
                    for (let field in errors) {
                        if (errors[field].length > 0) {
                            message += errors[field][0].message;
                            break;
                        }
                    }
                } else {
                    message += textStatus;
                }
                this.main.set_status(message, false);
            }
        });
    }

    display2FASetup(secret) {
        let csrftoken = this.main.getCookie('csrftoken');

        if (csrftoken) {
            $.ajax({
                url: '/display_2fa/',
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrftoken,
                },
                data: {
                    "email": this.main.email,
                    "secret": secret
                },
                success: (html) => {
                    this.main.dom_container.innerHTML = html;
                    if (this.main.display_2fa && typeof this.main.display_2fa.events === 'function') {
                        this.main.display_2fa.events();
                    }
                },
                error: function(errorThrown) {
                    this.main.set_status('Error setting up 2FA: ' + errorThrown, false);
                }
            });
        } else {
            this.main.load('/pages/login', () => this.main.log_in.events());
        }
    }

    handle_key_press(event)
    {
        if (event.keyCode === 13)
            this.signup();
    }

    cancel() {
        this.main.load('/lobby', () => this.main.lobby.events());
    }
}
