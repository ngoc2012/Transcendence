
export class tournament_history {
    constructor(m) {
        this.main = m;
    }

    events() {
        this.main.set_status('');

        this.dom_Select = document.querySelector("#Select");
        this.dom_Select.addEventListener("click", () => this.selectTournament());

    }


    selectTournament() {

        const tournament_name = document.getElementById('tournamentSelect').value
        console.log(tournament_name)
        const selectedTournamentElement = document.getElementById("selectedTournamentName");
        selectedTournamentElement.innerText = "Selected Tournament: " + tournament_name;

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
                        <h2>Selected Tournament:  ${tournamentName}</h2>
                        <h3>Contenders:</h3>
                        <ul>
                            ${contenders.map(contender => `<li>${contender[0]} - ${contender[1]}</li>`).join('')}
                        </ul>
                        <h3>Matches:</h3>
                        <ul>
                            ${matches.map(match => `<li>${match[4]} : ${match[0]} vs ${match[1]}, ${match[2]} - ${match[3]} | Winner: ${match[5]}</li>`).join('')}
                        </ul>
                        <p>Tournament Winner: ${tournamentWinner}</p>

                    `;
                }

                else {
                    document.getElementById("selectedTournamentName").innerHTML = `
                        <h2>Selected Tournament:  ${tournamentName}</h2>
                        <h3>Contenders:</h3>
                        <ul>
                            ${contenders.map(contender => `<li>${contender[0]} - ${contender[1]}</li>`).join('')}
                        </ul>
                        <h3>Matches:</h3>
                        <ul>
                            ${matches.map(match => `<li>${match[4]} : ${match[0]} vs ${match[1]} (${match[2]}) - (${match[3]}) | Winner: ${match[5]}</li>`).join('')}
                        </ul>

                        <p>Winner : The tournament is not over yet !</p>

                    `;
                }

            },
            error: (xhr, status, error) => {
                console.error('Error:', error);
            }
        });
    }

}
