

// Start the differents 2fa processes for login

export class twofa
{
    constructor(m) {
        this.main = m;
    }
    
    events() {
        this.main.set_status('');

        this.dom_log_in_qrcode = document.querySelector("#log_in_with_qrcode");
        this.dom_cancel = document.querySelector("#cancel0");
        this.dom_log_in_google = document.querySelector("#log_in_with_google");
        this.dom_log_in_email = document.querySelector("#log_in_with_email");

        this.dom_log_in_qrcode.addEventListener("click", () => this.loginwithqrcode());
        this.dom_cancel.addEventListener("click", () => this.cancel());
        this.dom_log_in_google.addEventListener("click", () => this.loginWithgoogle());
        this.dom_log_in_email.addEventListener("click", () => this.loginWithemail());

    }

    loginWithemail() {
        $.ajax({
            url: '/mail_2fa/',
            method: 'GET',
            data: {
                "login": this.main.login,
                "name": this.main.name,
                "email": this.main.email
            },
            success: (response) => {
                this.main.load('/code_2fa', () => this.main.code_2fa.events());
            },
            error: (xhr, status, error) => {
                console.error('Error:', error);
            }
        });
    }


    loginwithqrcode() {
        this.main.load('/qrcode_2fa', () => this.main.qrcode_2fa.events());
    }


    loginWithgoogle() {
        $.ajax({
            url: '/google_auth/',
            method: 'GET',
            data: {
                "login": this.main.login,
                "name": this.main.name,
            },
            success: function(response) {
                window.location.href = response.authorization_url;
            },
            error: function(xhr, status, error) {
                console.error('Error:', error);
            }
        });
    }

    cancel() {
        this.main.set_status('');
        this.main.load('/lobby', () => this.main.lobby.events());
    }
}
