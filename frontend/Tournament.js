export class Tournament {

    constructor(m) {
        this.main = m;
    }

    events() {
        this.dom_tournamentForm = document.getElementById('tournamentForm');
        this.dom_tournamentForm.addEventListener('submit', (e) => this.tournamentSubmit(e));
        // this.dom_listUsers = document.getElementById('players-list');
        // this.dom_listUsers = document.addEventListener('players-list', (e) => this.fetchUsers());
    }
    
    tournamentSubmit(event) {
        event.preventDefault();

        const formData = {
            name: document.getElementById('tname').value,
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
                this.main.load('/tournament/lobby/', () => this.main.tournament.events());
            },
            error: () => {
                this.main.set_status('Error: Could not create tournament');
            }
        });
    }

    // fetchUsers() {
    //     $.ajax({
    //         url: '/tournament/list/users/',
    //         method: 'GET',
    //         success: (data) => {
    //             const playersList = document.getElementById('players-list');
    //             playersList.innerHTML = ''; // Clear existing list items
    //             data.forEach((user) => {
    //                 const li = document.createElement('li');
    //                 li.textContent = `${user.login} - ${user.name}`; // Adjust based on your actual user object structure
    //                 playersList.appendChild(li);
    //             });
    //         },
    //         error: () => {
    //             console.error('Error fetching players');
    //         }
    //     });
    // }
}