import {new_connection} from './new_connection.js'

export class Pong
{
	constructor(m, g, i) {
        this.main = m;
        this.lobby = g;
        this.info = i;
        this.connected = false;
        this.socket = -1;
    }

	init() {
		this.canvas = document.getElementById('pongCanvas');
		this.ctx = this.canvas.getContext('2d');
        this.ctx.canvas.width  = this.info.width;
        this.ctx.canvas.height = this.info.height;
        let dom_start = document.getElementById("start");
        let dom_quit = document.getElementById("quit");
        dom_start.addEventListener("click", () => this.set_state("start"));
        dom_quit.addEventListener("click", () => this.quit());
        document.addEventListener('keydown', (event) => {
            switch (event.key) {
                case 'ArrowUp':
                    this.set_state("up");
                    break;
                case 'ArrowDown':
                    this.set_state("down");
                    break;
            }
        });
        this.connect();
	}

    quit() {
        if (this.socket !== -1)
            this.socket.close();
        this.main.load('/lobby', () => this.lobby.events());
    }

    connect() {
        this.main.set_status("Connecting to server...");
        new_connection({
            name: "Connect to pong server",
            link: 'ws://127.0.0.1:8000/pong/' + this.info.room + '?user=' + this.main.id,
            callback: {
                open: () => {
                    this.connected = true;
                    if (this.lobby.socket.readyState === WebSocket.OPEN)
                        this.lobby.socket.send(this.info);
                    else
                        this.main.set_status('Error: WebSocket lobby not open.')
                },
                message: this.update_state,
                close: this.quit
            }
        });
    }

    set_state(e) {
        if (this.connected && this.socket !== -1)
            this.socket.send(JSON.stringify({ 'do': e }));
    }

    update_state(data) {
        this.data = data;
        if (this.connected && this.lobby.socket !== -1)
        {
            this.socket.send("got");
            this.draw();
        }
    }

	draw() {
		// Clear the canvas
		this.ctx.clearRect(0, 0, this.info.width, this.info.height);

		// Draw paddles
		this.ctx.fillStyle = '#8b3a62';
        //this.data.position.forEach((p, i) => {
        this.data.position.forEach((p) => {
		    this.ctx.fillRect(
                p.x,
                p.y,
                this.info.paddle_width,
                this.info.paddle_height);
        });

		// Draw this.ball
		this.ctx.beginPath();
		this.ctx.arc(this.data.ball.x, this.data.ball.y, this.info.ball_r, 0, Math.PI * 2);
		this.ctx.fillStyle = '#00ffcc';
		this.ctx.fill();
		this.ctx.closePath();
	}
}
