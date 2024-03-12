

// Give the user the different way of login in our app (normal or through 42), 
// then in case of a normal connection start the 2fa verification process


export class Login
{
    constructor(m) {
        this.main = m;
		this.blocked_users = [];
    }
    
    events() {
        this.main.set_status('');
        this.dom_login = document.querySelector("#login0");
        this.dom_password = document.querySelector("#password0");
        this.dom_log_in = document.querySelector("#log_in");
        this.dom_cancel = document.querySelector("#cancel0");
        this.dom_log_in42 = document.querySelector("#log_in42");

        this.dom_log_in.addEventListener("click", () => this.login());
        this.dom_cancel.addEventListener("click", () => this.cancel());
        this.dom_log_in42.addEventListener("click", () => this.loginWith42());

    }

    login() {
        if (this.dom_login.value === '' || this.dom_password.value === '')
        {
            this.main.set_status('Field must not be empty');
            return;
        }
        $.ajax({
            url: '/log_in/',
            method: 'POST',
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
                    sessionStorage.setItem('JWTToken', info.access_token);
                    document.cookie = `refresh_token=${info.refresh_token}; path=/; secure; HttpOnly`;
                    this.main.email = info.email;
                    this.main.login = info.login;
                    this.main.name = info.name;
                    this.main.dom_name.innerHTML = info.name;
                    if (info.enable2fa == 'true')
                        this.main.load('/twofa', () => this.main.twofa.events());
                    else
                        this.main.load('/lobby', () => this.main.lobby.events());
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
        $.ajax({
            url: '/transchat/chat_lobby/',
            method: 'POST',
            data: {
                'username': this.dom_login.value
            }
        })
    }

    loginWith42() {
        window.location.href = 'https://api.intra.42.fr/oauth/authorize?client_id=u-s4t2ud-bda043967d92d434d1d6c24cf1d236ce0c6cc9c718a9198973efd9c5236038ed&redirect_uri=https%3A%2F%2F127.0.0.1%3A8080%2Fcallback%2F&response_type=code';
    }

    cancel() {
        this.main.set_status('');
        this.main.load('/lobby', () => this.main.lobby.events());
    }
}
