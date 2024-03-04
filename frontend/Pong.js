import {Draw} from './Draw.js'

export class Pong
{
    constructor(m, l, r, t = null) {
        this.main = m;
        this.lobby = l;
        this.room = r;
        this.connected = false;
        this.socket = -1;
        this.draw = new Draw(this);
        this.tournament = t;
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
        this.dom_start = document.getElementById("start");
        this.dom_quit = document.getElementById("quit");
        this.dom_start.addEventListener("click", () => this.start());
        this.dom_quit.addEventListener("click", () => this.quit());
        document.addEventListener('keydown', (event) => {
            switch (event.key) {
                case 'ArrowUp':
                    this.set_state("up");
                    break;
                case 'ArrowDown':
                    this.set_state("down");
                    break;
                case 'ArrowLeft':
                    this.set_state("left");
                    break;
                case 'ArrowRight':
                    this.set_state("right");
                    break;
                // change side
                case 's':
                    this.set_state("side");
                    break;
                case 'c':
                    this.set_state("server");
                    break;
                case ' ':
                    this.start();
                    break;
                case 'q':
                    this.quit();
                    break;
            }
        });
        this.connect();
	}

    start() {
        if (this.socket !== -1)
            this.socket.send('start');
        if (this.tournament) {
            // check if 2 players are here ?
            this.main.lobby.socket.send(JSON.stringify({type: 'match_start', roomId: this.room.id}));
        }
    }

    quit() {
        this.set_state('quit');
        if (this.socket !== -1)
        {
            this.socket.close();
            this.socket = -1;
        }
        this.main.load('/lobby', () => this.lobby.events());
    }

    connect() {
        this.socket = new WebSocket(
            'wss://'
            + window.location.host
            + '/ws/pong/'
            + this.room.id
            + '/'
            + this.room.player_id
            + '/'
        );

        this.socket.onmessage = (e) => {
            if (!('data' in e))
                return;
            let data = JSON.parse(e.data);
            //console.log(data.score);
            if ('win' in data) {
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
                this.draw.execute(data);
        };

        this.socket.onclose = (e) => {
            //console.error('Chat socket closed unexpectedly');
        };
    }

    set_state(e) {
        if (this.socket !== -1)
            this.socket.send(e);
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
                this.set_state('quit');
                if (this.socket !== -1) {
                    this.socket.close();
                    this.socket = -1;
                }
                this.tournament.endMatch(data);
            };     
        }   
        winBox.appendChild(backButton);

        document.body.appendChild(winBox);
    }
}
