

// Start the differents 2fa processes for login

export class twofa
{
    constructor(m) {
        this.main = m;
    }
    
    events(isPopState) {
        this.main.checkcsrf();
        if (!isPopState)
            window.history.pushState({page: '/twofa'}, '', '/twofa');

        this.dom_log_in_qrcode = document.querySelector("#log_in_with_qrcode");
        this.dom_cancel = document.querySelector("#cancel0");
        this.dom_log_in_email = document.querySelector("#log_in_with_email");

        this.dom_log_in_qrcode.addEventListener("click", () => this.loginwithqrcode());
        this.dom_cancel.addEventListener("click", () => this.cancel());
        this.dom_log_in_email.addEventListener("click", () => this.loginWithemail());
    }

    eventsTour(id, login, name, email) {
        this.tournament = true;
        this.id = id;
        this.tourLogin = login;
        this.tourName = name;
        this.tourEmail = email;
        this.events()
    }

    loginWithemail() {
        var csrftoken = this.main.getCookie('csrftoken');
        let data;

        if (!this.tournament) {
            data = {
                "login": this.main.login,
                "name": this.main.name,
                "email": this.main.email
            }
        } else {
            data = {
                "login": this.tourLogin,
                "name": this.tourName,
                "email": this.tourEmail
            }
        }

        $.ajax({
            url: '/mail_2fa/',
            method: 'GET',
            headers: {
                'X-CSRFToken': csrftoken,
            },
            data: data,
            success: (response) => {
                if (!this.tournament) {
                    this.main.load('/code_2fa', () => this.main.code_2fa.events());
                } else {
                    this.main.load('/code_2fa', () => this.main.code_2fa.eventsTour(this.tourLogin));
                }
            },
            error: (xhr, status, error) => {
                // console.error('Error:', error);
            }
        });
    }


    loginwithqrcode() {
        if (!this.tournament) {
            this.main.load('/qrcode_2fa', () => this.main.qrcode_2fa.events());
        } else {
            this.main.load('/qrcode_2fa', () => this.main.qrcode_2fa.eventsTour(this.tourLogin));
        }
    }

    cancel() {
        if (this.tournament) {
            this.main.lobby.socket.send(JSON.stringify({
                type: 'tournament-quit',
                tour_id: this.id,
            }));
        }
        
        // this.main.history_stack.push('/');
        // window.history.pushState({}, '', '/');
        this.main.load('/lobby', () => this.main.lobby.events(false));
    }
}
