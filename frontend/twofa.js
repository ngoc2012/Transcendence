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

    loginwithsms() {
        console.log('salut')
        this.main.load('/lobby', () => this.main.lobby.events());
    }

    // generateState() {
    //     const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    //     let state = '';
    //     for (let i = 0; i < 32; i++) {
    //         state += chars.charAt(Math.floor(Math.random() * chars.length));
    //     }
    //     return state;
    // }
    
    loginWithgoogle() {
        console.log('PASSE ICI')
        $.ajax({
            url: '/google_auth/',  // URL de votre vue Django
            method: 'GET',  // Méthode HTTP utilisée (GET dans ce cas)
            data: {
                "login": this.main.login,
                "name": this.main.name,
            },
            success: function(response) {
                // Réponse réussie de la vue Django
                console.log('Success:', response);
                // Redirection de l'utilisateur vers l'URL d'autorisation OAuth2
                window.location.href = response.authorization_url;
            },
            error: function(xhr, status, error) {
                // En cas d'erreur lors de la requête AJAX
                console.error('Error:', error);
            }
        });
    }


    cancel() {
        this.main.set_status('');
        this.main.load('/lobby', () => this.main.lobby.events());
    }
}
