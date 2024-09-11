import tkinter as tk
import random
import time
import hashlib
from tkinter import messagebox

class Block:
    def __init__(self, index, previous_hash, timestamp, data, proof):
        self.index = index
        self.previous_hash = previous_hash
        self.timestamp = timestamp
        self.data = data
        self.proof = proof
        self.hash = self.hash_block()

    def hash_block(self):
        block_string = f"{self.index}{self.previous_hash}{self.timestamp}{self.data}{self.proof}"
        return hashlib.sha256(block_string.encode()).hexdigest()

class Blockchain:
    def __init__(self):
        self.chain = []
        self.create_genesis_block()

    def create_genesis_block(self):
        genesis_block = Block(0, "0", time.time(), "Genesis Block", 100)
        self.chain.append(genesis_block)

    def get_last_block(self):
        return self.chain[-1]

    def add_block(self, data, proof):
        last_block = self.get_last_block()
        new_block = Block(len(self.chain), last_block.hash, time.time(), data, proof)
        self.chain.append(new_block)

    def proof_of_work(self, last_proof):
        proof = 0
        while not self.is_valid_proof(last_proof, proof):
            proof += 1
        return proof

    def is_valid_proof(self, last_proof, proof):
        guess = f"{last_proof}{proof}".encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"

class EggGame:
    ANIMALS = ["Cat", "Dog", "Bird", "Fish", "Lizard", "Horse", "Rabbit", "Elephant", "Tiger", "Lion"]

    def __init__(self):
        self.blockchain = Blockchain()
        self.collection = []

    def break_egg(self):
        # Generate random number between 0 and 99
        num = random.randint(0, 99)
        animal_type = self.ANIMALS[num % 10]  # Unit digit defines animal type
        animal_tier = num // 10  # Dozens digit defines animal tier

        animal = {"type": animal_type, "tier": animal_tier}
        self.collection.append(animal)

        # Add the animal to the blockchain
        last_proof = self.blockchain.get_last_block().proof
        proof = self.blockchain.proof_of_work(last_proof)
        self.blockchain.add_block(animal, proof)

        return animal

    def get_blockchain(self):
        blockchain_data = ""
        for block in self.blockchain.chain:
            blockchain_data += f"Index: {block.index}, Hash: {block.hash}, Data: {block.data}\n"
        return blockchain_data

class EggGameGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Egg Breaking Game")
        self.game = EggGame()

        # Set up UI
        self.label = tk.Label(root, text="Click 'Break Egg' to get an animal!", font=("Helvetica", 18))
        self.label.pack(pady=20)

        self.result_label = tk.Label(root, text="", font=("Helvetica", 16))
        self.result_label.pack(pady=10)

        self.break_egg_button = tk.Button(root, text="Break Egg", command=self.break_egg, font=("Helvetica", 18))
        self.break_egg_button.pack(pady=20)

        self.collection_button = tk.Button(root, text="Show Collection", command=self.show_collection, font=("Helvetica", 18))
        self.collection_button.pack(pady=10)

        self.quit_button = tk.Button(root, text="Quit", command=self.quit_game, font=("Helvetica", 18))
        self.quit_button.pack(pady=10)

    def break_egg(self):
        animal = self.game.break_egg()
        result_text = f"Animal: {animal['type']} (Tier {animal['tier']})"
        self.result_label.config(text=result_text)

    def show_collection(self):
        collection_text = "\n".join([f"{a['type']} (Tier {a['tier']})" for a in self.game.collection])
        if not collection_text:
            collection_text = "No animals yet!"
        self.result_label.config(text=collection_text)

    def quit_game(self):
        # Display the blockchain information
        blockchain_data = self.game.get_blockchain()
        messagebox.showinfo("Blockchain", blockchain_data)

        # Quit the game
        self.root.quit()

if __name__ == "__main__":
    root = tk.Tk()
    game_gui = EggGameGUI(root)
    root.mainloop()
