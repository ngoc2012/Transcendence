import {Lobby} from './Lobby.js'
import {Pong} from './Pong.js';

export class Tournament {

    constructor(m) {
        this.main = m;
        this.lobby = m.lobby;
        this.id = -1;
        this.game = null;
    }

    events() {
        this.dom_tournamentForm = document.getElementById('tournamentForm');
        this.dom_tournamentForm.addEventListener('submit', (e) => this.tournamentSubmit(e));
    }

    eventsLobby() {
        this.dom_player_list = document.getElementById('players-list');
        if (this.dom_player_list)
            this.main.lobby.socket.send(JSON.stringify({type: 'request_users_list'}));
            const inviteButton = document.querySelector(`button[data-login='${login}']`);
        this.dom_start_tournament = document.getElementById('start-tournament');
        this.dom_start_tournament.disabled = true;
    }

    eventsStart() {
        this.dom_matches = document.getElementById('tournament-matches');
        if (this.dom_matches) {
            const data = {
            type: 'tournament_list',
            id: this.id
            };
            this.main.lobby.socket.send(JSON.stringify(data));
        }
    }
    
    tournamentSubmit(event) {
        event.preventDefault();

        const formData = {
            name: document.getElementById('tname').value,
            game: document.getElementById('game').value,
            login: this.main.login,
        };

        $.ajax({
            url: '/tournament/new/',
            method: 'POST',
            data: formData,
            success: (response) => {
                this.id = response.id;
                this.main.set_status('Tournament created successfully');
                console.log(response);
                this.main.load('/tournament/lobby', () => this.eventsLobby());
            },
            error: () => {
                this.main.set_status('Error: Could not create tournament');
            }
        });
    }

    userList(users) {
        const playersList = document.getElementById('players-list');
        playersList.innerHTML = '';
        users.forEach((user) => {
            if (user.login === this.main.login) {
                return;
            }
    
            const li = document.createElement('li');
            li.textContent = `${user.login}`; // Display the user's login
            
            const inviteButton = document.createElement('button');
            inviteButton.setAttribute('data-login', user.login);
            inviteButton.textContent = 'Send Invite';
            inviteButton.onclick = () => {
                this.sendInvite(user.login, this.id);
            };
            
            li.appendChild(inviteButton);
            playersList.appendChild(li);
        });
    }

    tournamentInviteAccepted(login) {
        const inviteButton = document.querySelector(`button[data-login='${login}']`);
        if (inviteButton) {
            inviteButton.textContent = 'Accepted';
            inviteButton.disabled = true;
        }
    }

    sendInvite(userId, tournamentId) {
        const inviteData = {
            type: 'tournament_invite',
            inviteeId : userId,
            tourId : tournamentId
        };
        this.main.lobby.socket.send(JSON.stringify(inviteData));
        console.log(`Game invite sent to ${userId}`);
    }

    tournamentReady() {
        this.dom_start_tournament.addEventListener('click', (e) => {this.queryTournamentRound(e); this.startEventInvite();});
        this.dom_start_tournament.disabled = false;
    }

    queryTournamentRound() {
        const tournamentUrl = `/tournament/${this.id}`;
        this.main.load(tournamentUrl, () => this.eventsStart());
        const data = {
        type: 'tournament_rounds',
        id: this.id
        };
        this.main.lobby.socket.send(JSON.stringify(data));
    }

    queryRoundList() {
        const tournamentUrl = `/tournament/${this.id}`;
        this.main.load(tournamentUrl, () => this.eventsStart());
    }

    startEventInvite() {
        const inviteData = {
            type: 'tournament_event_invite',
            tour_id : this.id
        };
        this.main.lobby.socket.send(JSON.stringify(inviteData));
        console.log(`Event invite sent to players`);
    }

    eventInvite(tourID) {
        this.id = tourID;
        // this.queryTournamentRound();
        this.queryRoundList();
    }

    tournamentInfos(name, round) {
        const tournamentInfosContainer = document.getElementById('tournament-infos');
        tournamentInfosContainer.innerHTML = '';
    
        tournamentInfosContainer.innerHTML = `
            <h3>Tournament - ${name} - Round: ${round}</h3>
        `;
    }

    displayTournamentMatches(matches) {
        const matchesContainer = document.getElementById('tournament-matches');
        matchesContainer.innerHTML = '';
        
        matches.forEach(match => {
            const matchElement = document.createElement('div');
            matchElement.className = 'match';
            
            matchElement.innerHTML = `
                <p>Room ID: ${match.room_id}</p>
                <p>Player 1: ${match.player1_name} vs. Player 2: ${match.player2_name}</p>
                <p>Status: ${match.status}</p>
            `;
            matchElement.setAttribute('match-id', match.room_id);
            matchesContainer.appendChild(matchElement);
        });
        this.main.lobby.socket.send(JSON.stringify({
            type: 'tournament-player-action',
            id: this.id
        }));
    }

    displayPlayerAction(matchId) {
        const matchElement = document.querySelector(`[match-id="${matchId}"]`);
        if (matchElement) {
            const button = document.createElement('button');
            button.textContent = 'Join';
            matchElement.appendChild(button);
            button.onclick = () => {
                this.main.lobby.socket.send(JSON.stringify({
                    type: 'tournament-join',
                    tour_id: this.id,
                    match_id: matchId 
                }));
            };
        }
    }

    joinMatch(data) {
        $.ajax({
            url: '/game/tournament/join',
            method: 'POST',
            data: {
                'login': this.main.login,
                "game_id": data.matchId
            },
            success: (info) => {
                if (typeof info === 'string')
                    return;
                else
                {
                    switch (info.game) {
                        case 'pong':
                            this.game = new Pong(this.main, this.main.lobby, info);
                            this.main.load('/pong', () => this.game.init());
                            break;
                    }
                }
            },
            error: () => this.main.set_status('Error: Can not join game')
        });
    }
}