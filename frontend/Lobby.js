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
            if (data.type === 'users_list' ) {
                if (this.tournament)
                    this.tournament.userList(data.users);
            }
            if (data.type === 'already_in') {
                if (this.tournament)
                    this.tournament.alreadyIn(data.users)
            }
            else if (data.type == 'tournament_invite') {
                this.displayTournamentInvite(data.message.message, data.message.tour_id);
            }
            else if (data.type === 'tournament_invite_accepted') {
                if (this.tournament)
                    this.tournament.tournamentInviteAccepted(data.message);
            }
            else if (data.type === 'tournament_ready') {
                if (this.tournament)
                    this.tournament.tournamentReady();
            }
            else if (data.type === 'tournament_infos') {
                if (this.tournament)
                    this.tournament.tournamentInfos(data.name, data.round)
            }
            else if (data.type === 'tournament_matches' || data.type === 'match_update') {
                if (this.tournament)
                    this.tournament.displayTournamentMatches(data.matches);
            }
            else if (data.type === 'tournament_join') {
                if (this.tournament)
                    this.tournament.displayPlayerAction(data.message);
            }
            else if (data.type === 'tournament_join_valid') {
                if (this.tournament)
                    this.tournament.joinMatch(data);
            }
            else if (data.type === 'tournament_event_invite') {
                this.displayEventInvite(data.message);
            }
            else if (data.type === 'tournament_in_progress') {
                this.displayTournamentBack(data.message);
            }
            else if (data.type === 'tournament_owner_lobby') {
                this.displayTournamentLobbyBack(data.message);
            }
            else if (data.type === 'tournament_creation_OK') {
                this.tournamentLaunch();
            }
            else if (data.type === 'already_in_tournament') {
                // this.alreadyInTournament(data.message);
                // WHEN ACTION IS NOT POSSIBLE -> MESSAGE BOX ?
            }
            else if (data.type === 'tournament_in_setup') {
                if (this.tournament)
                    this.tournament.inSetup();
            }
            else if (data.type === 'match_status_update') {
                if (this.tournament)
                    this.tournament.updateMatchStatus(data);
            }
            else if (data.type === 'tournament_winner') {
                if (this.tournament)
                    this.tournament.winnerDisplay(data);
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
        this.socket.send(JSON.stringify({
            type: 'tournament_creation_request',
        }));
    }
    
    tournamentLaunch() {
        this.tournament = new Tournament(this.main);
        this.main.load('/tournament', () => this.tournament.events());
    }

    displayTournamentInvite(message, tourId) {
        let inviteContainer = document.getElementById('inviteContainer');
        if (!inviteContainer) {
            inviteContainer = document.createElement('div');
            inviteContainer.id = 'inviteContainer';
            document.body.appendChild(inviteContainer);
        }

        const inviteNotification = document.createElement('div');
        inviteNotification.classList.add('invite-notification');
        inviteNotification.innerHTML = `
            <p>${message}</p>
            <button id="acceptInviteBtn">Accept</button>
            <button id="declineInviteBtn">Decline</button>
        `;

        inviteContainer.appendChild(inviteNotification);

        document.getElementById('acceptInviteBtn').addEventListener('click', () => {
            this.tournamentInviteResponse('accept', tourId);
            inviteContainer.removeChild(inviteNotification);
        });
        document.getElementById('declineInviteBtn').addEventListener('click', () => {
            this.tournamentInviteResponse('decline', tourId);
            inviteContainer.removeChild(inviteNotification);
        });
    }

    displayEventInvite(tourID) {
        let noInviteContainer = document.getElementById('no-invite');
        if (noInviteContainer)
            return;
    
        let inviteContainer = document.getElementById('inviteContainer');
        if (!inviteContainer) {
            inviteContainer = document.createElement('div');
            inviteContainer.id = 'inviteContainer';
            document.addEventListener('DOMContentLoaded', () => document.body.appendChild(inviteContainer));
        }
    
        const inviteNotification = document.createElement('div');
        inviteNotification.classList.add('event-invite-notification');
        inviteNotification.innerHTML = `
            <p>Tournament is ready! Join?</p>
            <button id="acceptInviteBtn">Accept</button>
            <button id="declineInviteBtn">Decline</button>`;
    
        const appendInvite = () => {
            if(document.body.contains(inviteContainer)) {
                inviteContainer.appendChild(inviteNotification);
    
                document.getElementById('acceptInviteBtn').addEventListener('click', () => {
                    inviteContainer.removeChild(inviteNotification);
                    this.tournament = new Tournament(this.main, tourID);
                    this.tournament.queryRoundList();
                });
                document.getElementById('declineInviteBtn').addEventListener('click', () => {
                    inviteContainer.removeChild(inviteNotification);
                });
            } else {
                document.addEventListener('DOMContentLoaded', appendInvite);
            }
        };
    
        appendInvite();
    }    

    displayTournamentBack(tourID) {
        const existingButton = document.getElementById('tournament');

        if (existingButton) {
            const newButton = document.createElement('button');
            newButton.textContent = 'Tournament';
            newButton.id = 'tournament';
            newButton.addEventListener('click', () => {
                    this.tournament = new Tournament(this.main, tourID);
                    this.tournament.queryRoundList();
            });
            existingButton.parentNode.replaceChild(newButton, existingButton);
        }
    }

    displayTournamentLobbyBack(tourID) {
        const existingButton = document.getElementById('tournament');

        if (existingButton) {
            const newButton = document.createElement('button');
            newButton.textContent = 'Tournament';
            newButton.id = 'tournament';
            newButton.addEventListener('click', () => {
                    this.tournament = new Tournament(this.main, tourID);
                    this.main.load('/tournament/lobby', () => this.tournament.eventsLobby());
            });
            existingButton.parentNode.replaceChild(newButton, existingButton);
        }
    }

    tournamentInviteResponse(response, tourId) {
        if (response === 'accept') {
            this.socket.send(JSON.stringify({
                type: 'tournament_invite_resp',
                response: 'accept',
                id: tourId,
                login: this.main.login
            }));
        } else {
            this.socket.send(JSON.stringify({
                type: 'tournament_invite_resp',
                response: 'decline',
                id: tourId,
                login: this.main.login
            }));
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
