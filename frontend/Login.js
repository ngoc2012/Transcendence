export class Login
{
    constructor(m) {
        this.main = m;
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
                    this.main.login = info.login;
                    this.main.name = info.name;
                    this.main.dom_name.innerHTML = info.name;
                    this.main.load('/lobby', () => this.main.lobby.events());
                }
            },
            error: (data) => this.main.set_status(data.error)
        });
    }

    loginWith42() {
        // console.log("coucou1");
        window.location.href = 'https://api.intra.42.fr/oauth/authorize?client_id=u-s4t2ud-bda043967d92d434d1d6c24cf1d236ce0c6cc9c718a9198973efd9c5236038ed&redirect_uri=http%3A%2F%2F0.0.0.0%3A8000%2Fcallback%2F&response_type=code';
        // console.log("coucou2");
    }

    cancel() {
        this.main.set_status('');
        this.main.load('/lobby', () => this.main.lobby.events());
    }
}
