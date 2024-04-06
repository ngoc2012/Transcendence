// SPDX-License-Identifier: MIT

pragma solidity ^0.8.0;

contract TournamentRegistry {

    // Structure de données pour représenter un joueur
    struct Player {
        string name;
        uint elo;
    }

    // Structure de données pour représenter un match
    struct Match {
        Player player1;
        Player player2;
        uint scorePlayer1;
        uint scorePlayer2;
        string round;
        string winner;
    }

    struct Tournament {
        string TournamentName;
        Player[] contenders;
        Match[] matches;
        string winner;
        bool pending;
        bool started;
    }

    Tournament[] public tournaments;

//Tournament getters

    // Get all tournaments
    function getTournaments() public view returns (Tournament[] memory) {
        return tournaments;
    }

    function deleteTournament(string memory name) public {
        for (uint i = 0; i < tournaments.length; i++) {
            if (keccak256(abi.encodePacked(tournaments[i].TournamentName)) == keccak256(abi.encodePacked(name))) {
                for (uint j = i; j < tournaments.length - 1; j++) {
                    tournaments[j] = tournaments[j + 1];
                }
                tournaments.pop();
                break;
            }
        }
    }
    
    function getActiveTournamentNames() public view returns (string[] memory) {
        uint startedCount = 0;
        for (uint i = 0; i < tournaments.length; i++) {
            if (tournaments[i].started) {
                startedCount++;
            }
        }
        
        string[] memory names = new string[](startedCount);
        uint index = 0;
        for (uint i = 0; i < tournaments.length; i++) {
            if (tournaments[i].started) {
                names[index] = tournaments[i].TournamentName;
                index++;
            }
        }
        return names;
    }


    function getTournamentNames() public view returns (string[] memory) {
        string[] memory names = new string[](tournaments.length);
        for (uint i = 0; i < tournaments.length; i++) {
            names[i] = tournaments[i].TournamentName;
        }
        return names;
    }

    // Get all contenders for a given tournament
    function getContenders(uint tournamentIndex) public view returns (Player[] memory) {
        return tournaments[tournamentIndex].contenders;
    }

    // Get all matches for a given tournament
    function getMatches(uint tournamentIndex) public view returns (Match[] memory) {
        return tournaments[tournamentIndex].matches;
    }

    // Get the winner of a given tournament
    function getTournamentWinner(uint tournamentIndex) public view returns (string memory) {
        return tournaments[tournamentIndex].winner;
    }

    // Get the pending status of a given tournament
    function isTournamentPending(uint tournamentIndex) public view returns (bool) {
        return tournaments[tournamentIndex].pending;
    }


    //Matches getters


    // Get the details of a match by its index
    function getMatchDetails(uint tournamentIndex, uint matchIndex) public view returns (Player memory, Player memory, uint, uint, string memory, string memory) {
        Match memory matchDetails = tournaments[tournamentIndex].matches[matchIndex];
        return (matchDetails.player1, matchDetails.player2, matchDetails.scorePlayer1, matchDetails.scorePlayer2, matchDetails.round, matchDetails.winner);
    }

    // Get the player1 details of a match by its index
    function getMatchPlayer1(uint tournamentIndex, uint matchIndex) public view returns (Player memory) {
        return tournaments[tournamentIndex].matches[matchIndex].player1;
    }

    // Get the player2 details of a match by its index
    function getMatchPlayer2(uint tournamentIndex, uint matchIndex) public view returns (Player memory) {
        return tournaments[tournamentIndex].matches[matchIndex].player2;
    }

    // Get the scores of player1 and player2 in a match by its index
    function getMatchScores(uint tournamentIndex, uint matchIndex) public view returns (uint, uint) {
        Match memory matchDetails = tournaments[tournamentIndex].matches[matchIndex];
        return (matchDetails.scorePlayer1, matchDetails.scorePlayer2);
    }

    // Get the round of a match by its index
    function getMatchRound(uint tournamentIndex, uint matchIndex) public view returns (string memory) {
        return tournaments[tournamentIndex].matches[matchIndex].round;
    }

    // Get the winner of a match by its index
    function getMatchWinner(uint tournamentIndex, uint matchIndex) public view returns (string memory) {
        return tournaments[tournamentIndex].matches[matchIndex].winner;
    }


    //Player getters

    // Get player name by tournament index and player index
    function getPlayerName(uint tournamentIndex, uint playerIndex) public view returns (string memory) {
        return tournaments[tournamentIndex].contenders[playerIndex].name;
    }

    // Get player elo by tournament index and player index
    function getPlayerElo(uint tournamentIndex, uint playerIndex) public view returns (uint) {
        return tournaments[tournamentIndex].contenders[playerIndex].elo;
    }

    // Get player index by name in a given tournament
    function getPlayerIndexByName(uint tournamentIndex, string memory playerName) public view returns (uint) {
        Player[] memory players = tournaments[tournamentIndex].contenders;
        for (uint i = 0; i < players.length; i++) {
            if (keccak256(bytes(players[i].name)) == keccak256(bytes(playerName))) {
                return i;
            }
        }
        revert("Player not found in the tournament");
    }

  

    function getTournamentIndex(string memory tournamentName) public view returns (int) {
        for (uint i = 0; i < tournaments.length; i++) {
            if (keccak256(bytes(tournaments[i].TournamentName)) == keccak256(bytes(tournamentName))) {
                return int(i);
            }
        }
        return -1;
    }

  //  SETTERSTournament setters

    // Setter for adding a new tournament

    function addTournament(string memory newName) public {
        Tournament storage p = tournaments.push();
        p.TournamentName = newName;
        p.pending = true;
        p.started = false;
    }

    function addPlayer(uint tournamentIndex, string memory newName, uint newElo) public {
        Player storage p = tournaments[tournamentIndex].contenders.push();
        p.name = newName;
        p.elo = newElo;
    }

    // // Setter for adding a new match
    function addMatch(uint tournamentIndex, string memory player1Name, string memory player2Name, uint newscorePlayer1, uint newscorePlayer2, string memory newround, string memory newwinner) public {
        Player memory player1;
        Player memory player2;
        uint player1Index;
        uint player2Index;
        for (uint i = 0; i < tournaments[tournamentIndex].contenders.length; i++) {
            if (keccak256(bytes(tournaments[tournamentIndex].contenders[i].name)) == keccak256(bytes(player1Name))) {
                player1 = tournaments[tournamentIndex].contenders[i];
                player1Index = i;
            }
            if (keccak256(bytes(tournaments[tournamentIndex].contenders[i].name)) == keccak256(bytes(player2Name))) {
                player2 = tournaments[tournamentIndex].contenders[i];
                player2Index = i;
            }
        }

        Match storage newMatch = tournaments[tournamentIndex].matches.push();
        newMatch.player1 = player1;
        newMatch.player2 = player2;
        newMatch.scorePlayer1 = newscorePlayer1;
        newMatch.scorePlayer2 = newscorePlayer2;
        newMatch.round = newround;
        newMatch.winner = newwinner;
        tournaments[tournamentIndex].started = true;
    }



    // Setter for updating tournament winner
    function setTournamentWinner(uint tournamentIndex, string memory newWinner) public {
        tournaments[tournamentIndex].winner = newWinner;
    }

    // Setter for updating tournament pending status
    function setTournamentPending(uint tournamentIndex, bool isPending) public {
        tournaments[tournamentIndex].pending = isPending;
    }

    // Setter for updating tournament started status
    function setTournamentStarted(uint tournamentIndex, bool isStarted) public {
        tournaments[tournamentIndex].started = isStarted;
    }
}
