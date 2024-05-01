// Description: Contains functions for game logic.
export function join_game(main, game_id)
{
    if (main.login === '') {
        main.set_status('Please login or sign up');
        return;
    }
    
    var csrftoken = main.getCookie('csrftoken');

    if (csrftoken) {
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
                    // this.rooms_update();
                } else {
                    switch (info.game) {
                        case 'pong':
                            this.pong_game(info);
                            break;
                    }
                }
            },
            error: () => main.set_status('Error: Can not join game')
        });
    } else
        main.load('/pages/login', () => main.log_in.events());
}