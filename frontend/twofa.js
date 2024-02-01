export class twofa
{
    constructor(m) {
        this.main = m;
    }
    
    events() {
        this.main.set_status('');

        this.dom_log_in_sms = document.querySelector("#log_in_with_sms");
        this.dom_cancel = document.querySelector("#cancel0");
        this.dom_log_in_google = document.querySelector("#log_in_with_google");

        this.dom_log_in_sms.addEventListener("click", () => this.loginwithsms());
        this.dom_cancel.addEventListener("click", () => this.cancel());
        this.dom_log_in_google.addEventListener("click", () => this.loginWithgoogle());

    }

    // Fonction pour générer et afficher le QR code
    // le faire s'integrer a l'html
    // import QRCode from 'qrcode-generator';

    generateQRCode(otpauthUrl) {

        var qrCodeContainer = document.createElement('div');
        qrCodeContainer.id = 'qr-code-container';
    
        document.body.appendChild(qrCodeContainer);
    
        var qrCode = QRCode(0, 'M');
        qrCode.addData(otpauthUrl);
        qrCode.make();
    
        var img = qrCode.createImgTag(5);
    
        qrCodeContainer.innerHTML = img;
    }

    loginwithsms() {
        console.log(this.main.login);
        console.log(this.main.name);
        $.ajax({
            url: '/enable_2fa/',
            method: 'GET',
            data: {
                "login": this.main.login,
                "name": this.main.name,
            },
            success: function(response) {
                console.log('Success:', response);
    
                // Générer et afficher le QR code
                // this.generateQRCode(response.otpauth_url);
                
                // Rediriger vers enable_2fa.html avec otpauth_url comme paramètre
                // window.location.href = 'enable_2fa.html?otpauth_url=' + response.otpauth_url;
    
            }.bind(this),
            error: function(xhr, status, error) {
                console.error('Error:', error);
            }
        });
    }

    loginWithgoogle() {
        console.log('PASSE ICI')
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
