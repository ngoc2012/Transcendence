

// After signup of a new user, this js and the linked html display what's needed the future login to go through the 2fa

export class display_2fa {
    constructor(m) {
        this.main = m;
    }

    events() {
        this.main.checkcsrf();
        this.main.set_status('');
        this.dom_proceed = document.querySelector("#proceed");
        this.dom_proceed.addEventListener("click", () => this.proceed());
        this.generateQRCode();
    }

    proceed() {
        window.history.pushState({}, '', '/');
        this.main.load('/lobby', () => this.main.lobby.events());
        this.main.lobby.socket.send(JSON.stringify({ type: "authenticate", login: this.main.login }));
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

