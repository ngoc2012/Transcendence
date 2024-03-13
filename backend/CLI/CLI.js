const WebSocket = require('ws');
const https = require('https');
const readline = require('readline');

// Disable SSL-related warnings
process.env.NODE_TLS_REJECT_UNAUTHORIZED = "0";

const host = "127.0.0.1:8080";
const certfile = "minh-ngu.crt";
const keyfile = "minh-ngu.key";

let quitProgram = false;
let quitLobby = false;
let quitGame = false;

let roomsSocket = null;
let pongSocket = null;

let rooms = [];
let login = null;

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout
});

const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms));

const roomsListener = async () => {
  const uri = `wss://${host}/ws/game/rooms/`;

  console.log(`Connecting to ${uri}...`);

  const roomsSocket = new WebSocket(uri, {
    ca: certfile,
    key: keyfile,
    cert: certfile,
    rejectUnauthorized: false
  });

  roomsSocket.on('open', () => {
    console.log('Connected to rooms websocket');
  });

  roomsSocket.on('message', (response) => {
    const obj = JSON.parse(response);
    console.clear();

    if (Array.isArray(obj)) {
      rooms = obj;
      rooms.forEach((r, i) => {
        console.log(`${i} - ${r.name} - ${r.id}`);
      });
    }

    console.log("[0..9]: join game\nn: new game\nEsc: quit");

    if (quitLobby) {
      roomsSocket.close();
    }
  });

  roomsSocket.on('close', () => {
    console.log("Rooms websocket connection closed.");
    quitLobby = true;
  });

  roomsSocket.on('error', (error) => {
    console.error(`An unexpected error occurred: ${error}`);
    quitProgram = true;
  });
};

const pongListener = async (room) => {
  const uri = `wss://${host}/ws/pong/${room.id}/${room.player_id}/`;

  console.log(`Connecting to ${uri}...`);

  const pongSocket = new WebSocket(uri, {
    ca: certfile,
    key: keyfile,
    cert: certfile,
    rejectUnauthorized: false
  });

  pongSocket.on('open', () => {
    console.log('Connected to pong websocket');
  });

  pongSocket.on('message', (response) => {
    console.clear();
    console.log("q: quit");
    console.log(response);

    if (quitGame) {
      pongSocket.close();
    }
  });

  pongSocket.on('close', () => {
    console.log("Pong websocket connection closed.");
    quitGame = true;
  });

  pongSocket.on('error', (error) => {
    console.error(`An unexpected error occurred: ${error}`);
    quitGame = true;
  });
};

const joinGame = async (game) => {
  if (game + 1 > rooms.length) {
    return;
  }

  try {
    const response = await new Promise((resolve, reject) => {
      const requestOptions = {
        hostname: host.split(':')[0],
        port: host.split(':')[1] || 443,
        path: '/game/join',
        method: 'POST',
        key: fs.readFileSync(keyfile),
        cert: fs.readFileSync(certfile),
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded'
        }
      };

      const req = https.request(requestOptions, (res) => {
        let data = '';

        res.on('data', (chunk) => {
          data += chunk;
        });

        res.on('end', () => {
          resolve(data);
        });
      });

      req.on('error', (error) => {
        reject(error);
      });

      req.write(`login=${login}&game_id=${rooms[game].id}`);
      req.end();
    });

    if (response.statusCode !== 200) {
      console.log("Request failed with status code:", response.statusCode);
      return;
    }

    quitGame = false;
    pongListener(JSON.parse(response));
  } catch (error) {
    console.error("An unexpected error occurred:", error);
  }
};

const lobby = async () => {
  quitLobby = false;
  roomsListener();
};

const keyboardListener = async () => {
  await lobby();
  await sleep(100);

  while (true) {
    let game = -1;

    for (let i = 0; i < 10; i++) {
      if (keyboard.isPressed(`${i}`)) {
        game = i;
      }
    }

    if (game !== -1) {
      joinGame(game);
    } else if (keyboard.isPressed('esc')) {
      quitLobby = true;
      quitGame = true;

      if (roomsSocket !== null) {
        roomsSocket.send("exit");
      }

      if (pongSocket !== null) {
        pongSocket.send("exit");
      }

      console.log("Bye");
      break;
    } else if (keyboard.isPressed('q')) {
      quitGame = true;

      if (pongSocket !== null) {
        pongSocket.send("exit");
      }

      if (roomsSocket === null) {
        lobby();
      }
    } else if (keyboard.isPressed('up') && pongSocket !== null) {
      pongSocket.send('up');
    } else if (keyboard.isPressed('down') && pongSocket !== null) {
      pongSocket.send('down');
    } else if (keyboard.isPressed('left') && pongSocket !== null) {
      pongSocket.send('left');
    } else if (keyboard.isPressed('right') && pongSocket !== null) {
      pongSocket.send('right');
    } else {
      await sleep(100);
    }

    if (quitProgram) {
      break;
    }
  }
};

const main = async () => {
  await keyboardListener();
};

// const login = () => {
  // Your login logic here
// };

if (require.main === module) {
  // login();
  main();
}
