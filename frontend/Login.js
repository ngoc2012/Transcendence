export class Login
{
    constructor(m) {
        this.main = m;
    }
    
    events() {
        this.dom_login = document.querySelector("#login");
        this.dom_password = document.querySelector("#password");
        this.dom_log_in = document.querySelector("#log_in");
        this.dom_cancel = document.querySelector("#cancel");
    }

    signup() {
        $.ajax({
            url: '/login',
            method: 'POST',
            data: {
                "login": this.dom_login.value,
                "password": this.dom_password.value
            },
            success: (info) => {
                this.main.login = info.login;
                this.main.name = info.name;
            },
            error: (data) => this.main.set_status(data.error)
        });
    }

    cancel() {
        this.main.load('/lobby', () => this.main.lobby.events());
    }
}
