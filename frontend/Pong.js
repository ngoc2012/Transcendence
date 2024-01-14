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
		this.canvas = document.getElementById('pongCanvas');
		this.ctx = this.canvas.getContext('2d');
        this.ctx.canvas.width  = this.room.data.width;
        this.ctx.canvas.height = this.room.data.height;
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
        this.socket = new WebSocket(
            'ws://'
            + window.location.host
            + '/ws/pong/'
            + this.room.data.room
            + '/'
        );

        this.socket.onmessage = (e) => {
            if (!('data' in e))
                return;
            const rooms = JSON.parse(e.data);
            var options_rooms = this.dom_rooms && this.dom_rooms.options;
            this.dom_rooms.innerHTML = "";
            if (options_rooms && rooms && rooms.length > 0) {
                rooms.forEach((room) => {
                    var option = document.createElement("option");
                    option.value = room.id;
                    option.text = room.name + " - " + room.id;
                    this.dom_rooms.add(option);
                });
            }
        };

        this.socket.onclose = (e) => {
            //console.error('Chat socket closed unexpectedly');
        };
    }

    set_state(e) {
        if (this.connected && this.socket !== -1)
            this.socket.send(JSON.stringify({ 
                'login': this.main.login,
                'action': e
        }));
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
		this.ctx.clearRect(0, 0, this.room.data.width, this.room.data.height);

		// Draw paddles
		this.ctx.fillStyle = '#8b3a62';
        //this.data.position.forEach((p, i) => {
        this.data.position.forEach((p) => {
		    this.ctx.fillRect(
                p.x,
                p.y,
                this.room.data.paddle_width,
                this.room.data.paddle_height);
        });

		// Draw this.ball
		this.ctx.beginPath();
		this.ctx.arc(this.data.ball.x, this.data.ball.y, this.room.data.ball_r, 0, Math.PI * 2);
		this.ctx.fillStyle = '#00ffcc';
		this.ctx.fill();
		this.ctx.closePath();
	}
}
