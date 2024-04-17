import {Lobby} from './Lobby.js'
import {Pong} from './Pong.js';
import { localTournament } from './tournamentLocal.js';

export class Tournament {

    constructor(m, id = null) {
        this.main = m;
        this.lobby = m.lobby;
        this.id = id;
        this.game = null;
        this.ready = -1;
        this.final = 0;
        this.localTournament = null;
    }

    events() {
        this.main.checkcsrf();
        this.dom_tournamentForm = document.getElementById('tournamentForm');
        if (this.dom_tournamentForm)
            this.dom_tournamentForm.addEventListener('submit', (e) => this.tournamentSubmit(e));
    }

    eventsLocal() {
        document.getElementById('playerCount').addEventListener('change', (event) => {
            const numberOfPlayers = event.target.value;
            const form = document.getElementById('playerForm');
            form.innerHTML = '';
        
            // First player input, always visible and not editable
            const mainPlayerInput = document.createElement('input');
            mainPlayerInput.type = 'text';
            mainPlayerInput.name = 'player1';
            mainPlayerInput.placeholder = `${this.main.login}`;
            mainPlayerInput.readOnly = true;
            mainPlayerInput.classList.add('ignore');
            form.appendChild(mainPlayerInput);
            form.appendChild(document.createElement('br'));
        
            // Create inputs, checkboxes, and password fields for other players
            for (let i = 2; i <= numberOfPlayers; i++) {
                const input = document.createElement('input');
                input.type = 'text';
                input.name = 'player' + i;
                input.placeholder = 'Player ' + i + ' Nickname';
        
                const checkbox = document.createElement('input');
                checkbox.type = 'checkbox';
        
                const loginLabel = document.createElement('label');
                loginLabel.textContent = 'Log in';
                loginLabel.style.marginLeft = '5px';
                loginLabel.appendChild(checkbox);
        
                const passwordInput = document.createElement('input');
                passwordInput.type = 'password';
                passwordInput.name = 'password' + i;
                passwordInput.placeholder = 'Password for Player ' + i;
                passwordInput.style.display = 'none';
                passwordInput.style.marginLeft = '5px';
        
                // Display password field when checkbox is checked
                checkbox.addEventListener('change', function () {
                    passwordInput.style.display = this.checked ? 'inline' : 'none';
                });
        
                form.appendChild(input);
                form.appendChild(loginLabel);
                form.appendChild(passwordInput);
                form.appendChild(document.createElement('br'));
            }
        
            // Submit button
            if (numberOfPlayers > 0) {
                const submitButton = document.createElement('button');
                submitButton.type = 'submit';
                submitButton.textContent = 'Submit';
                form.appendChild(submitButton);
            }
        });
        
        document.getElementById('playerForm').addEventListener('submit', (event) => {
            event.preventDefault();
            const form = event.currentTarget;
            const inputs = form.querySelectorAll('input[type="text"]:not(.ignore)');
            const checkboxes = form.querySelectorAll('input[type="checkbox"]');
            let allFilled = true;
            let playerCredentials = [];
        
            inputs.forEach((input, index) => {
                if (input.value === '') {
                    allFilled = false;
                } else {
                    const checkbox = checkboxes[index];
                    if (checkbox && checkbox.checked) {
                        const password = form.querySelector(`input[name="password${index + 2}"]`).value;
                        playerCredentials.push({ nickname: input.value, password: password });
                    } else {
                        playerCredentials.push({ nickname: input.value });
                    }
                }
            });
        
            if (!allFilled) {
                alert('Please fill out all player nicknames.');
            } else {
                var csrftoken = this.main.getCookie('csrftoken');
                var formData = JSON.stringify({ players: playerCredentials, id: this.id });
        
                if (csrftoken) {
                    $.ajax({
                        url: '/game/tournament/local/verify/',
                        method: 'POST',
                        data: formData,
                        headers: {
                            'X-CSRFToken': csrftoken,
                        },
                        success: (response) => {
                            this.main.set_status = '';
                            this.localTournament = new localTournament(this.main, playerCredentials.map(p => p.nickname), this.id, this);
                            this.main.load('/tournament/local/start', () => this.localTournament.getMatch());
                        },
                        error: (xhr) => {
                            this.main.set_status(xhr.responseJSON.error);
                        }
                    });
                }
            }
        });              
    }
    
    tournamentSubmit(event) {
        event.preventDefault();

        let formData = {
            name: document.getElementById('tname').value,
            game: 'pong',
            login: this.main.login,
            local: 'true'
        };

        var csrftoken = this.main.getCookie('csrftoken');

        if (csrftoken) {
            $.ajax({
                url: '/tournament/new/',
                method: 'POST',
                data: formData,
                headers: {
                    'X-CSRFToken': csrftoken,
                },
                success: (response) => {
                    this.id = response.id;
                        this.main.load('/tournament/local', () => this.eventsLocal());
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
        } else {
            this.main.load('/pages/login', () => this.main.log_in.events());
        }        
    }

    quitTournament() {
        const confirmQuit = confirm("Warning: Quitting the tournament will end tournament for every player. Are you sure?");
        
        if (confirmQuit) {
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
    }

    backToLobby() {
        this.main.load('/lobby', () => this.main.lobby.events());
    }

    localBack() {
        this.localTournament = new localTournament(this.main, null, this.id, this);
        this.main.load('/tournament/local/start', () => this.localTournament.getMatch());
    }
}