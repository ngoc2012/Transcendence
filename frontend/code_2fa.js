

// Take and verify the 2fa code from email then conect the user if the code is right


export class code_2fa
{
    constructor(m) {
        this.main = m;
    }
    
    events() {
        this.main.checkcsrf();
        this.main.set_status('');

        this.dom_code = document.querySelector("#code0");
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
                        var dom_log_in = document.getElementById('login');
                        if (dom_log_in) {
                            dom_log_in.style.display = "none";
                        }
    
                        var dom_signup = document.getElementById('signup');
                        if (dom_signup) {
                            dom_signup.style.display = "none";
                            dom_signup.insertAdjacentHTML('afterend', '<button id="logoutButton" class="btn btn-danger">Logout</button>');
                        }
    
                        var dom_logout = document.getElementById('logoutButton');
                        if (dom_logout) {
                            dom_logout.addEventListener('click', () => this.main.logout());
                        }
                        if (!this.tournament) {
                            this.main.load('/lobby', () => this.main.lobby.events());
                        } else {
                            this.main.load('/tournament/local', () => this.main.lobby.tournament.eventsTwoFA(this.login));
                        }
                    } else {
                        this.main.set_status('Wrong code, please try again');
                    }
                },
                error: (data) => this.main.set_status(data.error)
            });
        }
    }

    cancel() {
        this.main.set_status('');
        this.main.load('/lobby', () => this.main.lobby.events());
    }
}
