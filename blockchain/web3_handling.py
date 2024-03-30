
from web3 import Web3
import json
from django.http import HttpResponseBadRequest, JsonResponse
from flask import Flask, jsonify, request
import requests
app = Flask(__name__)

ganache_url = 'http://ganache:8545'
web3 = Web3(Web3.HTTPProvider(ganache_url))

def add_tournament_blockchain(name):
    try:
        with open('/app/blockchain/build/contracts/TournamentRegistry.json') as f:
            contract_data = json.load(f)
            contract_abi = contract_data['abi']

        latest_network_id = max(contract_data['networks'].keys())
        contract_address = contract_data['networks'][latest_network_id]['address']
        
        TournamentRegistry = web3.eth.contract(address=contract_address, abi=contract_abi)
        accounts = web3.eth.accounts
        chosen_account = accounts[0]
        tournament_name = name
        tournament_index = TournamentRegistry.functions.getTournamentIndex(tournament_name).call()

        if tournament_index == -1:
            TournamentRegistry.functions.addTournament(tournament_name).transact({'from': chosen_account})
            tournament_index = TournamentRegistry.functions.getTournamentIndex(tournament_name).call()

        TournamentRegistry.functions.setTournamentPending(tournament_index, True).transact({'from': chosen_account})

    except Exception as e:
        print("Error:", e)
        return -1


def add_player_to_tournament_blockchain(name, player, elo):
    try:
        with open('/app/blockchain/build/contracts/TournamentRegistry.json') as f:
            contract_data = json.load(f)
            contract_abi = contract_data['abi']

        print("name acceded : ", name)

        print("player acceded : ", player)

        latest_network_id = max(contract_data['networks'].keys())
        contract_address = contract_data['networks'][latest_network_id]['address']
        
        TournamentRegistry = web3.eth.contract(address=contract_address, abi=contract_abi)
        accounts = web3.eth.accounts
        chosen_account = accounts[0]
        tournament_name = name
        tournament_index = TournamentRegistry.functions.getTournamentIndex(tournament_name).call()

        if tournament_index == -1:
            print("Error:", e)
            return -1

        players = [
            {'name': player, 'elo': elo},
        ]
        for player_data in players:
            TournamentRegistry.functions.addPlayer(tournament_index, player_data['name'], player_data['elo']).transact({'from': chosen_account})

    except Exception as e:
        print("Error:", e)
        return -1




@app.route("/add_player/", methods=["POST"])
def add_player():
    player_data = request.json
    if not player_data:
        return jsonify({"error": "Missing player data"}), 400
    name = player_data.get('name')
    player = player_data.get('player')
    login = player.get('login')
    elo = player.get('elo')
    result = add_player_to_tournament_blockchain(name, login, elo)
    if result == -1:
        return jsonify({"error": "Failed to add player to blockchain"}), 500
    else:
        return jsonify({"message": "Player added successfully"}), 201


def tournament_history():

    try:
        with open('/app/blockchain/build/contracts/TournamentRegistry.json') as f:
            contract_data = json.load(f)
            contract_abi = contract_data['abi']

        latest_network_id = max(contract_data['networks'].keys())
        contract_address = contract_data['networks'][latest_network_id]['address']
        
        TournamentRegistry = web3.eth.contract(address=contract_address, abi=contract_abi)
        tournament_names = TournamentRegistry.functions.getTournamentNames().call()

        return {'names' : tournament_names}

    except Exception as e:
        print("Error:", e)
        return -1

def get_tournament_data(tournament_name):
    try:

        with open('/app/blockchain/build/contracts/TournamentRegistry.json') as f:
            contract_data = json.load(f)
            contract_abi = contract_data['abi']

        latest_network_id = max(contract_data['networks'].keys())
        contract_address = contract_data['networks'][latest_network_id]['address']
        
        TournamentRegistry = web3.eth.contract(address=contract_address, abi=contract_abi)
        tournament_index = TournamentRegistry.functions.getTournamentIndex(tournament_name).call()

        if tournament_index == -1:
            return JsonResponse({"error": "Tournament not found."}, status=400)
        
        contenders = TournamentRegistry.functions.getContenders(tournament_index).call()

        matches = TournamentRegistry.functions.getMatches(tournament_index).call()

        tournament_winner = TournamentRegistry.functions.getTournamentWinner(tournament_index).call()
        is_pending = TournamentRegistry.functions.isTournamentPending(tournament_index).call()

        data = {
            'tournament_name': tournament_name,
            'tournament_winner': tournament_winner,
            'is_pending': is_pending,
            'contenders': contenders,
            'matches': matches
        }
        return data

    except Exception as e:
        return {"error": str(e)}



@app.route("/tournaments/<tournament_name>", methods=["GET"])
def get_tournament_data_route(tournament_name):
    try:
        data = get_tournament_data(tournament_name)

        if not data:
            return HttpResponseBadRequest(json.dumps({"error": "Tournament not found."}))  # Keep JSON for error responses

        return jsonify(data)  # Pass data to template

    except Exception as e:
        print(f"Error retrieving tournament data: {e}")
        return HttpResponseBadRequest(json.dumps({"error": "Internal server error."}))


@app.route("/tournament_history", methods=["GET"])
def tournament_history_route():
    try:
        tournament_data = tournament_history()
        if tournament_data == -1:
            return jsonify({"message": "Error retrieving tournament history"}), 500
        else:
            return jsonify(tournament_data)
    except Exception as e:
        print("Unexpected error:", e)
        return jsonify({"message": "Internal server error"}), 500


@app.route("/add_tournament/<tournament_name>", methods=["POST"])
def add_tournament_route(tournament_name):
    try:
        result = add_tournament_blockchain(tournament_name)

        if result == -1:
            return jsonify({"message": "Error adding tournament"}), 500
        else:
            return jsonify({"message": "Tournament added successfully"}), 201

    except Exception as e:
        print(f"Error adding tournament: {e}")
        return jsonify({"message": "Internal server error"}), 500


    

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9000)




# @database_sync_to_async
# def add_player_2_tournament_blockchain(name, player):
#     print("je suis bien dans la fonction blockchain voici player : ", player.login)
#     try:
#         with open('/app/blockchain/build/contracts/TournamentRegistry.json') as f:
#             contract_data = json.load(f)
#             contract_abi = contract_data['abi']

#         latest_network_id = max(contract_data['networks'].keys())
#         contract_address = contract_data['networks'][latest_network_id]['address']
        
#         TournamentRegistry = web3.eth.contract(address=contract_address, abi=contract_abi)
#         accounts = web3.eth.accounts
#         chosen_account = accounts[0]
#         tournament_name = name
#         tournament_index = TournamentRegistry.functions.getTournamentIndex(tournament_name).call()
#         # print("j'ai bien recup le tournoi")
#         if tournament_index == -1:
#             print("Error:", e)
#             return -1

#         elo = player.elo
#         players = [
#             {'name': player.login, 'elo': elo},
#         ]
#         # print("j'ai bien recup le joueur : ", player.login)
#         for player_data in players:
#             TournamentRegistry.functions.addPlayer(tournament_index, player_data['name'], player_data['elo']).transact({'from': chosen_account})

#     except Exception as e:
#         print("Error:", e)
#         return -1



# @sync_to_async
# def add_winner_to_tournament_blockchain(name, tournament_winner):
#     print("je suis bien dans la fonction add winner")
#     try:
#         with open('/app/blockchain/build/contracts/TournamentRegistry.json') as f:
#             contract_data = json.load(f)
#             contract_abi = contract_data['abi']

#         latest_network_id = max(contract_data['networks'].keys())
#         contract_address = contract_data['networks'][latest_network_id]['address']
        
#         TournamentRegistry = web3.eth.contract(address=contract_address, abi=contract_abi)
#         accounts = web3.eth.accounts
#         chosen_account = accounts[0]
#         tournament_name = name
#         tournament_index = TournamentRegistry.functions.getTournamentIndex(tournament_name).call()
#         if tournament_index == -1:
#             print("Error:", e)
#             return -1

#         TournamentRegistry.functions.setTournamentWinner(tournament_index, tournament_winner).transact({'from': chosen_account})

#         TournamentRegistry.functions.setTournamentPending(tournament_index, False).transact({'from': chosen_account})

#     except Exception as e:
#         print("Error:", e)
#         return -1


# @sync_to_async
# def add_match_to_tournament_blockchain(name, match):
#     print('EH')
#     print('on ajoute un match, le winner est : ', match.winner.login)
#     try:
#         with open('/app/blockchain/build/contracts/TournamentRegistry.json') as f:
#             contract_data = json.load(f)
#             contract_abi = contract_data['abi']

#         latest_network_id = max(contract_data['networks'].keys())
#         contract_address = contract_data['networks'][latest_network_id]['address']
        
#         TournamentRegistry = web3.eth.contract(address=contract_address, abi=contract_abi)
#         accounts = web3.eth.accounts
#         chosen_account = accounts[0]
#         tournament_name = name
#         tournament_index = TournamentRegistry.functions.getTournamentIndex(tournament_name).call()


#         matches = [
#             {'player1': {'name': match.player1.login, 'elo': match.player1.elo}, 'player2': {'name': match.player2.login, 'elo': match.player2.elo}, 'scorePlayer1': match.p1_score, 'scorePlayer2': match.p2_score, 'round': str(match.round_number) , 'winner': match.winner.login}
#         ]
#         # print('bob')
#         for match_data in matches:
#             player1 = match_data['player1']
#             player2 = match_data['player2']
#             TournamentRegistry.functions.addMatch(tournament_index,
#                                                    player1['name'], 
#                                                    player2['name'],
#                                                    match_data['scorePlayer1'], 
#                                                    match_data['scorePlayer2'],
#                                                    match_data['round'], 
#                                                    match_data['winner']).transact({'from': chosen_account})
#     except Exception as e:
#         print("Error:", e)
#         return -1
