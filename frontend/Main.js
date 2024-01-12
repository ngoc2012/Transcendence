import {Lobby} from './Lobby.js'
import {Signup} from './Signup.js'

export class Main
{
    login = "";
    name = "";
    id = -1;
    status = "";

    constructor()
    {
        this.lobby = new Lobby(this);
        this.signup = new Signup(this);
        this.dom_login = document.getElementById("login");
        this.dom_signup = document.getElementById("signup");
        this.dom_status = document.getElementById("status");
        this.dom_user_name = document.getElementById("user_name");
        this.dom_container = document.getElementById("container");
        this.dom_signup.addEventListener("click", () => this.signup());
    }

    new_player() {
        $.ajax({
            url: '/new_player',
            method: 'GET',
            //headers: {'X-CSRFToken': csrftoken},
            success: (response) => {
                this.user = response;
                console.log("new player :", this.user);
                this.dom_user_name.innerHTML = this.user;
            },
            error: function(error) {
                console.error('Error: sending new player demand', error.message);
            }
        });
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

    signup() {
        this.load('/signup', () => this.signup.events());
    }
    set_status(s) { dom.textContent = s; }
}
