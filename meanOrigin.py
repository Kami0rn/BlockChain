import hashlib
from flask import Flask, jsonify
from datetime import datetime

class Block:
    def __init__(self, index, previous_hash, timestamp, data, hash, nonce):
        self.index = index
        self.previous_hash = previous_hash
        self.timestamp = timestamp
        self.data = data
        self.hash = hash
        self.nonce = nonce

def calculate_hash(index, previous_hash, timestamp, data, nonce):
    value = str(index) + str(previous_hash) + str(timestamp) + str(data) + str(nonce)
    return hashlib.sha256(value.encode('utf-8')).hexdigest()

def create_genesis_block():
    return Block(0, "0", datetime.now(), "Genesis Block", calculate_hash(0, "0", datetime.now(), "Genesis Block", 0), 0)

def create_new_block(previous_block, data):
    index = previous_block.index + 1
    timestamp = datetime.now()
    nonce = 0
    hash = calculate_hash(index, previous_block.hash, timestamp, data, nonce)
    
    # Proof of work: Keep incrementing nonce until the hash meets certain criteria (e.g., starts with '000')
    while not hash.startswith('000'):
        nonce += 1
        hash = calculate_hash(index, previous_block.hash, timestamp, data, nonce)
    
    return Block(index, previous_block.hash, timestamp, data, hash, nonce)

app = Flask(__name__)

# Create the blockchain and add a genesis block
blockchain = [create_genesis_block()]
previous_block = blockchain[0]

@app.route('/')
def hello():
    return "<h1>Hello Blockchain</h1>"

@app.route('/get', methods=['GET'])
def get_chain():
    chain_data = []
    for block in blockchain:
        chain_data.append({
            'index': block.index,
            'previous_hash': block.previous_hash,
            'timestamp': block.timestamp,
            'data': block.data,
            'hash': block.hash,
            'nonce': block.nonce
        })
    return jsonify({'chain': chain_data, 'length': len(chain_data)})

@app.route('/mine', methods=['GET'])
def mine():
    global previous_block  # Declare previous_block as a global variable
    new_data = f"Block #{len(blockchain) + 1} data"
    new_block = create_new_block(previous_block, new_data)
    blockchain.append(new_block)
    previous_block = new_block
    response = {
        'message': 'New block mined!',
        'index': new_block.index,
        'previous_hash': new_block.previous_hash,
        'timestamp': new_block.timestamp,
        'data': new_block.data,
        'hash': new_block.hash,
        'nonce': new_block.nonce
    }
    return jsonify(response), 200

@app.route('/valid', methods=['GET'])
def is_chain_valid():
    for i in range(1, len(blockchain)):
        current_block = blockchain[i]
        previous_block = blockchain[i - 1]

        # Check if the current block's previous_hash matches the hash of the previous block
        if current_block.previous_hash != previous_block.hash:
            response = {'message': 'Blockchain is not valid!'}
            return jsonify(response), 400

        # Check if the current block's hash is valid
        if current_block.hash != calculate_hash(current_block.index, current_block.previous_hash, current_block.timestamp, current_block.data, current_block.nonce):
            response = {'message': 'Blockchain is not valid!'}
            return jsonify(response), 400

    response = {'message': 'Blockchain is valid!'}
    return jsonify(response), 200

if __name__ == '__main__':
    app.run()

# link : https://chat.openai.com/c/8fc7496d-403c-4baf-85bf-ae4972af5a51