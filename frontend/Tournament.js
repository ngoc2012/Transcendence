import {Lobby} from './Lobby.js'
import {Pong} from './Pong.js';

export class Tournament {

    constructor(m, id = null) {
        this.main = m;
        this.lobby = m.lobby;
        this.id = id;
        this.game = null;
        this.ready = -1;
        this.final = 0;
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
            this.main.lobby.socket.send(JSON.stringify({type: 'request_users_in_tour', id: `${this.id}`}));
        this.dom_start_tournament = document.getElementById('start-tournament');
        this.dom_start_tournament.disabled = true;
        this.dom_quit_tournament = document.getElementById('quit-tournament');
        this.dom_quit_tournament.addEventListener('click', (e) => this.quitTournament())
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
        this.dom_lobby_tournament = document.getElementById('Lobby');
        this.dom_lobby_tournament.addEventListener('click', (e) => this.backToLobby())
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
                this.main.load('/tournament/lobby', () => this.eventsLobby());
                this.main.lobby.socket.send(JSON.stringify({type: 'add_to_group', id: this.id}));
            },
            error: (xhr, textStatus, errorThrown) => {
                if (xhr.status === 400) {
                    var errorResponse = JSON.parse(xhr.responseText);
                    this.main.set_status('Error: ' + errorResponse.error);
                } else {
                    this.main.set_status('Error: Could not create tournament');
                }
            }
        });
        
    }
    
    alreadyIn(users) {
        const acceptedList = document.getElementById('accepted-list');
        users.forEach(user => {
            if (user.login === this.main.login) {
                return;
            }
            const li = document.createElement('li');
            li.setAttribute('data-login', user.login);
            li.textContent = `${user.login}`;
    
            const acceptedButton = document.createElement('button');
            acceptedButton.setAttribute('data-login', user.login);
            acceptedButton.textContent = 'Accepted';
            acceptedButton.disabled = true;
            li.appendChild(acceptedButton);
            acceptedList.appendChild(li);
        });
    }
    

    createUserListItem(user) {
        const li = document.createElement('li');
        li.textContent = user.login;
        
        const inviteButton = document.createElement('button');
        inviteButton.setAttribute('data-login', user.login);
        inviteButton.textContent = 'Send Invite';
        inviteButton.onclick = () => this.sendInvite(user.login, this.id);
        li.appendChild(inviteButton);
        return li;
    }

    userList(users) {
        const playersList = document.getElementById('players-list');
        const acceptedList = document.getElementById('accepted-list');
        const acceptedLogins = new Set([...acceptedList.querySelectorAll('[data-login]')].map(li => li.getAttribute('data-login')));
        playersList.innerHTML = '';
        
        users.forEach(user => {
            if (user.login === this.main.login || acceptedLogins.has(user.login)) {
                return;
            }
            const li = this.createUserListItem(user);
            playersList.appendChild(li);
        });
    }

    tournamentInviteAccepted(login) {
        const inviteButton = document.querySelector(`button[data-login='${login}']`);
        if (inviteButton) {
            inviteButton.textContent = 'Accepted';
            inviteButton.disabled = true;
            
            const li = inviteButton.closest('li');
            const acceptedList = document.getElementById('accepted-list');
            acceptedList.appendChild(li);
        }
    }

    sendInvite(userId, tournamentId) {
        const inviteData = {
            type: 'tournament_invite',
            inviteeId : userId,
            tourId : tournamentId
        };
        this.main.lobby.socket.send(JSON.stringify(inviteData));
    }

    tournamentReady() {
        if (this.ready === -1) {
            this.dom_start_tournament.addEventListener('click', (e) => {this.queryTournamentRound(e); this.startEventInvite();});
            this.dom_start_tournament.disabled = false;
            this.ready = 1;
        }
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

    endMatch(data) {
        const resultData = {
            type: 'match_result',
            winner: data.win,
            score: data.score,
            winning_score: data.winning_score,
            roomid: data.roomid
        };
        this.main.lobby.socket.send(JSON.stringify(resultData));
        this.queryRoundList();
    }

    startEventInvite() {
        const inviteData = {
            type: 'tournament_event_invite',
            tour_id : this.id
        };
        this.main.lobby.socket.send(JSON.stringify(inviteData));
    }

    tournamentInfos(name, round) {
        const tournamentInfosContainer = document.getElementById('tournament-infos');
        if (tournamentInfosContainer) {
            let content = '';
            if (round === -2) {
                content = `<h3>Tournament - ${name} - Results</h3>`;
            }
            else if (round === -1) {
                this.final = 1;
                content = `<h3>Tournament - ${name} - Round: Final</h3>`;
            }
            else {
                content = `<h3>Tournament - ${name} - Round: ${round}</h3>`;
            }
    
            tournamentInfosContainer.innerHTML = content;
        }
    }    

    displayTournamentMatches(matches) {
        const matchesContainer = document.getElementById('tournament-matches');
        if (matchesContainer) {
            matchesContainer.innerHTML = '';
    
            // group matches by round number
            const matchesByRound = matches.reduce((acc, match) => {
                if (!acc[match.round]) {
                    acc[match.round] = [];
                }
                acc[match.round].push(match);
                return acc;
            }, {});
    
            // sort rounds in reverse to display newer rounds first
            Object.keys(matchesByRound).sort((a, b) => b - a).forEach(round => {
                // Create round element
                const roundElement = document.createElement('div');
                roundElement.setAttribute('data-round-number', round);
                roundElement.innerHTML = `<strong>Round: ${round}</strong>`;
                matchesContainer.appendChild(roundElement);
    
                matchesByRound[round].forEach(match => {
                    // Create match element
                    const matchElement = document.createElement('div');
                    matchElement.className = 'match';
                    matchElement.setAttribute('data-match-id', match.room_id);
                    matchElement.innerHTML = `
                        <p>Match: #${match.match_nbr}</p>
                        <p>Player 1: ${match.player1_name} vs. Player 2: ${match.player2_name}</p>
                        <p>Status: ${match.status}</p>
                    `;
                    // append match element directly after its round's header
                    matchesContainer.appendChild(matchElement);
                });
            });
    
            this.main.lobby.socket.send(JSON.stringify({
                type: 'tournament-player-action',
                id: this.id
            }));
        }
    }    

    displayPlayerAction(matchId) {
        const matchElement = document.querySelector(`[data-match-id="${matchId}"]`);
        if (matchElement) {
            const existingButton = matchElement.querySelector('button');
            if (!existingButton) {
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
    }    

    updateMatchStatus(data) {
        const roomId = data.room_id;
        const newStatus = data.status;

        const matchElement = document.querySelector(`[data-match-id="${roomId}"]`);

        if (matchElement) {
            const statusParagraph = matchElement.querySelectorAll('p')[2];
            statusParagraph.innerHTML = `Status: ${newStatus}`;
        }
    }

    winnerDisplay(data) {
        const winnerName = data.winner;
        const container = document.getElementById('winnerNameDisplay');

        if (container) {
            container.innerHTML = '';

            const winnerMsg = document.createElement('div');
            winnerMsg.classList.add('winnerMessage');
            winnerMsg.textContent = `Tournament Terminated | Winner: ${winnerName}`;

            const congratsMsg = document.createElement('div');
            congratsMsg.classList.add('congratulationsMessage');
            congratsMsg.textContent = 'Congratulations!';

            container.appendChild(winnerMsg);
            container.appendChild(congratsMsg);
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
                            this.game = new Pong(this.main, this.main.lobby, info, this);
                            this.main.load('/pong', () => {
                                this.game.init();
                            });
                            break;
                    }
                }
            },
            error: () => this.main.set_status('Error: Can not join game')
        });
    }

    quitTournament() {
        this.main.lobby.socket.send(JSON.stringify({
            type: 'tournament-quit',
            tour_id: this.id,
        }));
        this.id = -1;
        this.game = null;
        this.ready = -1;
        this.final = 0;
        this.lobby.tournament = null;
        this.main.load('/lobby', () => this.main.lobby.events());
    }

    backToLobby() {
        this.main.load('/lobby', () => this.main.lobby.events());
    }

    inSetup() {
        const parentElement = document.getElementById('tournament-matches');
        if (parentElement) {
            const message = document.createElement('div');
            message.innerHTML = 'Tournament is still in preparation';
            parentElement.appendChild(message);
        }
    }
}