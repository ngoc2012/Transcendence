import {Pong} from './Pong.js'
import {new_connection} from './new_connection.js'

export class Lobby
{
    constructor(m) {
        this.main = m;
        this.socket = -1;
    }
    
    events() {
        this.game = null;
        this.dom_pong = document.querySelector("#pong");
        this.dom_pew = document.querySelector("#pew");
        this.dom_join = document.querySelector("#join");
        this.dom_rooms = document.getElementById("rooms");
        this.dom_pong.addEventListener("click", () => this.new_pong("pong"));
        this.dom_join.addEventListener("click", () => this.join());
        //this.rooms_update();
    }

    join() {
        if (this.dom_rooms.selectedIndex === -1)
            return;
        $.ajax({
            url: '/join_game',
            method: 'POST',
            data: {
                "user": this.main.user,
                "id": this.dom_rooms.options[this.dom_rooms.selectedIndex].value
            },
            success: (info) => {
                switch (info.game) {
                    case 'pong':
                        this.pong_game(info);
                        break;
                }
            },
            error: (error) => this.main.set_status('Error: Can not join game')
        });
    }

    new_game(game) {
        $.ajax({
            url: '/new_game',
            method: 'POST',
            data: {
                "user": this.main.user,
                "game": game
            },
            success: (info) => this.pong_game(info),
            error: (error) => this.main.set_status('Error: Can not create game')
        });
    }

    pong_game(info) {
        this.game = new Pong(this.main, this, info);
        this.main.load('/pong', () => this.game.init());
    }

    rooms_update() {
        new_connection({
            name: "rooms update",
            socket: this.socket,
            link: 'ws://127.0.0.1:8000/rooms',
            callback: {
                message: (data) => {
                    var options_rooms = this.dom_rooms && this.dom_rooms.options;
                    this.dom_rooms.innerHTML = "";
                    if (options_rooms && data.rooms && data.rooms.length > 0) {
                        data.rooms.forEach((room) => {
                            var option = document.createElement("option");
                            option.value = room.id;
                            option.text = "" + room.id;
                            room.players.forEach((p) => {
                                option.text += " - " + p;
                            });
                            this.dom_rooms.add(option);
                        });
                    }
                },
                error: this.rooms_update
            }
        });
    }
}
