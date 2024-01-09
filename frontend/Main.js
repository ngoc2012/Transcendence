import {Lobby} from './Lobby.js'

export class Main
{
    user = "";
    id = -1;
    status = "";

    constructor()
    {
        this.lobby = new Lobby(this);
        this.dom_login = document.getElementById("login");
        this.dom_status = document.getElementById("status");
        this.dom_user_name = document.getElementById("user_name");
        this.dom_container = document.getElementById("container");
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

    set_status(s) { dom.textContent = s; }
}
