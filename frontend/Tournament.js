export class Tournament {

    constructor(m) {
        this.main = m;
    }

    events() {
        this.dom_tournamentForm = document.getElementById('tournamentForm');
        this.dom_tournamentForm.addEventListener('submit', (e) => this.tournamentSubmit(e));
    }
    
    tournamentSubmit(event) {
        event.preventDefault();

        const formData = {
            name: document.getElementById('name').value,
            game: document.getElementById('game').value,
            login: this.main.login,
        };

        $.ajax({
            url: '/tournament/new/',
            method: 'POST',
            data: formData,
            success: (response) => {
                this.main.set_status('Tournament created successfully');
                console.log(response);
                // this.main.load('/tournament/lobby', () => this.main.tournament_lobby.events());
            },
            error: () => {
                this.main.set_status('Error: Could not create tournament');
                // console.log(main.dom_status);
            }
        });
    }
}