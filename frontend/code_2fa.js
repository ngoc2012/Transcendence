

// Take and verify the 2fa code from email then conect the user if the code is right

export class code_2fa
{
    constructor(m) {
        this.main = m;
    }
    
    events() {
        this.main.checkcsrf();
        this.dom_code = document.querySelector("#code");
        this.dom_confirm = document.querySelector("#confirm");
        this.dom_cancel = document.querySelector("#cancel0");
        document.getElementById("email_address").innerText = this.main.email;
        this.dom_confirm.addEventListener("click", () => this.confirm());
        this.dom_cancel.addEventListener("click", () => this.cancel());
    }

    eventsTour(login) {
        this.tournament = true;
        this.login = login;
        this.events();
    }

    confirm() {
        if (this.dom_code.value === '')
        {
            this.main.set_status('Field must not be empty');
            return;
        }
        
        var csrftoken = this.main.getCookie('csrftoken');

        if (this.tournament)
            return this.confirm_tour(csrftoken);

        if (csrftoken) {
            $.ajax({
                url: '/verify/',
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrftoken,
                },
                data: {
                    "input_code": this.dom_code.value,
                },
                success: (info) => {
                    if (typeof info === 'string') {
                        this.main.set_status(info);
                    } else if (info.result === '1') {      
                        $.ajax({
                            url: 'log_in/',
                            method: 'POST',
                            headers: {
                                'X-CSRFToken': csrftoken,
                            },
                            data: {
                                "login": this.main.log_in.dom_login.value,
                                "password": this.main.log_in.dom_password.value,
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
                                    this.main.lobby.ws = info.ws;
                                    var dom_log_in = document.getElementById('login');
                                    if (dom_log_in) {
                                        dom_log_in.style.display = "none";
                                    }
                
                                    var dom_signup = document.getElementById('signup');
                                    if (dom_signup) {
                                        dom_signup.style.display = "none";
                                        dom_signup.insertAdjacentHTML('afterend', '<button id="logoutButton" class="btn btn-danger">Log Out</button>');
                                    }
                
                                    var dom_logout = document.getElementById('logoutButton');
                                    if (dom_logout) {
                                        dom_logout.addEventListener('click', () => this.main.logout());
                                    }
                                    if (!this.tournament) {
                                        this.main.history_stack.push('/');
                                        window.history.pushState({}, '', '/');
                                        this.main.load('/lobby', () => this.main.lobby.events());
                                    } else {
                                        this.main.history_stack.push('/tournament/local');
                                        window.history.pushState({}, '', '/tournament/local');
                                        this.main.load('/tournament/local', () => this.main.lobby.tournament.eventsTwoFA(this.login));
                                    }
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
                                'username': this.main.log_in.dom_login.value
                            }
                        })
                    } else {
                        this.main.set_status('Wrong code, please try again');
                    }
                },
                error: (data) => this.main.set_status(data.error)
            });
        }
    }

    confirm_tour(csrftoken) {
        if (csrftoken) {
            $.ajax({
                url: '/verify/',
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrftoken,
                },
                data: {
                    "input_code": this.dom_code.value,
                },
                success: (info) => {
                    if (typeof info === 'string') {
                        this.main.set_status(info);
                    } else if (info.result === '1') {     
                        this.main.history_stack.push('/tournament/local');
                        window.history.pushState({}, '', '/tournament/local');
                        this.main.load('/tournament/local', () => this.main.lobby.tournament.eventsTwoFA(this.login));
                    } else {
                        this.main.set_status('Wrong code, please try again');
                    }
                },
                error: (data) => this.main.set_status(data.error)
            });
        }
    }

    cancel() {
        this.main.history_stack.push('/');
        window.history.pushState({}, '', '/');
        this.main.load('/lobby', () => this.main.lobby.events());
    }
}
