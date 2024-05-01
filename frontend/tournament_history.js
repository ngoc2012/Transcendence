
export class tournament_history {
    constructor(m) {
        this.main = m;
    }

    events() {
        
        this.dom_proceed = document.querySelector("#proceed");
        this.dom_proceed.addEventListener("click", () => this.proceed());
        this.dom_Select = document.querySelector("#Select");
        this.dom_Select.addEventListener("click", () => this.selectTournament());

    }


    selectTournament() {

        const tournament_name = document.getElementById('tournamentSelect').value
        console.log(tournament_name)
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
                        <h3>Contenders:</h3>
                        <ul>
                        ${contenders.map(contender => contender[0]).join(', ')}
                        </ul>
                    
                        <h3>Matches:</h3>
                        <ul>
                        ${matches.map(match => `<li>Match number ${match[4]} : ${match[0][0]} vs ${match[1][0]} <br>Result : ${match[2]} - ${match[3]} | Winner : ${match[5]}</li>`).join('')}
                        </ul>
                        <h3><p style="font-weight: bold;">Winner:<br>${tournamentWinner} !</p></h3>
                    `;
                }
                else {
                    document.getElementById("selectedTournamentName").innerHTML = `
                        <h1><p style="font-weight: bold;">${tournamentName}</p></h1>
                        <h3>Contenders:</h3>
                        <ul>
                        ${contenders.map(contender => contender[0]).join(', ')}
                        </ul>
                        <h3>Matches:</h3>
                        <ul>
                        ${matches.map(match => `<li>Match number ${match[4]} : ${match[0][0]} vs ${match[1][0]} <br>Result : ${match[2]} - ${match[3]} | Winner : ${match[5]}</li>`).join('')}
                        </ul>
                        <h3><p style="font-weight: bold;">Winner:<br>The tournament is not over yet !</p></h3>
                    `;
                }
            },
            error: (xhr, status, error) => {
                console.error('Error:', error);
            }
        });
    }

    proceed() {
        this.main.history_stack.push('/');
        window.history.pushState({}, '', '/');
        this.main.load('/lobby', () => this.main.lobby.events());
    }

}
