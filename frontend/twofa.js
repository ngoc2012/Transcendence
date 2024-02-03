
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
        this.dom_log_in_email = document.querySelector("#log_in_with_email");

        this.dom_log_in_sms.addEventListener("click", () => this.loginwithsms());
        this.dom_cancel.addEventListener("click", () => this.cancel());
        this.dom_log_in_google.addEventListener("click", () => this.loginWithgoogle());
        this.dom_log_in_email.addEventListener("click", () => this.loginWithemail());

    }

    loginWithemail() {
        console.log('email from js before avax : ', this.main.email)
        $.ajax({
            url: '/mail_2fa/',
            method: 'GET',
            data: {
                "login": this.main.login,
                "name": this.main.name,
                "email": this.main.email
            },
            success: function(response) {
                console.log('MON CODE :',response.code)
            },
            error: function(xhr, status, error) {
                console.error('Error:', error);
            }
        });
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
                this.main.load('/qrcode_2fa');
                // this.generateQRCode(response.otpauth_url);                
                // Rediriger vers enable_2fa.html avec otpauth_url comme paramètre
                
                //window.location.href = 'https://qrcode_2fa';
    
            }.bind(this),
            error: function(xhr, status, error) {
                console.error('Error:', error);
            }
        });
    }

    loginWithgoogle() {
        // console.log('PASSE ICI')
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
