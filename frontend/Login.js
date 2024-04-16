// // Give the user the different way of login in our app (normal or through 42),
// // then in case of a normal connection start the 2fa verification process

export class Login
{
    constructor(m) {
        this.main = m;
		this.blocked_users = [];
    }

    events() {
        this.main.checkcsrf();
        this.main.set_status('');
        this.dom_login = document.querySelector("#login0");
        this.dom_password = document.querySelector("#password0");
        this.dom_log_in = document.querySelector("#log_in");
        this.dom_cancel = document.querySelector("#cancel0");
        this.dom_log_in42 = document.querySelector("#log_in42");

        this.dom_log_in.addEventListener("click", () => this.login());
        this.dom_cancel.addEventListener("click", () => this.cancel());
        this.dom_log_in42.addEventListener("click", () => this.loginWith42());

        this.dom_login.addEventListener("keydown", (event) => this.handle_key_press(event));
        this.dom_password.addEventListener("keydown", (event) => this.handle_key_press(event));
    }

    login() {
        if (this.dom_login.value === '' || this.dom_password.value === '')
        {
            this.main.set_status('Field must not be empty');
            return;
        }

        var csrftoken = this.main.getCookie('csrftoken');

        $.ajax({
            url: 'log_in/',
            method: 'POST',
            headers: {
                'X-CSRFToken': csrftoken,
            },   
            data: {
                "login": this.dom_login.value,
                "password": this.dom_password.value,
            },
            success: (info) => {
                if (typeof info === 'string')
                {
                    this.main.set_status(info);
                }
                else
                {
                    this.main.email = info.email;
                    this.main.login = info.login;
                    this.main.name = info.name;
                    this.main.dom_name.innerHTML = info.name;
                    this.main.lobby.ws = info.ws;
                    if (info.enable2fa == 'true')
                        this.main.load('/twofa', () => this.main.twofa.events());
                    else
                    {
                        var dom_log_in = document.getElementById('login');
                        if (dom_log_in) {
                            dom_log_in.style.display = "none";
                        }
    
                        var dom_signup = document.getElementById('signup');
                        if (dom_signup) {
                            dom_signup.style.display = "none";
                            dom_signup.insertAdjacentHTML('afterend', '<button id="logoutButton" class="btn btn-danger">Logout</button>');
                        }
    
                        var dom_logout = document.getElementById('logoutButton');
                        if (dom_logout) {
                            dom_logout.addEventListener('click', () => this.main.logout());
                        }
                        
                        this.main.history_stack.push('/');
                        window.history.pushState({}, '', '/');
                        this.main.load('/lobby', () => this.main.lobby.events());
                    }
                }
            },
            error: (xhr, textStatus, errorThrown) => {
                if (xhr.responseJSON && xhr.responseJSON.error) {
                    this.main.set_status(xhr.responseJSON.error);
                } else {
                    this.main.set_status('An error occurred during the request.');
                }
            }
        });
    }

    handle_key_press(event)
    {
        if (event.keyCode === 13)
            this.login();
    }

    loginWith42() {
        window.location.href = 'https://api.intra.42.fr/oauth/authorize?client_id=u-s4t2ud-bda043967d92d434d1d6c24cf1d236ce0c6cc9c718a9198973efd9c5236038ed&redirect_uri=https%3A%2F%2F127.0.0.1%3A8080%2Fcallback%2F&response_type=code';
    }

    cancel() {
        this.main.set_status('');
        window.history.pushState({}, '', '/');
        this.main.load('/lobby', () => this.main.lobby.events());
    }
}
