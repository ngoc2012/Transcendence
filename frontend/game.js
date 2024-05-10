// Description: Contains functions for game logic.
export function join_game(main, game_id, isPopState, joined = false)
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
            if (typeof info === 'string') {
                main.set_status(info);
                main.load('/lobby', () => main.lobby.events(false));
            } else {
                switch (info.game) {
                    case 'pong':
                        if (joined)
                            main.lobby.pong_game(info, isPopState, true);
                        else
                        main.lobby.pong_game(info, isPopState);
                        break;
                }
            }
        },
        error: (info) => {
            main.set_status('Error: Can not join game', false);
        }
    });
}
