import {Pong} from 'Pong.js'
import {game} from '../main.js'

var pong = new Pong();

// Handle keyboard input
document.addEventListener('keydown', function (event) {
    switch (event.key) {
        case 'ArrowUp':
            pong.rightPaddle.dy = -5;
            break;
        case 'ArrowDown':
            pong.rightPaddle.dy = 5;
            break;
        case 'w':
            pong.leftPaddle.dy = -5;
            break;
        case 's':
            pong.leftPaddle.dy = 5;
            break;
    }
});

document.addEventListener('keyup', function (event) {
    switch (event.key) {
        case 'ArrowUp':
        case 'ArrowDown':
            pong.rightPaddle.dy = 0;
            break;
        case 'w':
        case 's':
            pong.leftPaddle.dy = 0;
            break;
    }
});

function pollGameState() {
    // Make an AJAX request to get the current game state
    $.ajax({
        url: '/api/state/',
        method: 'GET',
        success: function(data) {
            // Update game elements based on data received from the server
            updateGame(data);
        },
        error: function(error) {
            console.error('Error fetching game state:', error);
        }
    });
}

// Send player actions to the server
function sendAction(action) {
    // Make an AJAX request to send player action to the server
    $.ajax({
        url: '/api/action/',
        method: 'POST',
        data: { action: action },
        success: function(response) {
            // Handle server response if needed
        },
        error: function(error) {
            console.error('Error sending player action:', error);
        }
    });
}

