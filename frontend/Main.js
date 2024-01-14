import {Lobby} from './Lobby.js'
import {Signup} from './Signup.js'
import {Login} from './Login.js'

export class Main
{
    login = '';
    name = '';
    id = -1;
    status = '';

    constructor()
    {
        this.lobby = new Lobby(this);
        this.signup = new Signup(this);
        this.log_in = new Login(this);
        this.dom_login = document.getElementById("login");
        this.dom_signup = document.getElementById("signup");
        this.dom_status = document.getElementById("status");
        this.dom_name = document.getElementById("name");
        this.dom_name.innerHTML = "Anonyme";
        this.dom_container = document.getElementById("container");
        this.dom_signup.addEventListener("click", () => this.signup_click());
        this.dom_login.addEventListener("click", () => this.login_click());
    }

    load(page, callback) {
        $.ajax({
            url: page + '/',
            method: 'GET',
            success: (html) => {
                //window.history.pushState({
                //    "user": this.user
                //}, page, page);
                this.dom_container.innerHTML = html;
                callback();
            },
            error: function(error) {
                console.error('Error: pong GET fail', error.message);
            }
        });
    }

    signup_click() {
        this.load('/signup', () => this.signup.events());
    }

    login_click() {
        this.load('/login', () => this.log_in.events());
    }
    set_status(s) {this.dom_status.innerHTML = s;}
}
