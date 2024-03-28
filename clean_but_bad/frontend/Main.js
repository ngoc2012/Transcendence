import {Lobby} from './Lobby.js'
import {Signup} from './Signup.js'
import {Login} from './Login.js'
import {twofa} from './twofa.js'
import {code_2fa} from './code_2fa.js'
import {qrcode_2fa} from './qrcode_2fa.js'
import {display_2fa} from './display_2fa.js'
import {tournament_history} from './tournament_history.js'

import {Tournament} from './Tournament.js'

export class Main
{
    login = '';
    twofa = '';
    name = '';
    email = '';
    id = -1;
    status = '';
    secret_2fa = '';
    history_stack = [];

    constructor()
    {
        this.lobby = new Lobby(this);
        this.twofa = new twofa(this);
        this.signup = new Signup(this);
        this.log_in = new Login(this);
        this.code_2fa = new code_2fa(this);
        this.qrcode_2fa = new qrcode_2fa(this);
        this.display_2fa = new display_2fa(this);
        this.tournament_history = new tournament_history(this);

        this.dom_home = document.getElementById("home");
        this.dom_login = document.getElementById("login");
        this.dom_proceed = document.getElementById("proceed");
        this.dom_signup = document.getElementById("signup");
        this.dom_status = document.getElementById("status");
        this.dom_name = document.getElementById("name");
        this.dom_name.innerHTML = "Anonyme";
        this.dom_email = document.getElementById("email");
        this.dom_container = document.getElementById("container");
        this.dom_login42 = document.getElementById("login42");

        this.dom_signup.addEventListener("click", () => this.signup_click());
        this.dom_login.addEventListener("click", () => this.login_click());
        this.dom_home.addEventListener("click", () => {
            if (this.lobby.game && this.lobby.game !== undefined)
            {
                this.lobby.game.quit();
                this.lobby.game = undefined;
            }
            window.history.pushState({}, '', '/');
            this.load('/lobby', () => this.lobby.events());
        });
    }

    load(page, callback) {
        $.ajax({
            url: page + '/',
            method: 'GET',
            success: (html) => {
                this.dom_container.innerHTML = html;
                //pas oublier de changer ca
                if (callback && typeof callback === 'function') {
                    callback();
                }
                // callback();  // fait erreur "callback is not a function"
            },
            error: function(error) {
                console.error('Error: pong GET fail', error.message);
            }
        });
    }

	load_with_data(page, callback, data) {
        $.ajax({
            url: page + '/',
            method: 'GET',
			data : data,
            success: (html) => {
                this.dom_container.innerHTML = html;
                //pas oublier de changer ca
                if (callback && typeof callback === 'function') {
                    callback();
                }
                // callback();  // fait erreur "callback is not a function"
            },
            error: function(error) {
                console.error('Error: pong GET fail', error.message);
            }
        });
    }

    login_click() {
        this.history_stack.push('/login');
        window.history.pushState({page: '/login'}, '', '/login');
        this.load('/pages/login', () => this.log_in.events());
    }
    set_status(s) {this.dom_status.innerHTML = s;}

    signup_click() {
        this.history_stack.push('/signup');
        window.history.pushState({}, '', '/signup');
        this.load('/pages/signup', () => this.signup.events());
    }

}
