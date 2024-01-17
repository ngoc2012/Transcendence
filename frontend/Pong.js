export class Pong
{
	constructor(m, l, r) {
        this.main = m;
        this.lobby = l;
        this.room = r;
        this.connected = false;
        this.socket = -1;
    }

	init() {
        this.dom_game_name = document.getElementById("game_name");
        this.dom_game_name.innerHTML = this.room.name;
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
            'ws://'
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
            if ('score' in data)
            {
                this.dom_score0.innerHTML = data.score[0];
                this.dom_score1.innerHTML = data.score[1];
            }
            else
                this.draw(data);
        };

        this.socket.onclose = (e) => {
            //console.error('Chat socket closed unexpectedly');
        };
    }

    set_state(e) {
        if (this.socket !== -1)
            this.socket.send(e);
    }

	draw(data) {
		// Clear the canvas
		this.ctx.clearRect(0, 0, this.room.data.WIDTH, this.room.data.HEIGHT);

		// Draw paddles
		this.ctx.fillStyle = '#8b3a62';
        data.players.forEach((p) => {
		    this.ctx.fillRect(
                p.x,
                p.y,
                this.room.data.PADDLE_WIDTH,
                this.room.data.PADDLE_HEIGHT);
        });

		// Draw this.ball
		this.ctx.beginPath();
		this.ctx.arc(data.ball.x, data.ball.y, this.room.data.RADIUS, 0, Math.PI * 2);
		this.ctx.fillStyle = '#00ffcc';
		this.ctx.fill();
		this.ctx.closePath();
	}
}
