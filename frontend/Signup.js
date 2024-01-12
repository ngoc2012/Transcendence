export class Signup
{
    constructor(m) {
        this.main = m;
    }
    
    events() {
        this.dom_login = document.querySelector("#login");
        this.dom_password = document.querySelector("#password");
        this.dom_name = document.querySelector("#name");
        this.dom_signup = document.querySelector("#signup");
        this.dom_cancel = document.querySelector("#cancel");
        this.dom_signup.addEventListener("click", () => this.signup());
        this.dom_cancel.addEventListener("click", () => this.cancel());
    }

    signup() {
        $.ajax({
            url: '/new_player',
            method: 'POST',
            data: {
                "login": this.dom_login.value,
                "password": this.dom_password.value,
                "name": this.dom_name.value
            },
            success: (info) => {
                this.main.login = info.login;
                this.main.name = info.name;
            },
            error: (data) => this.main.set_status(data.error)
        });
    }

    cancel() {
        main.load('/lobby', () => main.lobby.events());
    }
}
