// Description: Contains functions for game logic.
export function join_game(main, game_id)
{
    console.log("join_game", game_id);
    var csrftoken = main.getCookie('csrftoken');

    if (!csrftoken) {
        main.load('/pages/login', () => main.log_in.events());
        return;
    }

    console.log("join_game2", game_id);
    console.log("join_game3", main.login);
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
                // this.rooms_update();
            } else {
                switch (info.game) {
                    case 'pong':
                        this.pong_game(info);
                        break;
                }
            }
        },
        error: (info) => {
            console.log(info);
            main.set_status('Error: Can not join game');
        }
        // error: () => main.set_status('Error: Can not join game')
    });
}
