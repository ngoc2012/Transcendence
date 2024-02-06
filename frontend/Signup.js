export class Signup
{
    constructor(m) {
        this.main = m;
    }
    
    events() {
        this.main.set_status('');
        this.dom_login = document.querySelector("#login1");
        this.dom_password = document.querySelector("#password1");
        this.dom_email = document.querySelector("#email1");
        this.dom_name = document.querySelector("#name1");
        this.dom_signup = document.querySelector("#signup1");
        this.dom_cancel = document.querySelector("#cancel1");
        this.dom_signup.addEventListener("click", () => this.signup());
        this.dom_cancel.addEventListener("click", () => this.cancel());
    }

    signup() {
        if (this.dom_login.value === '' || this.dom_password.value === '' || this.dom_name.value === '' || this.dom_email.value === '')
        {
            this.main.set_status('Field must not be empty');
            return;
        }
        console.log("Sending AJAX request with data:", {
            "login": this.dom_login.value,
            "password": this.dom_password.value,
            "name": this.dom_name.value,
            "email": this.dom_email.value
        });
        
        $.ajax({
            url: '/new_player/',
            method: 'POST',
            data: {
                "login": this.dom_login.value,
                "password": this.dom_password.value,
                "name": this.dom_name.value,
                "email": this.dom_email.value
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
                    $.ajax({
                        url: '/display_2fa/',
                        method: 'POST',
                        data: {
                            "email": this.main.email,
                            "secret": info.secret
                        },
                        success: (html) => {
                                this.main.dom_container.innerHTML = html;
                                this.main.display_2fa.events();
                        },
                        error: function(error) {
                            console.error('Error: pong POST fail', error.message);
                        }
                    });
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
