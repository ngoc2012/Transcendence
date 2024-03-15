import {Lobby} from './Lobby.js'
import {Pong} from './Pong.js';

export class Tournament {

    constructor(m) {
        this.main = m;
        this.lobby = m.lobby;
        this.id = -1;
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
                this.main.set_status('Tournament created successfully');
                this.main.history_stack.push('/');
                window.history.pushState({}, '', '/');
                this.main.load('/tournament/lobby', () => this.eventsLobby());
            },
            error: () => {
                this.main.set_status('Error: Could not create tournament');
            }
        });
    }

    userList(users) {
        const playersList = document.getElementById('players-list');
        if (playersList) {
            playersList.innerHTML = '';
            users.forEach((user) => {
                if (user.login === this.main.login) {
                    return;
                }
        
                const li = document.createElement('li');
                li.textContent = `${user.login}`;
                
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
        this.main.history_stack.push(tournamentUrl);
        window.history.pushState({}, '', tournamentUrl);
        this.main.load(tournamentUrl, () => this.eventsStart());
        const data = {
            type: 'tournament_rounds',
            id: this.id
        };
        this.main.lobby.socket.send(JSON.stringify(data));
    }

    queryRoundList() {
        const tournamentUrl = `/tournament/${this.id}`;
        this.main.history_stack.push(tournamentUrl);
        window.history.pushState({}, '', tournamentUrl);
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

    eventInvite(tourID) {
        this.id = tourID;
        this.queryRoundList();
    }

    infoRequest(tourId) {
        this.main.lobby.socket.send(JSON.stringify({
            type: 'tournament-info-request',
            id: this.id
        }));
    }

    tournamentInfos(name, round) {
        const tournamentInfosContainer = document.getElementById('tournament-infos');
        if (tournamentInfosContainer) {
            tournamentInfosContainer.innerHTML = '';
            
            if (round === -2) {
                tournamentInfosContainer.innerHTML = `
                    <h3>Tournament - ${name} - Results</h3>
                `;
            }
            else if (round === -1) {
                this.final = 1;
                tournamentInfosContainer.innerHTML = `
                    <h3>Tournament - ${name} - Round: Final</h3>
                `;
            }
            else {
                tournamentInfosContainer.innerHTML = `
                    <h3>Tournament - ${name} - Round: ${round}</h3>
                `;
            }
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

    scoreDisplay(matches) {
        const container = document.getElementById('tournament-matches');
        
        if (container) {
            container.innerHTML = '';

            const matchesByRound = matches.reduce((acc, match) => {
                // If the round doesn't exist in the accumulator, add it
                if (!acc[match.round_number]) {
                    acc[match.round_number] = [];
                }
                // Add the match to the round
                acc[match.round_number].push(match);
                return acc;
            }, {});

            Object.keys(matchesByRound).forEach(round => {
                // Create a section for each round
                const roundSection = document.createElement('div');
                roundSection.innerHTML = `<h3>Round ${round}</h3>`;
                const list = document.createElement('ul');

                matchesByRound[round].forEach(match => {
                    // Create list item for each match in the round
                    const item = document.createElement('li');
                    item.textContent = `${match.player1_login} (${match.player1_score}) vs ${match.player2_login} (${match.player2_score}) - Winner: ${match.winner_login}`;
                    list.appendChild(item);
                });

                roundSection.appendChild(list);
                container.appendChild(roundSection);
            });
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
        this.main.history_stack.push('/');
        window.history.pushState({}, '', '/');
        this.main.load('/lobby', () => this.main.lobby.events());
    }

    backToLobby() {
        // url = `/tournament/${this.id}`
        // this.main.history_stack.push(url);
        // window.history.pushState({}, '', url);
        this.main.history_stack.push('/');
        window.history.pushState({}, '', '/');
        this.main.load('/lobby', () => this.main.lobby.events());
    }
}