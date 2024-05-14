import {Draw} from './Draw.js'

function waitForWebSocketClose(websocket) {
    return new Promise((resolve) => {
        if (websocket.readyState === WebSocket.CLOSED) {
            resolve(); // WebSocket is already closed
        } else {
            websocket.addEventListener('close', function(event) {
                resolve(); // WebSocket is closed
            });
        }
    });
}

async function closeSocket(websocket) {
    if (websocket instanceof WebSocket)
    {
        websocket.close();
        await waitForWebSocketClose(websocket);
    }
}

function keydown_loop(pong, i, direction)
{
    pong.set_state(i, direction);
    if (pong.players[i][direction]) {
        setTimeout(() => {keydown_loop(pong, i, direction);}, pong.delay + 0.01);
    }
}

function keydown(pong, i, direction)
{
    if (pong.players[i][direction])
        return;
    pong.players[i][direction] = true;
    keydown_loop(pong, i, direction);
}

export class Pong
{
    constructor(m, l, r, t = null, localTournament = null, localTour = false, id = null) {
        this.main = m;
        this.lobby = l;
        this.room = r;
        this.connected = false;
        this.power_play = false;
        this.draw = new Draw(this);
        this.keyboard_layout = "";
        this.players = [{
            'id': this.room.player_id,
            'sk': -1,
            'up': false,
            'down': false,
            'left': false,
            'right': false
        }];
        this.tournament = t;
        this.localTournament = localTournament;
        this.localTour = localTour;
        this.id = id;
        this.preventWinBox = true;
        this.pmBox = false;
        this.joined = false;
        this.playerLocal = false;
        this.touchStart = [0, 0];
        this.touchEnd = [0, 0];
        this.set_state_available = true;
        this.delay = 40;

    }

    reset_ratio() {
        let width = window.innerWidth - 2;
        if (width < this.room.data.WIDTH)
        {
            this.ctx.canvas.width = width;
            this.ctx.canvas.height = width * this.room.data.HEIGHT / this.room.data.WIDTH;
            this.draw.ratio = width / this.room.data.WIDTH;
        }
    }

	init(isPopState) {
        if (!isPopState)
            window.history.pushState({page: '/pong/' + this.room.id}, '', '/pong/' + this.room.id);

        this.dom_game_name = document.getElementById("game_name");
        if (this.dom_game_name && this.room && this.room.name)
            this.dom_game_name.innerHTML = this.room.name;
        else
            return;
        this.dom_team0 = document.getElementById("team0");
        this.dom_team1 = document.getElementById("team1");
        this.dom_score0 = document.getElementById("score0");
        this.dom_score1 = document.getElementById("score1");

		this.canvas = document.getElementById('pongCanvas');
        if (this.canvas)
		    this.ctx = this.canvas.getContext('2d');
        else
            return;
        this.ctx.canvas.width  = this.room.data.WIDTH;
        this.ctx.canvas.height = this.room.data.HEIGHT;
        this.reset_ratio();

        window.addEventListener('resize', () => {
            this.reset_ratio();
            this.draw.execute(this.draw.data);
            this.draw.update_3D(this.draw.data);
        });

        this.pongThreeJS = document.getElementById('pongThreeJS');

        if (!this.localTour) {
            this.dom_start = document.getElementById("start");
            this.dom_start.addEventListener("click", () => this.start());
            this.dom_quit = document.getElementById("quit");
            this.dom_quit.addEventListener("click", () => this.quit());
        }

		this.dom_angle = document.getElementById("angle");
		this.dom_ratio = document.getElementById("ratio");
		this.dom_near = document.getElementById("near");
		this.dom_far = document.getElementById("far");
		this.dom_pos_x = document.getElementById("pos_x");
		this.dom_pos_y = document.getElementById("pos_y");
		this.dom_pos_z = document.getElementById("pos_z");
		this.dom_center_x = document.getElementById("center_x");
		this.dom_center_y = document.getElementById("center_y");
		this.dom_center_z = document.getElementById("center_z");
		this.dom_amb_dens = document.getElementById("amb_dens");
		this.dom_dir_dens = document.getElementById("dir_dens");
		this.dom_light_x = document.getElementById("light_x");
		this.dom_light_y = document.getElementById("light_y");
		this.dom_light_z = document.getElementById("light_z");
        this.dom_toggle_display = document.getElementById('toggle_display');
        this.dom_toggle_display_board = document.getElementById('toggle_display_board');
        this.dom_display_board = document.getElementById('display_board');

        if (!this.localTour) {
            this.dom_local_player = document.getElementById('local_player');
            this.dom_toggle_AI = document.getElementById("toggle_AI");
            this.dom_power_play = document.getElementById("power_play");
            this.dom_new_local_player = document.getElementById('new_local_player');
            this.dom_login_local = document.getElementById('login_local');
            this.dom_password_local = document.getElementById('password_local');
            this.dom_join_local = document.getElementById('join_local');
            this.dom_close_local = document.getElementById('close_local');
            this.dom_keyboard_layout = document.getElementById('keyboard_layout');
            document.getElementById('login_local').addEventListener('keydown', function(event) {
                event.stopPropagation();
            });
            document.getElementById('password_local').addEventListener('keydown', function(event) {
                event.stopPropagation();
            });
            document.getElementById('keyboard_layout').addEventListener('keydown', function(event) {
                event.stopPropagation();
            });
        }
        else {
            this.dom_quit_tournament = document.getElementById('quit-tournament');
            this.dom_quit_tournament.addEventListener('click', () => this.tournament.quitTournament());
        }

        document.addEventListener('keydown', (event) => {
            if (event.key === ' ') {
                event.stopPropagation();
                if (this.pmBox)
                    return;
                if (this.localTournament) {
                    this.startLocal();
                } else {
                    this.start();
                }
            }
        });

        if (!this.localTour) {
            document.addEventListener("touchstart", (event) => {
                var touch = event.touches[0];
                this.touchStart[0] = touch.clientX;
                this.touchStart[1] = touch.clientY;
            });
            document.addEventListener("touchend", (event) => {
                var touch = event.touches[0];
                this.touchEnd[0] = touch.clientX;
                this.touchEnd[1] = touch.clientY;
                let nx = Math.floor(Math.abs(this.touchEnd[0] - this.touchStart[0]) / (this.ctx.canvas.width / 20));
                let ny = Math.floor(Math.abs(this.touchEnd[1] - this.touchStart[1]) / (this.ctx.canvas.height / 10));
                if (this.touchEnd[0] - this.touchStart[0] < 0)
                {
                    for (let i = 0; i < nx; i++)
                        this.set_state(0, "left");
                }
                else
                {
                    for (let i = 0; i < nx; i++)
                        this.set_state(0, "right");
                }
                if (this.touchEnd[1] - this.touchStart[1] < 0)
                {
                    for (let i = 0; i < ny; i++)
                        this.set_state(0, "up");
                }
                else
                {
                    for (let i = 0; i < ny; i++)
                        this.set_state(0, "down");
                }
            });
            document.addEventListener('keyup', (event) => {
                if (["w", "s"].includes(event.key)) {
                    event.stopPropagation();
                }
                switch (event.key) {
                    case 'w':
                        this.players[0].up = false;
                        break;
                    case 's':
                        this.players[0].down = false;
                        break;
                    case 'a':
                        this.players[0].left = false;
                        break;
                    case 'd':
                        this.players[0].right = false;
                        break;
                    case 'Tab':
                        if (this.power_play)
                            this.set_state(0, "side");
                        break;
                    case 'Control':
                        this.set_state(0, "server");
                        break;
                }
                let commands = ['up', 'down', 'left', 'right'];
                if (event.key && event.key.length === 1)
                {
                    let index = this.keyboard_layout.indexOf(event.key);
                    if (index >= 0)
                    {
                        let i_player = Math.floor(index / 4) + 1;
                        index = index % 4;
                        if (index < 2 || (index >= 2 && this.power_play))
                            this.players[i_player][commands[index]] = false;
                    }

                }
            });
            document.addEventListener('keydown', (event) => {
                // document.addEventListener('keydown', (event) => {
                //     if (["w", "s"].includes(event.key)) {
                //         event.preventDefault();
                //     }
                // })
                if (["w", "s"].includes(event.key)) {
                    event.stopPropagation();
                }
                switch (event.key) {
                    case 'w':
                        keydown(this, 0, 'up');
                        break;
                    case 's':
                        keydown(this, 0, 'down');
                        break;
                    case 'a':
                        if (this.power_play)
                            keydown(this, 0, 'left');
                        break;
                    case 'd':
                        if (this.power_play)
                            keydown(this, 0, 'right');
                        break;
                    case 'Tab':
                        if (this.power_play)
                            this.set_state(0, "side");
                        break;
                    case 'Control':
                        this.set_state(0, "server");
                        break;
                }

                let commands = ['up', 'down', 'left', 'right'];
                if (event.key && event.key.length === 1)
                {
                    let index = this.keyboard_layout.indexOf(event.key);
                    if (index >= 0)
                    {
                        let i_player = Math.floor(index / 4) + 1;
                        index = index % 4;
                        if (index < 2 || (index >= 2 && this.power_play))
                            keydown(this, i_player, commands[index]);
                    }

                }
            });
            this.preMatchBox(this.main.login)
        } else {
            document.addEventListener('keyup', (event) => {
                if (["w", "s"].includes(event.key)) {
                    event.stopPropagation();
                }
                switch (event.key) {
                    case 'w':
                        this.players[0].up = false;
                        break;
                    case 's':
                        this.players[0].down = false;
                        break;
                }
                let commands = ['up', 'down', 'left', 'right'];
                if (event.key && event.key.length === 1)
                {
                    let index = this.keyboard_layout.indexOf(event.key);
                    if (index >= 0)
                    {
                        let i_player = Math.floor(index / 4) + 1;
                        index = index % 4;
                        if (index < 2 || (index >= 2 && this.power_play))
                            this.players[i_player][commands[index]] = false;
                    }

                }
            });
            document.addEventListener('keydown', (event) => {
                switch (event.key) {
                    case 'w':
                        keydown(this, 0, 'up');
                        break;
                    case 's':
                        keydown(this, 0, 'down');
                        break;
                }

                let commands = ['up', 'down', 'left', 'right'];
                if (event.key && event.key.length === 1)
                {
                    let index = this.keyboard_layout.indexOf(event.key);
                    if (index >= 0)
                    {
                        let i_player = Math.floor(index / 4) + 1;
                        index = index % 4;
                        if (index < 2 || (index >= 2 && this.power_play))
                            keydown(this, i_player, commands[index]);
                    }

                }
            });
        }

        if (!this.localTour) {
            this.dom_toggle_AI.addEventListener('click', () => {
                this.set_state(0, 'ai_player');
                this.players[0].sk.send('teams');
            });
            this.dom_power_play.addEventListener('click', () => {this.set_state(0, 'power')});
            this.dom_toggle_display.addEventListener('click', () => {this.toggle_display()});
            this.dom_toggle_display_board.addEventListener('click', () => {this.toggle_display_board()});
        }
        this.connect(0);

        this.draw.init();
        this.draw.update_camera();

        this.dom_angle.addEventListener('input', this.draw.update_camera.bind(this.draw));
		this.dom_ratio.addEventListener('input', this.draw.update_camera.bind(this.draw));
		this.dom_near.addEventListener('input', this.draw.update_camera.bind(this.draw));
		this.dom_far.addEventListener('input', this.draw.update_camera.bind(this.draw));
		this.dom_pos_x.addEventListener('input', this.draw.update_camera.bind(this.draw));
		this.dom_pos_y.addEventListener('input', this.draw.update_camera.bind(this.draw));
		this.dom_pos_z.addEventListener('input', this.draw.update_camera.bind(this.draw));
		this.dom_center_x.addEventListener('input', this.draw.update_camera.bind(this.draw));
		this.dom_center_y.addEventListener('input', this.draw.update_camera.bind(this.draw));
		this.dom_center_z.addEventListener('input', this.draw.update_camera.bind(this.draw));
		this.dom_amb_dens.addEventListener('input', this.draw.update_camera.bind(this.draw));
		this.dom_dir_dens.addEventListener('input', this.draw.update_camera.bind(this.draw));
		this.dom_light_x.addEventListener('input', this.draw.update_camera.bind(this.draw));
		this.dom_light_y.addEventListener('input', this.draw.update_camera.bind(this.draw));
		this.dom_light_z.addEventListener('input', this.draw.update_camera.bind(this.draw));

        if (!this.localTour) {
            this.dom_new_local_player.addEventListener('click', () => {
                this.dom_local_player.style.display = 'block';
            });
            this.dom_close_local.addEventListener('click', () => {
                this.dom_local_player.style.display = 'none';
            });
            this.dom_join_local.addEventListener('click', () => {
                this.local_player_login();
            });
        }

        if (this.localTour) {
            this.player1 = this.localTournament.player1;
            this.player2 = this.localTournament.player2;
            var csrftoken = this.main.getCookie('csrftoken');
            $.ajax({
                url: '/game/tournament/local/join/setup/',
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrftoken,
                },
                data: {
                    "game_id": this.room.id,
                    "player2": this.player2
                },
                success: (info) => {
                    if (typeof info === 'string')
                        this.main.set_status(info, false);
                    else
                    {
                        this.players.push({
                            'id': info.player_id,
                            'sk': -1
                        });
                        let i = this.players.length - 1;
                        this.connect(i);
                        if (this.players[i].sk !== -1)
                        {
                            this.keyboard_layout += 'ikjl';
                        }
                        this.preMatchBox(this.localTournament.player1, this.localTournament.player2);
                    }
                },
                error: (jqXHR) => {
                    this.main.set_status('Error: Can not join game', false)
                    if (jqXHR.status === 401 && jqXHR.responseText === "Unauthorized - Token expired") {
                        this.main.clearClient();
                        this.main.load('/pages/login', () => this.main.log_in.events());
                        return;
                    }
                }
            });
        }

        if (this.joined) {
            this.dom_toggle_AI.style.display = "none";
            this.dom_local_player.style.display = "none";
            // this.dom_power_play.style.display = "none";
            this.dom_new_local_player.style.display = "none";
            this.dom_login_local.style.display = "none";
            this.dom_password_local.style.display = "none";
            this.dom_join_local.style.display = "none";
            this.dom_close_local.style.display = "none";
            this.dom_keyboard_layout.style.display = "none";
            this.dom_toggle_display.style.display = 'none';
        }
	}

    toggle_display() {
        if (this.canvas.style.display === 'none') {
            this.canvas.style.display = 'block';
            this.pongThreeJS.style.display = 'none';
            this.dom_toggle_display_board.style.display = 'none';
            this.dom_display_board.style.display = 'none';
            this.dom_toggle_display_board.innerHTML = "Show display board";
            this.dom_toggle_display.innerHTML = "3D";
        } else {
            this.canvas.style.display = 'none';
            this.pongThreeJS.style.display = 'block';
            this.dom_toggle_display_board.style.display = 'block';
            this.dom_toggle_display.innerHTML = "2D";
        }
    }

    charExists(searchString, mainString) {
        for (let i = 0; i < searchString.length; i++) {
          const char = searchString[i];
          if (mainString.indexOf(char) >= 0) {
            return true;
          }
        }
        return false;
    }

    isAlphabetic(str) {
        const regex = /^[a-zA-Z]+$/;this.playerLocal
        return regex.test(str);
    }

    local_player_login() {
        if (this.players.length > 1)
        {
            this.main.set_status('Too many players', false);
            return;
        }
        if (this.dom_login_local.value === '' || this.dom_password_local.value === '')
        {
            this.main.set_status('Field must not be empty', false);
            return;
        }
        if (this.dom_keyboard_layout.value.length !== 4)
        {
            this.main.set_status('Keyboard layout must be 4 characters', false);
            return;
        }
        if (this.charExists(this.dom_keyboard_layout.value, this.keyboard_layout))
        {
            this.main.set_status('Keyboard layout must not contain already used1` characters', false);
            return;
        }
        if (this.isAlphabetic(this.dom_keyboard_layout.value) === false)
        {
            this.main.set_status('Keyboard layout must contain only alphabetic characters', false);
            return;
        }
        let csrftoken = this.main.getCookie('csrftoken');
        $.ajax({
            url: '/auth_view/',
            method: 'POST',
            headers: {
                'X-CSRFToken': csrftoken,
            },
            data: {
                "login": this.dom_login_local.value,
                "password": this.dom_password_local.value,
            },
            success: (info) => {
                if (typeof info === 'string')
                    this.main.set_status(info, false);
                else
                    this.join_local_player(info);
            },
            error: (xhr, jqXHR) => {
                if (xhr.responseJSON && xhr.responseJSON.error) {
                    this.main.set_status(xhr.responseJSON.error, false);
                } else {
                    this.main.set_status('An error occurred during the request.', false);
                }
                if (jqXHR.status === 401 && jqXHR.responseText === "Unauthorized - Token expired") {
                    this.main.clearClient();
					this.main.load('/pages/login', () => this.main.log_in.events());
					return;
				}
            }
        });
    }

    join_local_player(player) {
        let csrftoken = this.main.getCookie('csrftoken');
        $.ajax({
            url: '/game/join',
            method: 'POST',
            headers: {
                'X-CSRFToken': csrftoken,
            },
            data: {
                'login': player.login,
                "game_id": this.room.id
            },
            success: (info) => {
                if (typeof info === 'string')
                    this.main.set_status(info, false);
                else
                {
                    this.playerLocal = true;
                    this.players.push({
                        'id': info.player_id,
                        'sk': -1
                    });
                    let i = this.players.length - 1;
                    this.connect(i);
                    if (this.players[i].sk !== -1)
                    {
                        this.dom_local_player.style.display = 'none';
                        this.keyboard_layout += this.dom_keyboard_layout.value.toLowerCase();
                    }
                }
            },
            error: (jqXHR) => {
                if (jqXHR.status === 401 && jqXHR.responseText === "Unauthorized - Token expired") {
                    this.main.clearClient();
					this.main.load('/pages/login', () => this.main.log_in.events());
					return;
				}
                this.main.set_status('Error: Can not join game', false)
            }
        });
    }

    set_power_play(val) {
        this.power_play = val;
        if (val)
            this.dom_power_play.innerHTML = "Power play off";
        else
            this.dom_power_play.innerHTML = "Power play on";
    }

    set_ai_player(val) {
        if (val) {
            this.dom_toggle_AI.innerHTML = "AI player off";
            this.player2 = 'ai'
        }
        else
            this.dom_toggle_AI.innerHTML = "AI player on";
    }

    toggle_display_board() {
        if (this.dom_display_board.style.display === 'none') {
            this.dom_display_board.style.display = 'block';
            this.dom_toggle_display_board.innerHTML = "Hide display board";
        } else {
            this.dom_display_board.style.display = 'none';
            this.dom_toggle_display_board.innerHTML = "Show display board";
        }
    }

    start() {
        if (this.players[0].sk !== -1)
            this.players[0].sk.send('start');
        if (this.playerLocal) {
            if (this.players[1].sk !== -1)
                this.players[1].sk.send('start');
        }
    }

    startLocal() {
        if (!this.pmBox) {
            if (this.players[0].sk !== -1)
                this.players[0].sk.send('start');
            if (this.players[1]  && this.players[1].sk && this.players[1].sk !== -1)
                this.players[1].sk.send('start');
        }
    }

    close_room() {
        this.players.forEach((p, i) => {
            this.set_state(i, 'quit');
            if (p.sk instanceof WebSocket)
            {
                closeSocket(p.sk).then(() => {
                    p.sk = -1;
                });
            }
        });
    }

    quit() {
        this.close_room();
        this.main.load('/lobby', () => this.lobby.events());
    }

    stop() {
        this.players.forEach((p, i) => {
            this.set_state(i, 'stop');
            if (p.sk instanceof WebSocket)
            {
                closeSocket(p.sk).then(() => {
                    p.sk = -1;
                });
            }
        });
    }

    connect(i) {
        this.players[i].sk = new WebSocket(
            'wss://'
            + window.location.host
            + '/ws/pong/'
            + this.room.id
            + '/'
            + this.players[i].id
            + '/'
        );

        if (i !== 0)
            return;

        this.players[i].sk.onopen = (e) => {
            if (this.id) {
                this.players[i].sk.send('tour_id:' + this.id);
            }
        };

        this.players[i].sk.onmessage = (e) => {
            if (!('data' in e))
                return;
            let data = JSON.parse(e.data);
            if ('win' in data) {
                this.stop();
                this.preventWinBox = false;
                this.winnerBox(data);
            }
            else if ('score' in data)
            {
                this.dom_score0.innerHTML = data.score[0];
                this.dom_score1.innerHTML = data.score[1];
            }
            else if ('team0' in data)
            {
                this.dom_team0.innerHTML = "";
                data.team0.forEach((p) => {
                    if (this.localTour) {
                        let new_p = document.createTextNode(this.player1);
                        this.dom_team0.appendChild(new_p);
                    } else {
                        let new_p = document.createTextNode(p);
                        this.dom_team0.appendChild(new_p);
                        this.player1 = p;
                    }
                });
                this.dom_team1.innerHTML = "";
                let new_p1 = document.createTextNode("Waiting for opponent");
                this.dom_team1.appendChild(new_p1);
                data.team1.forEach((p) => {
                    let new_p = document.createTextNode(p);
                    if (this.localTour) {
                        this.dom_team1.innerHTML = "";
                        let new_p = document.createTextNode(this.player2);
                        this.dom_team1.appendChild(new_p);
                    } else {
                        this.dom_team1.innerHTML = "";
                        let new_p = document.createTextNode(p);
                        this.dom_team1.appendChild(new_p);
                        this.player2 = p;
                    }
                });
            }
            else
            {
                if (!this.localTour) {
                    if ('power_play' in data)
                        this.set_power_play(data.power_play);
                    if ('ai_player' in data)
                        this.set_ai_player(data.ai_player);
                }
                this.draw.update(data);
                this.draw.execute(data);
            }
        };
    }

    set_state(i, e) {
        if (this.players[i].sk !== -1 && this.players[i].sk.readyState === 1) {
            this.players[i].sk.send(e);
        }
    }

    preMatchBox(player1, player2) {
        this.pmBox = true;

        let existingBackdrop = document.getElementById('backdrop');
        if (existingBackdrop) {
            document.body.removeChild(existingBackdrop);
        }

        let existingMatchBox = document.getElementById('matchBox');
        if (existingMatchBox) {
            document.body.removeChild(existingMatchBox);
        }

        let canvas = document.getElementById('pongCanvas');
        if (canvas) {
            canvas.style.filter = '';
        }

        canvas.style.filter = 'blur(8px)';

        let backdrop = document.createElement('div');
        backdrop.setAttribute('id', 'backdrop');
        backdrop.style.cssText = 'position: fixed; top: 0; left: 0; width: 100%; height: 100%; background-color: rgba(51, 51, 51, 0.6); z-index: 99;';
        document.body.appendChild(backdrop);

        let matchBox = document.createElement('div');
        matchBox.setAttribute('id', 'matchBox');
        matchBox.style.cssText = 'position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%); padding: 20px; background-color: #ffffff7a; border: 2px solid #ffffff; text-align: center; z-index: 10000; border-radius: 10px;';
        document.body.appendChild(matchBox);

        const leftbar = document.getElementById('left-sidebar');
        leftbar.style.cssText += "z-index: 98;"
        const mobilebar = document.getElementById('mobile-sidebar');
        mobilebar.style.cssText += "z-index: 98;"
        const togglebar = document.getElementById('toggle-sidebar');
        togglebar.style.cssText += "z-index: 98;"

        let matchText = document.createElement('p');
        matchText.textContent = 'Match can start whenever you are ready!';
        matchText.style.cssText = 'font-family: "Poppins", sans-serif; font-weight: 400; font-style: normal; color: white;';
        matchBox.appendChild(matchText);

        let instruct1 = document.createElement('p');
        instruct1.textContent = `${player1} controls: 'w' = up, 's' = down`;
        instruct1.style.cssText = 'font-family: "Poppins", sans-serif; font-weight: 400; font-style: normal; color: white;';
        matchBox.appendChild(instruct1);

        if (player2) {
            let instruct2 = document.createElement('p');
            instruct2.textContent = `${player2} controls: 'i' = up, 'k' = down`;
            instruct2.style.cssText = 'font-family: "Poppins", sans-serif; font-weight: 400; font-style: normal; color: white;';
            matchBox.appendChild(instruct2);
        }

        let instruct3 = document.createElement('p');
        instruct3.textContent = 'Press \'space\' to launch the ball';
        instruct3.style.cssText = 'font-family: "Poppins", sans-serif; font-weight: 400; font-style: normal; color: white;';
        matchBox.appendChild(instruct3);

        let startButton = document.createElement('button');
        startButton.textContent = 'Start';
        startButton.classList.add('btn', 'btn-primary');
        startButton.onclick = () => {
            canvas.style.filter = '';
            const leftbar = document.getElementById('left-sidebar');
            leftbar.style.cssText += "z-index: 100;"
            const mobilebar = document.getElementById('mobile-sidebar');
            mobilebar.style.cssText += "z-index: 100;"
            const togglebar = document.getElementById('toggle-sidebar');
            togglebar.style.cssText += "z-index: 100;"
            document.body.removeChild(backdrop);
            document.body.removeChild(matchBox);
            this.pmBox = false;
        };
        matchBox.appendChild(startButton);
    }


    winnerBox(data) {
        if (this.preventWinBox) return;

        if (this.localTournament) {
            this.localTournament.sendResult(data.score[0], data.score[1], this.room.id);
        }

        let backdrop = document.createElement('div');
        backdrop.style.cssText = 'position: fixed; top: 0; left: 0; width: 100%; height: 100%; background-color: rgba(51, 51, 51, 0.6); z-index: 99;';
        document.body.appendChild(backdrop);
        document.getElementById('pongCanvas').style.filter = 'blur(8px)';

        const canvas = document.getElementById('pongCanvas');
        if (canvas) {
            canvas.style.filter = 'blur(8px)';
        }


        const leftbar = document.getElementById('left-sidebar');
        leftbar.style.cssText += "z-index: 98;"
        const mobilebar = document.getElementById('mobile-sidebar');
        mobilebar.style.cssText += "z-index: 98;"
        const togglebar = document.getElementById('toggle-sidebar');
        togglebar.style.cssText += "z-index: 98;"

        let winBox = document.createElement('div');
        winBox.setAttribute('id', 'winBox');
        winBox.style.cssText = 'position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%); padding: 15px; background-color: #ffffff7a; border: 2px solid #ffffff; text-align: center; z-index: 100; border-radius: 10px; width: 25vw; height: 25vh;padding: 2%';

        document.body.appendChild(winBox);
        const winnerText = document.createElement('p');
        winnerText.textContent = `${data.win === 'player0' ? this.player1 : this.player2} wins !`;
        winnerText.style.cssText = 'font-size: 30px; font-family: "Poppins", sans-serif; font-weight: bold; font-style: normal; color: white; text-align: center; padding: 3%';

        winBox.appendChild(winnerText);
        const scoreContainer = document.createElement('div');
        const scoreText = document.createElement('p');
        scoreText.textContent = `${this.player1} ${data.score[0]}  -  ${data.score[1]} ${this.player2}`;
        scoreText.style.cssText = 'font-size: 20px;';
        scoreContainer.appendChild(scoreText);
        winBox.appendChild(scoreContainer);

        const backButton = document.createElement('button');
        backButton.textContent = 'Back to lobby';
        backButton.classList.add('btn', 'btn-primary');
        backButton.onclick = () => {
            removeElements();
            const leftbar = document.getElementById('left-sidebar');
            leftbar.style.cssText += "z-index: 100;"
            const mobilebar = document.getElementById('mobile-sidebar');
            mobilebar.style.cssText += "z-index: 100;"
            const togglebar = document.getElementById('toggle-sidebar');
            togglebar.style.cssText += "z-index: 100;"
            this.quit();
        };
        winBox.appendChild(backButton);

        if (this.tournament) {
            const nextMatchButton = document.createElement('button');
            nextMatchButton.textContent = 'Continue';
            nextMatchButton.classList.add('btn', 'btn-primary');
            nextMatchButton.style.marginLeft = '10px';
            nextMatchButton.onclick = () => {
                removeElements();
                this.tournament.nextMatch();
            };
            winBox.appendChild(nextMatchButton);
        }

        function removeElements() {
            canvas && (canvas.style.filter = '');
            backdrop.parentNode && backdrop.parentNode.removeChild(backdrop);
            winBox.parentNode && winBox.parentNode.removeChild(winBox);
        }
    }
}
