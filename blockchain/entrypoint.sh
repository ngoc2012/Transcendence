#!/bin/bash

cd /app/blockchain/.

contract_json="build/contracts/TournamentRegistry.json"

if [ ! -f "$contract_json" ]; then
    echo "Deploying smart contracts..."
    truffle deploy
else
    echo "Contracts already deployed. Skipping deployment."
fi

cd /.

python3 web3_handling.py &

exec "$@"
