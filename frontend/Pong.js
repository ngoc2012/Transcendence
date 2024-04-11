import {Draw} from './Draw.js'

export class Pong
{
    constructor(m, l, r, t = null) {
        this.main = m;
        this.lobby = l;
        this.room = r;
        this.connected = false;
        this.power_play = false;
        this.draw = new Draw(this);
        this.tournament = t;
        this.keyboard_layout = "";
        this.players = [{
            'id': this.room.player_id,
            'sk': -1
        }];
    }

	init() {
        this.dom_game_name = document.getElementById("game_name");
        this.dom_game_name.innerHTML = this.room.name;
        this.dom_team0 = document.getElementById("team0");
        this.dom_team1 = document.getElementById("team1");
        this.dom_score0 = document.getElementById("score0");
        this.dom_score1 = document.getElementById("score1");
        
		this.canvas = document.getElementById('pongCanvas');
		this.ctx = this.canvas.getContext('2d');
        this.ctx.canvas.width  = this.room.data.WIDTH;
        this.ctx.canvas.height = this.room.data.HEIGHT;

        this.pongThreeJS = document.getElementById('pongThreeJS');

        this.dom_start = document.getElementById("start");
        this.dom_quit = document.getElementById("quit");
        this.dom_start.addEventListener("click", () => this.start());
        this.dom_quit.addEventListener("click", () => this.quit());

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
        this.dom_toggle_AI = document.getElementById("toggle_AI");
        this.dom_power_play = document.getElementById("power_play");
        this.dom_toggle_display = document.getElementById('toggle_display');
        this.dom_toggle_display_board = document.getElementById('toggle_display_board');
        this.dom_display_board = document.getElementById('display_board');

        this.dom_new_local_player = document.getElementById('new_local_player');
        this.dom_local_player = document.getElementById('local_player');
        this.dom_login_local = document.getElementById('login_local');
        this.dom_password_local = document.getElementById('password_local');
        this.dom_keyboard_layout = document.getElementById('keyboard_layout');
        this.dom_join_local = document.getElementById('join_local');
        this.dom_close_local = document.getElementById('close_local');

        document.addEventListener('keydown', (event) => {
            switch (event.key) {
                case 'ArrowUp':
                    this.set_state(0, "up");
                    break;
                case 'ArrowDown':
                    this.set_state(0, "down");
                    break;
                case 'ArrowLeft':
                    if (this.power_play)
                        this.set_state(0, "left");
                    break;
                case 'ArrowRight':
                    if (this.power_play)
                        this.set_state(0, "right");
                    break;
                // change side
                case 'Tab':
                    if (this.power_play)
                        this.set_state(0, "side");
                    break;
                case 'Control':
                    this.set_state(0, "server");
                    break;
                // case ' ':
                //     this.start();
                //     break;
                // case 'q':
                //     this.quit();
                //     break;
            }
            
            let commands = ['up', 'down', 'left', 'right'];
            if (event.key && event.key.length === 1)
            {
                let index = this.keyboard_layout.indexOf(event.key);
                if (index >= 0)
                {
                    let i_player = Math.floor(index / 4) + 1;
                    index = index % 4;
                    this.set_state(i_player, commands[index]);
                }
                
            }
        });

        this.dom_toggle_AI.addEventListener('click', () => {this.set_state(0, 'ai_player')});
        this.dom_power_play.addEventListener('click', () => {this.set_state(0, 'power')});
		this.dom_toggle_display.addEventListener('click', () => {this.toggle_display()});
        this.dom_toggle_display_board.addEventListener('click', () => {this.toggle_display_board()});
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
        
        this.dom_new_local_player.addEventListener('click', () => {
            this.dom_local_player.style.display = 'block';
            // this.dom_new_local_player.style.display = 'none';
        });
        this.dom_close_local.addEventListener('click', () => {
            this.dom_local_player.style.display = 'none';
            // this.dom_new_local_player.style.display = 'block';
        });
        this.dom_join_local.addEventListener('click', () => {
            this.local_player_login();
        });
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
            return true; // Character found, exit the loop
          }
        }
        return false; // Character not found in the entire loop
    }

    local_player_login() {
        if (this.dom_login_local.value === '' || this.dom_password_local.value === '')
        {
            this.main.set_status('Field must not be empty');
            return;
        }
        if (this.dom_keyboard_layout.value.length !== 4)
        {
            this.main.set_status('Keyboard layout must be 4 characters');
            return;
        }
        if (this.charExists(this.dom_keyboard_layout.value, this.keyboard_layout))
        {
            this.main.set_status('Keyboard layout must not contain already used characters');
            return;
        }
        $.ajax({
            url: '/log_in/',
            method: 'POST',
            data: {
                "login": this.dom_login_local.value,
                "password": this.dom_password_local.value,
            },
            success: (info) => {
                if (typeof info === 'string')
                {
                    this.main.set_status(info);
                }
                else
                {
                    this.join_local_player(info);
                }
            },
            error: (xhr, textStatus, errorThrown) => {
                if (xhr.responseJSON && xhr.responseJSON.error) {
                    this.main.set_status(xhr.responseJSON.error);
                } else {
                    this.main.set_status('An error occurred during the request.');
                }
            }
        });
    }

    join_local_player(player) {
        $.ajax({
            url: '/game/join',
            method: 'POST',
            data: {
                'login': player.login,
                "game_id": this.room.id
            },
            success: (info) => {
                if (typeof info === 'string')
                {
                    this.main.set_status(info);
                }
                else
                {
                    this.players.push({
                        'id': player.id,
                        'sk': -1
                    });
                    let i = this.players.length - 1;
                    this.connect(i);
                    if (this.players[i].sk !== -1)
                    {
                        this.dom_local_player.style.display = 'none';
                        // this.dom_new_local_player.style.display = 'none';
                        this.keyboard_layout += this.dom_keyboard_layout.value;
                    }
                }
            },
            error: () => this.main.set_status('Error: Can not join game')
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
        // this.ai_player = val;
        if (val)
            this.dom_toggle_AI.innerHTML = "AI player off";
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
    }

    quit() {
        this.players.forEach((p, i) => {
            this.set_state(i, 'quit');
            if (p.sk !== -1)
            {
                p.sk.close();
                p.sk = -1;
            }
        });
        
        this.main.history_stack.push('/');
        window.history.pushState({}, '', '/');
        this.main.load('/lobby', () => this.lobby.events());
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
            this.main.history_stack.push('/pong/' + this.room.id);
            window.history.pushState({}, '', '/pong/' + this.room.id);
        };

        this.players[i].sk.onmessage = (e) => {
            if (!('data' in e))
                return;
            let data = JSON.parse(e.data);
            if ('win' in data) {
                this.winnerBox(data);
            }
            else if (data.start === "tour_match_start") {
                if (this.tournament) {
                    this.main.lobby.socket.send(JSON.stringify({type: 'match_start', roomId: this.room.id}));
                }
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
                    let new_p = document.createElement("li");
                    new_p.textContent = p;
                    this.dom_team0.appendChild(new_p);
                });
                this.dom_team1.innerHTML = "";
                data.team1.forEach((p) => {
                    let new_p = document.createElement("li");
                    new_p.textContent = p;
                    this.dom_team0.appendChild(new_p);
                });
            }
            else
            {
                if ('power_play' in data)
                    this.set_power_play(data.power_play);
                if ('ai_player' in data)
                    this.set_ai_player(data.ai_player);
                this.draw.update(data);
                this.draw.execute(data);
            }
        };
    
        this.players[i].sk.onclose = (e) => {
            this.main.load('/lobby', () => this.lobby.events());
        };
    }

    set_state(i, e) {
        if (this.players[i].sk !== -1)
            this.players[i].sk.send(e);
    }

    winnerBox(data) {
        let backdrop = document.createElement('div');
        backdrop.style.cssText = 'position: fixed; top: 0; left: 0; width: 100%; height: 100%; background-color: rgba(0, 0, 0, 0.5); z-index: 99;';
        document.body.appendChild(backdrop);
        document.getElementById('pongCanvas').style.filter = 'blur(8px)';

        let winBox = document.createElement('div');
        winBox.setAttribute('id', 'winBox');
        winBox.style.cssText = 'position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%); padding: 20px; background-color: #fff; border: 2px solid #000; text-align: center; z-index: 100;';

        let winnerText = document.createElement('p');
        winnerText.textContent = `Winner: ${data.win}`;
        winBox.appendChild(winnerText);

        let scoreText = document.createElement('p');
        scoreText.textContent = `Score - Player0: ${data.score[0]}, Player1: ${data.score[1]}`;
        winBox.appendChild(scoreText);

        let backButton = document.createElement('button');
        backButton.textContent = 'Back to Lobby';
        backButton.onclick = () => {
            document.getElementById('pongCanvas').style.filter = '';
            document.body.removeChild(backdrop);
            document.body.removeChild(winBox);
            if (this.tournament) {
                // this.set_state('quit');
                // if (this.socket !== -1) {
                //     this.socket.close();
                //     this.socket = -1;
                // }
                this.quit();
                this.tournament.endMatch(data);
            };     
        }   
        winBox.appendChild(backButton);

        document.body.appendChild(winBox);
    }
}
