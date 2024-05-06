import {Pong} from './Pong.js'
import { Chat } from './Chat.js'
import { Profile } from './Profile.js'
import {Tournament} from './Tournament.js';
import {join_game} from './game.js';

export class Lobby
{
    constructor(m) {
        this.main = m;
        this.socket = -1;
        this.game = null;
        this.tournament = null;
        this.ws = null;
        this.socketTour1 = null;
        this.socketTour2 = null;
    }

    events(isPopState) {
        if (this.main.lobby.game && this.main.lobby.game !== null)
        {
            this.main.lobby.game.close_room();
            this.main.lobby.game = null;
        }

        this.main.checkcsrf();

        this.main.set_chat(this.main.login);
        if (this.main.login != '') {
            this.rooms_update();
        }

        if (!isPopState)
            window.history.pushState({page: '/'}, '', '/');

        if (this.listenersOK) {
            return;
        }

        this.dom_rooms = document.getElementById("rooms");
        // this.dom_tournament = document.getElementById("tournament");
        // this.dom_tournament_history = document.getElementById("tournament_history");
        // this.dom_tournament2 = document.getElementById("tournament2");
        // this.dom_tournament_history2 = document.getElementById("tournament_history2");
        this.dom_join = document.querySelector("#join");
        // this.dom_pong = document.getElementById("pong");
        // this.dom_pong2 = document.getElementById("pong2");
        // this.dom_chat = document.querySelector("#chat");
        // this.dom_chat2 = document.querySelector("#chat2");
        this.dom_delete = document.querySelector("#delete");
        // this.dom_profile = document.querySelector('#profile');
        // this.dom_homebar = document.querySelector('#homebar');
        // this.dom_homebar2 = document.querySelector('#homebar2');
        // this.dom_pong.addEventListener("click", () => this.new_game("pong"));
        // this.dom_pong2.addEventListener("click", () => this.new_game("pong"));

        this.dom_join.addEventListener("click", () => {
            if (this.dom_rooms.selectedIndex === -1) {
                this.main.set_status('Please select a room to join');
                return;
            }
            join_game(this.main, this.dom_rooms.options[this.dom_rooms.selectedIndex].value);
        });
		// this.dom_chat.addEventListener("click", () => this.start_chat());
        // this.dom_chat2.addEventListener("click", () => this.start_chat());

        // this.dom_profile.addEventListener("click", () => this.profile(false));
        // this.dom_homebar.addEventListener("click", () => this.homebar());
        // this.dom_homebar2.addEventListener("click", () => this.homebar());
        // this.dom_tournament.addEventListener("click", () => this.tournament_click());
        // this.dom_tournament2.addEventListener("click", () => this.tournament_click());
        // this.dom_tournament_history.addEventListener("click", () => this.tournament_history_click());
        // this.dom_tournament_history2.addEventListener("click", () => this.tournament_history_click());

        this.listenersOK = true;
    }

    // 2FA Tournament
    eventsCallback(tourid) {
        this.tournament = new Tournament(this.main, tourid);
        this.main.load('/tournament/local/start', () => this.tournament.localBack(false));
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
		this.main.chat = new Chat(this.main, this.main.lobby);
        this.main.load('transchat/general_chat', () => this.main.chat.events(false));
	}

    profile(){

        if (this.main.login === ''){
            this.main.set_status('You must be logged in to see your profile');
            return ;
        }
        this.main.load_with_data('/profile/' + this.main.login, () => this.main.profile.init(false), {'requester': this.main.login, 'user': this.main.login});
    }

    homebar() {
        this.main.load('/lobby', () => this.events(false));
    }

    new_game(game) {
        if (this.main.login === '')
        {
            this.main.set_status('Please login or sign up');
            return;
        }

        var csrftoken = this.main.getCookie('csrftoken');

        if (csrftoken) {
            $.ajax({
                url: '/game/new',
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrftoken,
                },
                data: {
                    'name': 'PONG',
                    'game': game,
                    'login': this.main.login
                },
                success: (info) => {
                    if (this.socket !== -1)
                        this.socket.send(JSON.stringify({
                            type: 'update'
                        }));
                    if (typeof info === 'string')
                    {
                        this.main.set_status(info);
                        this.rooms_update();
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
                error: () => this.main.set_status('Error: Can not create game')
            });
        } else
            this.main.load('/pages/login', () => this.main.log_in.events(false));
    }

    tournament_history_click() {
        if (this.main.login === ''){
			this.main.set_status('You must be logged to see the tournament history.');
			return;
		}
        this.main.load('/tournament_history', () => this.main.tournament_history.events(false));
    }

    pong_game(info) {
        this.quit();
        this.game = new Pong(this.main, this, info);
        this.main.load('/pong', () => this.game.init());
    }

    rooms_update() {
        if (this.socket === -1) {
            this.socket = new WebSocket(
                'wss://'
                + window.location.host
                + '/ws/game/rooms/'
            );
        }

        this.socket.onopen = () => {
            this.socket.send(JSON.stringify({
                type: "authenticate",
                token: this.ws,
            }));
        };

        this.socket.onmessage = (e) => {
            if (!('data' in e))
                return;
            const data = JSON.parse(e.data);
            if (data.type === 'friend_request_send'){
                this.main.profile.send_request(data);
            }
            else if (data.type === 'friend_request_receive'){
                if (data.receiver === this.main.login){
                    this.main.profile.receive_request(data)
                }
            }
            else if (data.type === 'users_list'){
                // Je ne sais pas si on doit faire quelque chose ici
            }
            else if (data.type === 'rooms') {
                const rooms = data.room;
                const selectElement = document.getElementById('rooms');

                for (let i = selectElement.options.length - 1; i >= 0; i--) {
                    selectElement.remove(i);
                }

                if (rooms && rooms.length > 0) {
                    rooms.forEach((room) => {
                        var option = document.createElement("option");
                        option.value = room.id;
                        let string = room.id.substring(0, 5);
                        option.text = `${room.name} - ${string}... - ${room.owner}`;
                        selectElement.add(option);
                    });
                } else {
                    var noRoomsOption = document.createElement("option");
                    noRoomsOption.text = "No rooms available";
                    selectElement.add(noRoomsOption);
                }
            }
        }

        if (this.socket.readyState === 1){
            this.socket.send(JSON.stringify({
                'type': 'status',
                'login': this.main.login
            }));
            this.socket.send(JSON.stringify({
                type: "authenticate",
                token: this.ws,
            }));
        }


        if (this.main.chat_socket === -1){
            this.main.chat_socket = new WebSocket(
                'wss://'
                + window.location.host
                + '/ws/transchat/general_chat/'
            );
        }
        this.main.chat_socket.onopen = (e) => {
		    if (this.main.login != ''){
           	    this.main.chat_socket.send(JSON.stringify({
               	    'type': 'connection',
	                'user': this.main.login,
               	}));
		    }
        };

       	this.main.chat_socket.onmessage = (e) => {
       	    var data = JSON.parse(e.data);
            var list_user = document.getElementById('user_list');
            if (data.type === 'update'){
                this.main.refresh_user_list(data.users, data.pictures);
                return;
            }
            else
		        document.querySelector('#chat-log').value += (data.message + '\n');
       	};
    }

    tournament_click() {
        if (this.main.login === '')
        {
            this.main.set_status('Please login or sign up');
            return;
        }

        var csrftoken = this.main.getCookie('csrftoken');

        if (csrftoken) {
            $.ajax({
                url: '/tournament/request/',
                method: 'GET',
                headers: {
                    'X-CSRFToken': csrftoken,
                },
                success: (response) => {
                    console.log(response.status);
                    if (response.status === 'not_found') {
                        this.tournament = new Tournament(this.main);
                        this.main.load('/tournament', () => this.tournament.events(false));
                    } else {
                        this.tournament = new Tournament(this.main, response.id);
                        this.tournament.localBack();
                    }
                },
                error: () => {
                    console.log('error');
                }
            });
        }
    }

    checkLogin() {
        if (this.main.login != '') {
            this.dom_l
        }
    }

    quit() {
        var user_list = document.getElementById('user-list');
        if (user_list){
            user_list.innerHTML = "<p>You must be logged<br>to see online users</p>";
        }
        if (this.socket !== -1)
        {
            this.socket.close();
            this.socket = -1;
        }
        if (this.main.chat_socket !== -1){
            this.main.chat_socket.send(JSON.stringify({
                'type': 'update'
            }));
            this.main.chat_socket.close();
            this.main.chat_socket = -1;
        }
    }
}
