export class Draw
{
	constructor(p) {
        this.pong = p;
    }

	execute(data) {
		// Clear the canvas
		this.pong.ctx.clearRect(0, 0, this.pong.room.data.WIDTH, this.pong.room.data.HEIGHT);

		// Draw paddles
		this.pong.ctx.fillStyle = '#8b3a62';
        data.players.forEach((p) => {
		    this.pong.ctx.fillRect(
                p.x,
                p.y,
                this.pong.room.data.PADDLE_WIDTH,
                this.pong.room.data.PADDLE_HEIGHT);
        });

		// Draw this.pong.ball
		this.pong.ctx.beginPath();
		this.pong.ctx.arc(data.ball.x, data.ball.y, this.pong.room.data.RADIUS, 0, Math.PI * 2);
		this.pong.ctx.fillStyle = '#00ffcc';
		this.pong.ctx.fill();
		this.pong.ctx.closePath();
	}
}
