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

    generateState() {
        const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
        let state = '';
        for (let i = 0; i < 32; i++) {
            state += chars.charAt(Math.floor(Math.random() * chars.length));
        }
        return state;
    }
    
    loginWithgoogle() {
        const clientId = '653042883299-77c3tjibru5mimotm5rin6q49ej0vo00.apps.googleusercontent.com';
        const redirectUri = encodeURIComponent('https://127.0.0.1/google/callback');
        const scopes = encodeURIComponent('openid email');
        const state = this.generateState();
        console.log('GOOGLE')
        
        const authorizationUrl = `https://accounts.google.com/o/oauth2/auth?response_type=code&client_id=${clientId}&redirect_uri=${redirectUri}&scope=${scopes}&state=${state}&access_type=offline&include_granted_scopes=true&prompt=select_account`;
        console.log(authorizationUrl)

        window.location.href = authorizationUrl;
    }
    

    cancel() {
        this.main.set_status('');
        this.main.load('/lobby', () => this.main.lobby.events());
    }
}
