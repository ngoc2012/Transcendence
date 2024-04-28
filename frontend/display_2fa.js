

// After signup of a new user, this js and the linked html display what's needed the future login to go through the 2fa

export class display_2fa {
    constructor(m) {
        this.main = m;
    }

    events() {
        this.main.checkcsrf();
        
        this.dom_proceed = document.querySelector("#proceed");
        this.dom_proceed.addEventListener("click", () => this.proceed());
        this.generateQRCode();
    }

    proceed() {
        window.history.pushState({}, '', '/');
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
        this.main.history_stack.push('/');
        window.history.pushState({}, '', '/');
        this.main.load('/lobby', () => this.main.lobby.events());
    }

    generateQRCode() {
        const secretKeyElement = document.getElementById("secretKey");
        const secretKey = secretKeyElement.dataset.secret;
        const login = this.main.login;
        const secret = `otpauth://totp/${login}?secret=${secretKey}&issuer=Transcendence`;
        const qrCodeElement = document.querySelector("#qrcode");
        new QRCode(qrCodeElement, secret);
    }
}

