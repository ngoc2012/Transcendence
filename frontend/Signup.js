export class Signup
{
    constructor(m) {
        this.main = m;
    }
    
    events() {
        this.main.set_status('');
        this.dom_login = document.querySelector("#login1");
        this.dom_password = document.querySelector("#password1");
        this.dom_name = document.querySelector("#name1");
        this.dom_signup = document.querySelector("#signup1");
        this.dom_cancel = document.querySelector("#cancel1");
        this.dom_signup.addEventListener("click", () => this.signup());
        this.dom_cancel.addEventListener("click", () => this.cancel());
    }

    signup() {
        if (this.dom_login.value === '' || this.dom_password.value === '' || this.dom_name.value === '')
        {
            this.main.set_status('Field must not be empty');
            return;
        }
        $.ajax({
            url: '/new_player/',
            method: 'POST',
            data: {
                "login": this.dom_login.value,
                "password": this.dom_password.value,
                "name": this.dom_name.value
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
