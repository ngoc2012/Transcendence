import {Pong} from './Pong.js'
import {Tournament} from './Tournament.js';

export class Lobby
{
    constructor(m) {
        this.main = m;
        this.socket = -1;
        this.game = null;
        this.tournament = null;
    }
    
    events() {
        this.dom_rooms = document.getElementById("rooms");
        this.dom_tournament = document.getElementById("tournament");
        this.dom_join = document.querySelector("#join");
        this.dom_pong = document.querySelector("#pong");
        this.dom_pew = document.querySelector("#pew");
        this.dom_delete = document.querySelector("#delete");
        this.dom_pong.addEventListener("click", () => this.new_game("pong"));
        this.dom_pew.addEventListener("click", () => this.new_game("pew"));
        this.dom_delete.addEventListener("click", () => this.delete_game());
        this.dom_join.addEventListener("click", () => this.join());
        this.dom_tournament.addEventListener("click", () => this.tournament_click());
        this.rooms_update();
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
                    this.socket.send(JSON.stringify({
                        type: 'update'
                    }));
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
        if (this.main.login === '')
        {
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
                'login': this.main.login
            },
            success: (info) => {
                this.main.set_status(info);
                if (this.socket !== -1)
                    this.socket.send(JSON.stringify({
                        type: 'update'
                    }));
            },
            error: (error) => this.main.set_status('Error: Can not join game')
        });
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
        else {
            this.socket.send(JSON.stringify({
                type: 'update'
            }));        
        }

        this.socket.onmessage = (e) => {
            if (!('data' in e))
                return;
            const data = JSON.parse(e.data);
            if (data.type === 'users_list' ) {
                if (this.tournament)
                    this.tournament.userList(data.users);
            }
            else if (data.type == 'tournament_invite') {
                this.displayTournamentInvite(data.message, data.tour_id);
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
            // console.error('Error: Socket Closed');
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

    displayTournamentInvite(message, tourId) {
        // Create a container for the invite notification if it doesn't exist
        let inviteContainer = document.getElementById('inviteContainer');
        if (!inviteContainer) {
            inviteContainer = document.createElement('div');
            inviteContainer.id = 'inviteContainer';
            document.body.appendChild(inviteContainer);
        }
    
        // Create the invite notification
        const inviteNotification = document.createElement('div');
        inviteNotification.classList.add('invite-notification'); // Add some CSS class for styling
        inviteNotification.innerHTML = `
            <p>${message}</p>
            <button id="acceptInviteBtn">Accept</button>
            <button id="declineInviteBtn">Decline</button>
        `;
    
        // Append the invite notification to the container
        inviteContainer.appendChild(inviteNotification);
    
        // Add event listeners for the accept and decline buttons
        document.getElementById('acceptInviteBtn').addEventListener('click', function() {
            acceptTournamentInvite(tourId);
            inviteContainer.removeChild(inviteNotification); // Remove the invite notification
        });
        document.getElementById('declineInviteBtn').addEventListener('click', function() {
            // Optionally do something on decline
            inviteContainer.removeChild(inviteNotification); // Remove the invite notification
        });
    }

    quit() {
        if (this.socket !== -1)
        {
            this.socket.close();
            this.socket = -1;
        }
    }
}
