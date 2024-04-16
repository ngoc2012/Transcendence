import {Pong} from './Pong.js'
import { Chat_signup } from './Chat_signup.js'
import {Tournament} from './Tournament.js';

export class Lobby
{
    constructor(m) {
        this.main = m;
        this.socket = -1;
        this.game = null;
        this.tournament = null;
        this.ws = null;
    }

    events() {
        this.main.checkcsrf();
        this.dom_rooms = document.getElementById("rooms");
        this.dom_tournament = document.getElementById("tournament");
        this.dom_tournament_history = document.getElementById("tournament_history");
        this.dom_join = document.querySelector("#join");
        this.dom_pong = document.querySelector("#pong");
        this.dom_pew = document.querySelector("#pew");
        this.dom_chat = document.querySelector("#chat");
        this.dom_delete = document.querySelector("#delete");
        this.dom_pong.addEventListener("click", () => this.new_game("pong"));
        this.dom_pew.addEventListener("click", () => this.new_game("pew"));
        this.dom_delete.addEventListener("click", () => this.delete_game());
        this.dom_join.addEventListener("click", () => this.join());
		this.dom_chat.addEventListener("click", () => this.chat());
        this.dom_tournament.addEventListener("click", () => this.tournament_click());
        this.dom_tournament_history.addEventListener("click", () => this.tournament_history_click());
        if (this.main.login != '') {
            this.rooms_update();
            this.queryTournament();
        }
    }

	chat(){
		this.main.set_status('')
		if (this.main.login === ''){
			this.main.set_status('You must be logged in to chat.');
			return;
		}
		this.chat_signup = new Chat_signup(this.main);
        this.main.load_with_data('transchat/chat_lobby', () => this.chat_signup.events(this.main), {
            'username': this.main.login
        });
	}

    join() {
        if (this.dom_rooms.selectedIndex === -1)
            return;

        var csrftoken = this.main.getCookie('csrftoken');

        if (csrftoken) {
            $.ajax({
                url: '/game/join',
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrftoken,
                },        
                data: {
                    'login': this.main.login,
                    "game_id": this.dom_rooms.options[this.dom_rooms.selectedIndex].value
                },
                success: (info) => {
                    if (typeof info === 'string') {
                        this.main.set_status(info);
                        this.rooms_update();
                    } else {
                        switch (info.game) {
                            case 'pong':
                                this.pong_game(info);
                                break;
                        }
                    }
                },
                error: () => this.main.set_status('Error: Can not join game')
            });
        } else {
            console.log('Login required');
            this.main.load('/pages/login', () => this.main.log_in.events());
        }
    }

    new_game(game) {
        this.main.set_status('');
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
                    'name': 'Stars war',
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
        } else {
            console.log('Login required');
            this.main.load('/pages/login', () => this.main.log_in.events());
        }
    }

    tournament_history_click() {
        if (this.main.login === ''){
			this.main.set_status('You must be logged to see the tournament history.');
			return;
		}
        this.main.load('/tournament_history', () => this.main.tournament_history.events());
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

        var csrftoken = this.main.getCookie('csrftoken');

        if (csrftoken) {
            $.ajax({
                url: '/game/delete',
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrftoken,
                },
                data: {
                    'game_id': this.dom_rooms.options[this.dom_rooms.selectedIndex].value,
                    'login': this.main.login,
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
                            this.socket.send(JSON.stringify({
                            type: 'update'
                        }));
                        }
                    }
                    if (this.socket !== -1) {
                        this.socket.send(JSON.stringify({
                            type: 'update'
                        }));
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
        } else {
            console.log('Login required');
            this.main.load('/pages/login', () => this.main.log_in.events());
        }
    }

    pong_game(info) {
        this.quit();
        this.game = new Pong(this.main, this, info);
        this.main.load('/pong', () => this.game.init());
    }

    rooms_update() {
        if (this.socket === -1) {
            this.main.set_status('');
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
            this.socket.send(JSON.stringify({
                type: 'tournament_registered',
            }));
        };
        
        $.ajax({
            url: '/game/update',
            method: 'GET',
            success: (rooms) => {
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
            },
            error: () => this.main.set_status('Error: Can not update rooms')
        });

        this.socket.onmessage = (e) => {
            if (!('data' in e))
                return;
            const data = JSON.parse(e.data);
            if (data.type === 'tournament_local_progress') {
                this.displayTournamentLocalBack(data.message);
            }
            else if (data.type === 'error_nf') {
                // this.main.load('/tournament/lobby', () => this.eventsLobby());
            }
            else {
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
        }

        this.socket.onclose = (e) => {

        };
    }

    tournament_click() {
        if (this.main.login === '')
        {
            this.main.set_status('Please login or sign up');
            return;
        }
        this.tournament = new Tournament(this.main);
        this.main.load('/tournament', () => this.tournament.events());
    }

    displayTournamentLocalBack(tourID) {
        const existingButton = document.getElementById('tournament');

        if (existingButton) {
            const newButton = document.createElement('button');
            newButton.textContent = 'Tournament';
            newButton.id = 'tournament';
            newButton.addEventListener('click', () => {
                    this.tournament = new Tournament(this.main, tourID);
                    this.tournament.localBack();
            });
            existingButton.parentNode.replaceChild(newButton, existingButton);
        }
    }

    queryTournament() {
        if (this.socket !== -1) {
            if (this.socket.readyState === WebSocket.OPEN) {
                this.socket.send(JSON.stringify({
                    type: 'tournament_registered',
                }));
            }
        }
    }

    checkLogin() {
        if (this.main.login != '') {
            this.dom_l
        }
    }

    quit() {
        if (this.socket !== -1)
        {
            this.socket.close();
            this.socket = -1;
        }
    }
}
