// import { TextGeometry } from './TextGeometry.js';
// import { OrbitControls } from './OrbitControls.js';

export class Draw
{
	constructor(p) {
        this.pong = p;
        this.ratio = 1.0;
        this.json_font = null;
        this.data = null;
        this.table = null;
        this.barrier1 = null;
        this.barrier2 = null;
        this.paddles = [];
	}

    update_3D(data) {
        if (this.table !== null) {
            this.scene.remove(this.table);
            this.scene.remove(this.barrier1);
            this.scene.remove(this.barrier2);
            this.scene.remove(this.ball);
        }
        if (this.paddles.length > 0) {
            this.paddles.forEach((p) => {this.scene.remove(p);});
            this.paddles = [];
        }
        // Draw table
        const tableGeometry = new THREE.BoxGeometry(
			this.pong.room.data.WIDTH * this.ratio,
			this.pong.room.data.HEIGHT * this.ratio,
			2);
        const tableMaterial = new THREE.MeshPhongMaterial({ color: 0x0077FF });
        this.table = new THREE.Mesh(tableGeometry, tableMaterial);
        this.table.position.z = -1;
        this.scene.add(this.table);
        
        // Draw barriers
        const barrierGeometry = new THREE.BoxGeometry(
			this.pong.room.data.WIDTH * this.ratio, 2,
			this.pong.room.data.RADIUS * this.ratio * 2);
        const barrierMaterial = new THREE.MeshPhongMaterial({ color: 0x0077FF });
        this.barrier1 = new THREE.Mesh(barrierGeometry, barrierMaterial);
        this.barrier1.position.y = this.pong.room.data.HEIGHT * this.ratio / 2 + 1;
        this.barrier1.position.z = this.pong.room.data.RADIUS * this.ratio;
        this.scene.add(this.barrier1);
        this.barrier2 = new THREE.Mesh(barrierGeometry, barrierMaterial);
        this.barrier2.position.y = -this.pong.room.data.HEIGHT * this.ratio / 2 - 1;
        this.barrier2.position.z = this.pong.room.data.RADIUS * this.ratio;
        this.scene.add(this.barrier2);
        
        // Create ball
        const ballGeometry = new THREE.SphereGeometry(this.pong.room.data.RADIUS * this.ratio, 32, 32);
        const ballMaterial = new THREE.MeshPhongMaterial({ color: 0xFFA500 });
        this.ball = new THREE.Mesh(ballGeometry, ballMaterial);
        this.ball.position.z = this.pong.room.data.RADIUS * this.ratio / 2;
        this.scene.add(this.ball);

        this.update(data);
    }
    
	init() {
		// Set up the scene
        this.scene = new THREE.Scene();
        this.scene.background = new THREE.Color(0x808080);
        this.camera = new THREE.PerspectiveCamera(75,
			this.pong.room.data.WIDTH / this.pong.room.data.HEIGHT,
			0.1, 1000);
        this.renderer = new THREE.WebGLRenderer();
        //this.controls = new OrbitControls( this.camera, this.renderer.domElement );

        this.renderer.setSize(this.pong.room.data.WIDTH * this.ratio, this.pong.room.data.HEIGHT * this.ratio);
        this.pong.pongThreeJS.style.width = this.pong.room.data.WIDTH * this.ratio;
        this.pong.pongThreeJS.style.height = this.pong.room.data.HEIGHT * this.ratio;
        this.pong.pongThreeJS.appendChild(this.renderer.domElement);
        
        // Add lighting
        this.ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
        this.scene.add(this.ambientLight);
        this.directionalLight = new THREE.DirectionalLight(0xffffff, 0.5);
        this.directionalLight.position.set(0, 1, 0);
        this.scene.add(this.directionalLight);

        // Create paddles
        this.paddleDepth = this.pong.room.data.RADIUS * this.ratio * 2;
        this.paddleGeometry = new THREE.BoxGeometry(
			this.pong.room.data.PADDLE_WIDTH * this.ratio,
			this.pong.room.data.PADDLE_HEIGHT * this.ratio,
			this.paddleDepth);
        
        this.update_3D(this.data);
 
        this.center = new THREE.Vector3(0, 0, 0); 
        this.distance = 200 * this.ratio / Math.tan(Math.PI * this.camera.fov / 360);

    }

    update_camera() {
		this.camera.fov = parseFloat(this.pong.dom_angle.value);
		this.camera.aspect = parseFloat(this.pong.dom_ratio.value);
		this.camera.near = parseFloat(this.pong.dom_near.value);
		this.camera.far = parseFloat(this.pong.dom_far.value);
		this.camera.position.x = this.distance * parseFloat(this.pong.dom_pos_x.value);
		this.camera.position.y = this.distance * parseFloat(this.pong.dom_pos_y.value);
		this.camera.position.z = this.distance * parseFloat(this.pong.dom_pos_z.value);
		this.center.x = this.distance * parseFloat(this.pong.dom_center_x.value);
		this.center.y = this.distance * parseFloat(this.pong.dom_center_y.value);
		this.center.z = this.distance * parseFloat(this.pong.dom_center_z.value);
        this.camera.lookAt(this.center);
		this.ambientLight.intensity = parseFloat(this.pong.dom_amb_dens.value);
		this.directionalLight.intensity = parseFloat(this.pong.dom_dir_dens.value);
		let x = parseFloat(this.pong.dom_light_x.value);
		let y = parseFloat(this.pong.dom_light_y.value);
		let z = parseFloat(this.pong.dom_light_z.value);
        this.directionalLight.position.set(x, y, z);

        this.camera.updateProjectionMatrix();
        //this.controls.update();
        this.renderer.render(this.scene, this.camera);
    }
    
    getRandomColor() {
        var color = Math.floor(Math.random() * 16777215).toString(16);
        while (color.length < 6)
            color = '0' + color;
        return '#' + color;
    }

	update(data) {
        this.data = data;
        if (data === null)
            return;
		if (data.players.length !== this.paddles.length) {
            this.paddles.forEach((p) => {this.scene.remove(p);});
            this.paddles = [];
			data.players.forEach((p) => {
                this.paddleMaterial = new THREE.MeshPhongMaterial({ color: this.getRandomColor() });
				const paddle = new THREE.Mesh(this.paddleGeometry, this.paddleMaterial);
                paddle.position.z = this.paddleDepth * this.ratio / 2;
				this.scene.add(paddle);
				this.paddles.push(paddle);
                
			});
		}

        if (data.players.length === 0)
            return;
        console.log(this.paddles);
        console.log(data.players);
		data.players.forEach((p, i) => {
			this.paddles[i].position.x = (p.x - this.pong.room.data.WIDTH / 2) * this.ratio + this.pong.room.data.PADDLE_WIDTH * this.ratio / 2;
			this.paddles[i].position.y = (this.pong.room.data.HEIGHT / 2 - p.y) * this.ratio - this.pong.room.data.PADDLE_HEIGHT * this.ratio / 2;
            this.paddles[i].position.z = this.paddleDepth * this.ratio / 2;
		});

		this.ball.position.x = (data.ball.x - this.pong.room.data.WIDTH / 2) * this.ratio;
        this.ball.position.y = (this.pong.room.data.HEIGHT / 2 - data.ball.y) * this.ratio;
        this.ball.position.z = this.pong.room.data.RADIUS * this.ratio / 2;

    	this.renderer.render(this.scene, this.camera);
	}

	execute(data) {
        this.data = data;
        // console.log(this.pong.ctx.canvas.width, this.pong.ctx.canvas.height, this.ratio)
		// Clear the canvas
		this.pong.ctx.clearRect(0, 0, this.pong.ctx.canvas.width, this.pong.ctx.canvas.height);
        // Draw table
        this.pong.ctx.fillStyle = '#0077FF';
        this.pong.ctx.fillRect(0, 0, this.pong.ctx.canvas.width, this.pong.ctx.canvas.height);
        
        // Draw limites
        this.pong.ctx.strokeStyle = '#A9A9A9';
        this.pong.ctx.lineWidth = 1;
        this.pong.ctx.setLineDash([10, 15]);
        this.pong.ctx.beginPath();
        this.pong.ctx.moveTo(this.pong.ctx.canvas.width / 4 + this.pong.room.data.PADDLE_WIDTH * this.ratio, 0);
        this.pong.ctx.lineTo(this.pong.ctx.canvas.width / 4 + this.pong.room.data.PADDLE_WIDTH * this.ratio, this.pong.ctx.canvas.height);
        this.pong.ctx.stroke();

        this.pong.ctx.strokeStyle = '#A9A9A9';
        this.pong.ctx.lineWidth = 1;
        this.pong.ctx.setLineDash([10, 15]);
        this.pong.ctx.beginPath();
        this.pong.ctx.moveTo(this.pong.ctx.canvas.width / 4 * 3 - this.pong.room.data.PADDLE_WIDTH * this.ratio, 0);
        this.pong.ctx.lineTo(this.pong.ctx.canvas.width / 4 * 3 - this.pong.room.data.PADDLE_WIDTH * this.ratio, this.pong.ctx.canvas.height);
        this.pong.ctx.stroke();

        this.pong.ctx.setLineDash([]);

        // Draw barriers
        this.pong.ctx.strokeStyle = '#262626';
        this.pong.ctx.lineWidth = 3;
        this.pong.ctx.beginPath();
        this.pong.ctx.moveTo(this.pong.ctx.canvas.width / 2, 0);
        this.pong.ctx.lineTo(this.pong.ctx.canvas.width / 2, this.pong.ctx.canvas.height);
        this.pong.ctx.stroke();

		// Draw paddles
		this.pong.ctx.fillStyle = '#8b3a62';
        data.players.forEach((p) => {
		    this.pong.ctx.fillRect(
                p.x * this.ratio,
                p.y * this.ratio,
                this.pong.room.data.PADDLE_WIDTH * this.ratio,
                this.pong.room.data.PADDLE_HEIGHT * this.ratio);
        });

		// Draw this.pong.ball
		this.pong.ctx.beginPath();
		this.pong.ctx.arc(data.ball.x * this.ratio, data.ball.y * this.ratio, this.pong.room.data.RADIUS * this.ratio, 0, Math.PI * 2);
		this.pong.ctx.fillStyle = '#FFA500';
		this.pong.ctx.fill();
		this.pong.ctx.closePath();
	}
}
