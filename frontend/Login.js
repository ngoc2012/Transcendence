// // Give the user the different way of login in our app (normal or through 42),
// // then in case of a normal connection start the 2fa verification process

export class Login
{
    constructor(m) {
        this.main = m;
        this.state = 0;
    }

    events(isPopState) {
        this.main.checkcsrf();
        if (!isPopState)
            window.history.pushState({page: '/login'}, '', '/login');

        this.dom_login = document.getElementById("login0");
        this.dom_password = document.getElementById("password0");
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
            this.main.set_status('Field must not be empty', false);
            return;
        }

        var csrftoken = this.main.getCookie('csrftoken');
        $.ajax({
            url: 'auth_view/',
            method: 'POST',
            headers: {
                'X-CSRFToken': csrftoken,
            },
            data: {
                "login": this.dom_login.value,
                "password": this.dom_password.value,
            },
            success: (info) => {

                if (info.enable2fa == 'true')
                {
                    this.main.load('/twofa', () => this.main.twofa.events(info.email, info.login, info.name ));
                }
                else
                {
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
                                this.main.set_status(info, true);
                            }
                            else
                            {
                                this.main.email = info.email;
                                this.main.login = info.login;
                                this.main.name = info.name;
                                this.main.dom_name.innerHTML = info.name;
                                this.main.lobby.ws = info.ws;
                                this.main.picture = info.avatar;
                                var dom_log_in = document.getElementById('login');
                                if (dom_log_in) {
                                    dom_log_in.style.display = "none";
                                }

                                var dom_signup = document.getElementById('signup');
                                if (dom_signup) {
                                    dom_signup.style.display = "none";
                                    dom_signup.insertAdjacentHTML('afterend', '<button id="logoutButton" class="btn btn-danger">Log Out</button>');
                                    var dom_logout = document.getElementById('logoutButton');
                                    if (dom_logout) {
                                        dom_logout.addEventListener('click', () => this.main.logout());
                                    }
                                }


                                var dom_picture = document.getElementById('picture');
                                if (dom_picture){
                                    dom_picture.src = this.main.picture.replace('/app/frontend/', '/static/');
                                }
                                var dom_chatarea = document.getElementById('chat_area');
                                if (dom_chatarea){
                                    dom_chatarea.innerHTML = '';
                                    this.main.make_chat(dom_chatarea);
                                }
                                this.main.load('/lobby', () => this.main.lobby.events(false));
                            }
                        },
                        error: (xhr) => {
                            if (xhr.responseJSON && xhr.responseJSON.error) {
                                this.main.set_status(xhr.responseJSON.error, false);
                            } else {
                                this.main.set_status('An error occurred during the request.', false);
                            }
                        }
                    });
                }
            },
            error: (xhr, textStatus, errorThrown) => {
                if (xhr.responseJSON && xhr.responseJSON.error) {
                    this.main.set_status(xhr.responseJSON.error, false);
                    // console.log( "erreur = ", xhr.responseJSON.error)
                } else {
                    this.main.set_status('An error occurred during the request.', false);
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
        var csrftoken = this.main.getCookie('csrftoken');

        if (csrftoken) {
            $.ajax({
                url: '/login42/',
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrftoken,
                },
                success: (response) => {
                    window.location.href = response.url;
                },
                error: () => {
                    this.main.set_status('Error', false);
                }
            })
        } else {
            this.main.load('/pages/login', () => this.main.log_in.events(false));
        }
    }

    cancel() {
        this.main.load('/lobby', () => this.main.lobby.events(false));
    }
}
