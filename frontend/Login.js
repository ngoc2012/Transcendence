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
        this.dom_log_in.addEventListener("click", () => this.login());
        this.dom_cancel.addEventListener("click", () => this.cancel());
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

    cancel() {
        this.main.set_status('');
        this.main.load('/lobby', () => this.main.lobby.events());
    }
}
