// Description: Contains functions for game logic.
export function join_game(main, game_id, isPopState)
{   
    var csrftoken = main.getCookie('csrftoken');
    if (csrftoken === null) {
        main.load('/pages/login', () => main.log_in.events());
        return;
    }
    $.ajax({
        url: '/game/join',
        method: 'POST',
        headers: {
            'X-CSRFToken': csrftoken,
        },
        data: {
            'login': main.login,
            "game_id": game_id
        },
        success: (info) => {
            console.log(info);
            if (typeof info === 'string') {
                main.set_status(info);
            } else {
                switch (info.game) {
                    case 'pong':
                        main.lobby.pong_game(info, isPopState);
                        break;
                }
            }
        },
        error: (info) => {
            main.set_status('Error: Can not join game');
        }
    });
}
