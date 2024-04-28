import {Lobby} from './Lobby.js'
import {Pong} from './Pong.js';
import { localTournament } from './tournamentLocal.js';

export class Tournament {

    constructor(m, id = null) {
        this.main = m;
        this.lobby = m.lobby;
        this.name = ''
        this.id = id;
        this.game = null;
        this.localTournament = null;
        this.userAdded = []
    }

    events() {
        this.main.checkcsrf();
        this.dom_tournamentForm = document.getElementById('tournamentForm');
        if (this.dom_tournamentForm)
            this.dom_tournamentForm.addEventListener('submit', (e) => this.tournamentSubmit(e));
    }

    eventsTwoFA(login) {
        const csrftoken = this.main.getCookie('csrftoken');
    
        if (csrftoken) {
            $.ajax({
                url: '/game/tournament/local/2FAback',
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrftoken,
                },
                data: {
                    'login': login
                },
                success: (response) => {
                    this.id = response.id;
                    const participants = response.participants;
                    participants.forEach(participant => {this.userAdded.push(participant.login)})
                    this.main.history_stack.push('/tournament/local');
                    window.history.pushState({}, '', '/tournament/local');
                    this.main.load('/tournament/local', () => this.eventsLocal());
                },
                error: (xhr) => {
                    this.main.set_status(xhr.responseJSON.error);
                }
            });
        }
    }

    eventsLocal() {
        var userLogin = false;
        
        var startBtn = document.getElementById('startTour');
        startBtn.disabled = true;
        this.checkAdded()
    
        const addPlayerBtn = document.getElementById('addPlayer');
        const playerForm = document.getElementById('playerForm');
        addPlayerBtn.addEventListener('click', () => {
            playerForm.style.display = (playerForm.style.display === 'none' || playerForm.style.display === '' ? 'block' : 'none');
        });

        const passwordField = document.getElementById('passwordField');
        const loginCheckbox = document.getElementById('loginCheckbox');
        loginCheckbox.addEventListener('change', () => {
            passwordField.style.display = loginCheckbox.checked ? 'block' : 'none';
            userLogin = userLogin === false ? true : false;
        });
    
        const submitBtn = document.getElementById('submitBtn');
        submitBtn.addEventListener('click', (event) => {
            event.preventDefault();
            const password = document.getElementById('passwordTour').value;
            const login = document.getElementById('loginTour').value;

            const isLoginTaken = this.userAdded.some(user => user.login === login) || login === this.main.login;

            if (isLoginTaken) {
                this.main.set_status(`The login ${login} is already in use.`);
                return;
            }

            if ((userLogin && password !== "" && login !== "") || (!userLogin && login !== "")) {
                this.addUser(login, password, userLogin);
            } else {
                this.main.set_status('Please fill all required fields');
            }
        });
    }
    
    addUser(login, password, userLogin) {
        const csrftoken = this.main.getCookie('csrftoken');

        const formData = {
            'login': login,
            'password': password,
            'userLogin': userLogin.toString() ,
            'id': this.id
        }

        if (csrftoken) {
            $.ajax({
                url: '/game/tournament/local/adduser/',
                method: 'POST',
                data: JSON.stringify(formData),
                headers: {
                    'X-CSRFToken': csrftoken,
                },
                success: (response) => {
                    if (response.success == 'twofa') {
                        this.main.history_stack.push('/twofa');
                        window.history.pushState({}, '', '/twofa');
                        this.main.load('/twofa', () => this.main.twofa.eventsTour(this.id, response.login, response.name, response.email));
                    } else {
                        this.userAdded.push(response.login);
                        this.main.history_stack.push('/tournament/local');
                        window.history.pushState({}, '', '/tournament/local');
                        this.main.load('/tournament/local', () => this.eventsLocal());
                    }
                },
                error: (xhr) => {
                    this.main.set_status(xhr.responseJSON.error);
                }
            });
        }
    }

    checkAdded() {
        const playerStack = document.getElementById('player-stack');
        if (playerStack && this.userAdded.length > 0) {
            playerStack.innerHTML = '<h3>Current Players</h3>';
    
            this.userAdded.forEach(user => {
                let playerEntry = document.createElement('div');
                playerEntry.textContent = user;
                playerStack.appendChild(playerEntry);
            });
    
            var startBtn = document.getElementById('startTour');
            if (startBtn) {
                startBtn.disabled = false;
                startBtn.addEventListener('click', () => {
                    this.startTournament();
                });
            }
        }
    }    

    startTournament() {
        const csrftoken = this.main.getCookie('csrftoken');
    
        const formData = {
            id: this.id
        };
    
        if (csrftoken) {
            $.ajax({
                url: '/game/tournament/local/verify/',
                method: 'POST',
                data: JSON.stringify(formData),
                headers: {
                    'X-CSRFToken': csrftoken,
                },
                success: (response) => {
                    
                    this.localTournament = new localTournament(this.main, response.id, this);
                    this.main.history_stack.push('/tournament/local/start');
                    window.history.pushState({}, '', '/tournament/local/start');
                    this.main.load('/tournament/local/start', () => this.localTournament.getMatch());
                },
                error: (xhr) => {
                    this.main.set_status(xhr.responseJSON.error);
                    this.quitTournament('force');
                }
            });
        }
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
                    this.name = response.name;
                    this.id = response.id;
                    this.main.history_stack.push('/tournament/local');
                    window.history.pushState({}, '', '/tournament/local');
                    this.main.load('/tournament/local', () => this.eventsLocal(response.name));
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
            this.history_stack.push('/login');
            window.history.pushState({page: '/login'}, '', '/login');
            this.main.load('/pages/login', () => this.main.log_in.events());
        }        
    }

    quitTournament(force) {
        if (force) {
            this.main.lobby.socket.send(JSON.stringify({
                type: 'tournament-quit',
                tour_id: this.id,
            }));
            this.id = -1;
            this.game = null;
            this.lobby.tournament = null;
            this.main.history_stack.push('/');
            window.history.pushState({}, '', '/');
            this.main.load('/lobby', () => this.main.lobby.events());
        } else {
            const confirmQuit = confirm("Warning: Quitting the tournament will end tournament for every player. Are you sure?");
            if (confirmQuit) {
                    this.main.lobby.socket.send(JSON.stringify({
                        type: 'tournament-quit',
                        tour_id: this.id,
                    }));
                    this.id = -1;
                    this.game = null;
                    this.lobby.tournament = null;
                    this.main.history_stack.push('/');
                    window.history.pushState({}, '', '/');
                    this.main.load('/lobby', () => this.main.lobby.events());
            }
        }
    }

    backToLobby() {
        if (this.localTournament && this.localTournament.game) {
            this.localTournament.game.stop();
            this.localTournament.game.preventWinBox = true;
        }
        this.main.history_stack.push('/');
        window.history.pushState({}, '', '/');
        this.main.load('/lobby', () => this.main.lobby.events());
    }

    localBack() {
        this.localTournament = new localTournament(this.main, this.id, this);
        this.main.load('/tournament/local/start', () => this.localTournament.getMatch());
    }
}