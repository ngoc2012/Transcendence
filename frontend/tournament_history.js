
export class tournament_history {
    constructor(m) {
        this.main = m;
    }

    events(isPopState) {
        if (!isPopState)
            window.history.pushState({ page: '/tournament_history' }, '', '/tournament_history');
        if (this.main.lobby.game && this.main.lobby.game !== null)
        {
            this.main.lobby.game.close_room();
            this.main.lobby.game = null;
        }
        this.dom_proceed = document.querySelector("#proceed");
        this.dom_Select = document.querySelector("#Select");
        if (this.dom_Select) {
            this.dom_Select.addEventListener("click", () => this.selectTournament());
        } else {
            console.error("Element with ID 'dom_Select' not found.");
        }
        

    }

    selectTournament() {

        const tournament_name = document.getElementById('tournamentSelect').value
        const selectedTournamentElement = document.getElementById("selectedTournamentName");
        selectedTournamentElement.innerText = "Selected Tournament: " + tournament_name;

        if (!tournament_name)
        {
            document.getElementById("selectedTournamentName").innerHTML = `
            <h8>There is no active or finished tournament to display !</h8>
        `;
        }
        $.ajax({
            url: '/get_tournament_data/',
            method: 'GET',
            headers:{
				'X-CSRFToken': this.main.getCookie('csrftoken')
			},
            data: {
                "name": tournament_name,
            },
            success: (response) => {

                const tournamentName = response.tournament_name;
                const tournamentWinner = response.tournament_winner;
                const isPending = response.is_pending;
                const contenders = response.contenders;
                const matches = response.matches;

                if (!isPending) {
                    document.getElementById("selectedTournamentName").innerHTML = `
                        <h1><p style="font-weight: bold;">${tournamentName}</p></h1>
                        <h3>Contenders</h3>
                        ${contenders.map(contender => contender[0]).join(', ')}

                        <h3><br>Matches</h3>
                        ${matches.map(match => `Match number ${match[4]} : ${match[0][0]} vs ${match[1][0]} <br>Result : ${match[2]} - ${match[3]} | Winner : ${match[5]}<br><br>`).join('')}
                        <h3><br><p style="font-weight: bold;">Winner<br>${tournamentWinner} !</p></h3>
                    `;
                }
                else {
                    document.getElementById("selectedTournamentName").innerHTML = `
                        <h1><p style="font-weight: bold;">${tournamentName}</p></h1>
                        <h3>Contenders</h3>
                        ${contenders.map(contender => contender[0]).join(', ')}
                        <h3><br>Matches</h3>
                        ${matches.map(match => `Match number ${match[4]} : ${match[0][0]} vs ${match[1][0]} <br>Result : ${match[2]} - ${match[3]} | Winner : ${match[5]}<br>`).join('')}
                        <h3><br><p style="font-weight: bold;">The tournament is not over yet !</p></h3>
                    `;
                }
            },
            error: (jqXHR) => {
                if (jqXHR.status === 401 && jqXHR.responseText === "Unauthorized - Token expired") {
                    this.main.clearClient();
					this.main.load('/pages/login', () => this.main.log_in.events());
					return;
				}
            }
        });
    }
}
