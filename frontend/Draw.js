import { TextGeometry } from './TextGeometry.js';
import { OrbitControls } from './OrbitControls.js';

export class Draw
{
	constructor(p) {
        this.pong = p;
        this.ratio = 1.0;
        this.json_font = null;
	}

	init() {
		this.n_paddles = 0;
		this.paddles = [];

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
        
        // Draw table
        const tableGeometry = new THREE.BoxGeometry(
			this.pong.room.data.WIDTH * this.ratio,
			this.pong.room.data.HEIGHT * this.ratio,
			2);
        const tableMaterial = new THREE.MeshPhongMaterial({ color: 0x0077FF });
        const table = new THREE.Mesh(tableGeometry, tableMaterial);
        table.position.z = -1;
        this.scene.add(table);
        
        // Draw barriers
        const barrierGeometry = new THREE.BoxGeometry(
			this.pong.room.data.WIDTH * this.ratio, 2,
			this.pong.room.data.RADIUS * this.ratio * 2);
        const barrierMaterial = new THREE.MeshPhongMaterial({ color: 0x0077FF });
        const barrier1 = new THREE.Mesh(barrierGeometry, barrierMaterial);
        barrier1.position.y = this.pong.room.data.HEIGHT * this.ratio / 2 + 1;
        barrier1.position.z = this.pong.room.data.RADIUS * this.ratio;
        this.scene.add(barrier1);
        const barrier2 = new THREE.Mesh(barrierGeometry, barrierMaterial);
        barrier2.position.y = -this.pong.room.data.HEIGHT * this.ratio / 2 - 1;
        barrier2.position.z = this.pong.room.data.RADIUS * this.ratio;
        this.scene.add(barrier2);
        
        // Draw scores
        // $.ajax({
        //     url: '/pong/load_font',
        //     method: 'GET',
        //     headers: {
        //         'Authorization': `Bearer ${sessionStorage.JWTToken}`
        //     },
        //     success: (response) => {
        //         if (response.token) {
        //             sessionStorage.setItem('JWTToken', response.token);
        //         }
        //         if (response.error) {
        //             const message = response.message;
        //             this.main.set_status('Error: ' + message);
        //         }
        //         else
        //         {
        //             this.json_font = response;
        //             const loader = new THREE.FontLoader();
        //             const font = loader.parse( this.json_font );
        //             var geometry = new THREE.TextGeometry('1 - 0', {
        //                 font: font,
        //                 size: 1,
        //                 height: 0.5,
        //                 curveSegments: 12,
        //                 bevelEnabled: true,
        //                 bevelThickness: 0.03,
        //                 bevelSize: 0.02,
        //                 bevelSegments: 5
        //             });
        //             var material = new THREE.MeshBasicMaterial({ color: 0xff0000 });
        //             var mesh = new THREE.Mesh(geometry, material);
        //             this.scene.add(mesh);
        //         }
        //     },
        //     error: (xhr, textStatus, errorThrown) => {
        //     let errorMessage = "Error: Can not get json font";
        //     if (xhr.responseJSON && xhr.responseJSON.error) {
        //         errorMessage = xhr.responseJSON.error;
        //     }
        //     this.main.set_status(errorMessage);
        //     }
        // });

        // const loader = new THREE.FontLoader();
        // loader.load('https://threejs.org/examples/fonts/optimer_regular.typeface.json', (font) => {
        // const geometry = new THREE.TextGeometry('Buy Here!', {
        //     font: font,
        //     size: 2,
        //     height: 200
        // });
        // geometry.center();
        // const material = new THREE.MeshLambertMaterial({
        //     color: 0x686868
        // });
        // const mesh = new THREE.Mesh(geometry, material);
        // mesh.position.y = - 1; // FIX
        
        // mesh.name = "bhText"
        // this.scene.add(mesh);
        
        // });
        
        // Create ball
        const ballGeometry = new THREE.SphereGeometry(this.pong.room.data.RADIUS * this.ratio, 32, 32);
        const ballMaterial = new THREE.MeshPhongMaterial({ color: 0xFFA500 });
        this.ball = new THREE.Mesh(ballGeometry, ballMaterial);
        this.ball.position.z = this.pong.room.data.RADIUS * this.ratio / 2;
        this.scene.add(this.ball);
 
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
		if (data.players.length !== this.n_paddles) {
            this.paddles.forEach((p) => {this.scene.remove(p);});
            this.paddles = [];
			data.players.forEach((p) => {
                this.paddleMaterial = new THREE.MeshPhongMaterial({ color: this.getRandomColor() });
				const paddle = new THREE.Mesh(this.paddleGeometry, this.paddleMaterial);
                paddle.position.z = this.paddleDepth * this.ratio / 2;
				this.scene.add(paddle);
				this.paddles.push(paddle);
                
			});
			this.n_paddles = data.players.length;
		}

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
