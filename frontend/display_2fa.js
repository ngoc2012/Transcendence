// import QRCode from '/app/frontend/qrcode.min.js';

export class display_2fa {
    constructor(m) {
        this.main = m;
    }

    events() {
        this.main.set_status('');
        this.dom_proceed = document.querySelector("#proceed");
        this.dom_proceed.addEventListener("click", () => this.proceed());

        this.generateQRCode();
    }

    proceed() {
        this.main.load('/lobby', () => this.main.lobby.events());
    }

    generateQRCode() {
        const secret = "https://www.google.com/"; // À remplacer ensuite par le code du 2FA
        const qrCodeElement = document.querySelector("#qrcode");
        new QRCode(qrCodeElement, secret);
    }
}
