import {Game} from './Game.js'
import {Pong} from './Pong.js'

export class Main
{
    user = "";
    name = "";
    id = -1;
    status = "";
    game_info;

    constructor()
    {
        this.game = new Game(this);
        this.pong = new Pong(this);
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
                this.user = response.user;
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
}
