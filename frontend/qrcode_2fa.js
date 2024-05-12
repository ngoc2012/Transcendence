

// Take and verify the 2fa code from authenticator then conect the user if the code is right

export class qrcode_2fa
{
    constructor(m) {
        this.main = m;
    }

    events(login) {
        this.main.checkcsrf();

        this.dom_code = document.querySelector("#code");
        this.dom_confirm = document.querySelector("#confirm");
        this.dom_cancel = document.querySelector("#cancel0");
        this.dom_confirm.addEventListener("click", () => this.confirm(login));
        this.dom_cancel.addEventListener("click", () => this.cancel());
        // this.dom_code.addEventListener("keypress", (e) => {
        //     // if (e.key === "Enter") {
        //     //     e.preventDefault();
        //     //     this.confirm();
        //     // }
        // });
    }

    eventsTour(login) {
        this.tournament = true;
        this.login = login;
        this.events();
    }

    confirm(login) {
        if (this.dom_code.value === '') {
            this.main.set_status('Field must not be empty', false);
            return;
        }
        const csrftoken = this.main.getCookie('csrftoken');
        // console.log(csrftoken)
        if (csrftoken) {
            $.ajax({
                url: '/verify_qrcode/',
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrftoken,
                },
                data: {
                    "input_code": this.dom_code.value,
                    'login': this.tournament ? this.login : login,
                },
                success: (info) => {
                    if (typeof info === 'string') {
                        this.main.set_status(info, true);
                        this.main.login.state = 2;
                    } else if (info.result === '1') {
                        if (this.tournament) {
                            this.main.load('/tournament/local', () => this.main.lobby.tournament.eventsTwoFA(this.login));
                            return;
                        } else {
                            $.ajax({
                                url: '/log_in/',
                                method: 'POST',
                                headers: {
                                    'X-CSRFToken': csrftoken,
                                },
                                data: {
                                    "login": this.main.log_in.dom_login.value,
                                    "password": this.main.log_in.dom_password.value,
                                },
                                success: (info) => {
                                    if (typeof info === 'string') {
                                        this.main.set_status(info, true);
                                    } else {
                                        this.main.email = info.email;
                                        this.main.login = info.login;
                                        this.main.name = info.name;
                                        this.main.dom_name.innerHTML = info.name;
                                        this.main.lobby.ws = info.ws;

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

                                        this.main.load('/lobby', () => this.main.lobby.events());
                                    }
                                },
                                error: (xhr, textStatus, errorThrown) => {
                                    if (xhr.responseJSON && xhr.responseJSON.error) {
                                        this.main.set_status(xhr.responseJSON.error, false);
                                    } else {
                                        this.main.set_status('An error occurred during the request.', false);
                                    }
                                }
                            });
                        }
                    } else {
                        this.main.set_status('Wrong code, please try again', false);
                    }
                },
                error: (xhr) => {
                    this.main.set_status(xhr.responseJSON && xhr.responseJSON.error ? xhr.responseJSON.error : 'An error occurred during the request.', false);
                }
            });
        }
    }


    cancel() {
        this.main.load('/lobby', () => this.main.lobby.events());
    }
}
