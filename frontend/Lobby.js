import {Pong} from './Pong.js'
import { Chat } from './Chat.js'
import { Profile } from './Profile.js'

export class Lobby
{
    constructor(m) {
        this.main = m;
        this.socket = -1;
        this.game = null;
    }
    
    events() {
        this.dom_rooms = document.getElementById("rooms");
        this.dom_join = document.querySelector("#join");
        this.dom_pong = document.querySelector("#pong");
        this.dom_pew = document.querySelector("#pew");
        this.dom_chat = document.querySelector("#chat");
        this.dom_delete = document.querySelector("#delete");
        this.dom_profile = document.querySelector('#profile');
        this.dom_pong.addEventListener("click", () => this.new_game("pong"));
        this.dom_pew.addEventListener("click", () => this.new_game("pew"));
        this.dom_delete.addEventListener("click", () => this.delete_game());
        this.dom_join.addEventListener("click", () => this.join());
		this.dom_chat.addEventListener("click", () => this.start_chat());
        this.dom_profile.addEventListener("click", () => this.profile());
        this.rooms_update();
    }

	start_chat(){
		this.main.set_status('')
		if (this.main.login === ''){
			this.main.set_status('You must be logged in to chat.');
			return;
		}
        $.ajax({
			url: '/transchat/chat_lobby/',
			method: 'POST',
			data:{
				'username': this.main.login
			}
		});
		this.main.chat = new Chat(this.main);
        this.main.load('transchat/general_chat', () => this.main.chat.init());
	}

    profile(){
        this.main.set_status('');
        if (this.main.login === ''){
            this.main.set_status('You must be logged in to see your profile');
            return ;
        }
        this.main.profile = new Profile(this.main);
        this.main.load('/profile/' + this.main.login, () => this.main.profile.init());
    }

    join() {
        if (this.dom_rooms.selectedIndex === -1)
            return;
        $.ajax({
            url: '/game/join',
            method: 'POST',
            data: {
                'login': this.main.login,
                "game_id": this.dom_rooms.options[this.dom_rooms.selectedIndex].value
            },
            success: (info) => {
                if (typeof info === 'string')
                {
                    this.main.set_status(info);
                }
                else
                {
                    switch (info.game) {
                        case 'pong':
                            this.pong_game(info);
                            break;
                    }
                }
            },
            error: () => this.main.set_status('Error: Can not join game')
        });
    }

    new_game(game) {
        this.main.set_status('');
        if (this.main.login === '')
        {
            this.main.set_status('Please login or sign up');
            return;
        }
        $.ajax({
            url: '/game/new',
            method: 'POST',
            data: {
                'name': 'Stars war',
                'game': game,
                'login': this.main.login
            },
            success: (info) => {
                if (this.socket !== -1)
                    this.socket.send('update');
                if (typeof info === 'string')
                {
                    this.main.set_status(info);
                }
                else
                {
                    //this.main.set_status('Game ' + info.name + ' created.');
                    switch (info.game) {
                        case 'pong':
                            this.pong_game(info);
                            break;
                    }
                }
            },
            error: () => this.main.set_status('Error: Can not create game')
        });
    }

    delete_game() {
        this.main.set_status('');
        if (this.main.login === '') {
            this.main.set_status('Please login or sign up');
            return;
        }
        if (this.dom_rooms.selectedIndex === -1) {
            this.main.set_status('Select a game');
            return;
        }
        $.ajax({
            url: '/game/delete',
            method: 'POST',
            data: {
                'game_id': this.dom_rooms.options[this.dom_rooms.selectedIndex].value,
                'login': this.main.login,
            },
            headers: {
                'Authorization': `Bearer ${sessionStorage.JWTToken}`
            },
            success: (response) => {
                if (response.token) {
                    sessionStorage.setItem('JWTToken', response.token);
                }
                if (response.error) {
                    const message = response.message;
                    this.main.set_status('Error: ' + message);
                } else if (response.message) {
                    const message = response.message;
                    this.main.set_status(message);
                    if (this.socket !== -1) {
                        this.socket.send('update');
                    }
                }
            },
            error: (xhr, textStatus, errorThrown) => {
            let errorMessage = "Error: Can not delete game";
            if (xhr.responseJSON && xhr.responseJSON.error) {
                errorMessage = xhr.responseJSON.error;
            }
            this.main.set_status(errorMessage);
            }
        });
    }

    pong_game(info) {
        this.quit();
        this.game = new Pong(this.main, this, info);
        this.main.load('/pong', () => this.game.init());
    }

    rooms_update() {
        this.main.set_status('');
        this.socket = new WebSocket(
            'wss://'
            + window.location.host
            + '/ws/game/rooms/'
        );

        this.socket.onmessage = (e) => {
            if (!('data' in e))
                return;
            const rooms = JSON.parse(e.data);
            var options_rooms = this.dom_rooms && this.dom_rooms.options;
            this.dom_rooms.innerHTML = "";
            if (options_rooms && rooms && rooms.length > 0) {
                rooms.forEach((room) => {
                    var option = document.createElement("option");
                    option.value = room.id;
                    option.text = room.name + " - " + room.id;
                    this.dom_rooms.add(option);
                });
            }
        };

        this.socket.onclose = (e) => {
            //console.error('Chat socket closed unexpectedly');
        };
    }

    quit() {
        if (this.socket !== -1)
        {
            this.socket.close();
            this.socket = -1;
        }
    }
}
