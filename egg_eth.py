import tkinter as tk
import hashlib
import time
import secrets
from tkinter import messagebox
from web3 import Web3

# Initialize Web3 connection to Ganache
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:7545"))

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
    ANIMAL_TYPES = ["Cat", "Dog", "Elephant", "Tiger", "Lion", "Bird", "Fish", "Horse", "Rabbit", "Bear"]
    TIERS = ["Common", "Uncommon", "Rare", "Epic", "Legendary"]

    def __init__(self):
        self.eggs = 0
        self.animals = []

    def buy_eggs(self, num_eggs):
        self.eggs += num_eggs

    def break_egg(self):
        if self.eggs <= 0:
            return None
        self.eggs -= 1
        number = secrets.randbelow(100)
        animal = self.ANIMAL_TYPES[number % 10]  # Unit digit determines animal type (0-9)
        tier = self.TIERS[number // 10]  # Dozens digit determines tier (0X-9X)
        return {"Animal": animal, "Tier": tier}

class LoginWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Login")
        self.root.geometry("300x150")

        self.label = tk.Label(self.root, text="Enter Account Address:")
        self.label.pack(pady=10)

        self.account_entry = tk.Entry(self.root, width=40)
        self.account_entry.pack(pady=5)

        self.login_button = tk.Button(self.root, text="Login", command=self.login)
        self.login_button.pack(pady=10)

    def login(self):
        account_address = self.account_entry.get()
        if account_address and w3.is_address(account_address):
            self.root.destroy()
            main_game_window(account_address)
        else:
            messagebox.showerror("Error", "Invalid account address. Please try again.")

class EggGameGUI:
    def __init__(self, root, account_address):
        self.blockchain = Blockchain()
        self.egg_game = EggGame()
        self.account_address = account_address
        self.host_address = "0x84488CcDAe6ABCF8A7cB269bd5dB873A0f968326"

        self.root = root
        self.root.title("Blockchain Egg Game")
        self.root.geometry("400x300")

        self.eggs_label = tk.Label(self.root, text="Eggs: 0", font=("Helvetica", 14))
        self.eggs_label.pack(pady=10)

        self.animals_listbox = tk.Listbox(self.root, height=5)
        self.animals_listbox.pack(pady=10)

        self.break_egg_button = tk.Button(self.root, text="Break Egg", command=self.break_egg)
        self.break_egg_button.pack(pady=10)

        self.buy_eggs_button = tk.Button(self.root, text="Buy 10 Eggs (0.1 ETH)", command=self.buy_eggs)
        self.buy_eggs_button.pack(pady=10)

        self.quit_button = tk.Button(self.root, text="Quit", command=self.quit_game)
        self.quit_button.pack(pady=10)

        self.update_egg_button_state()

    def update_egg_button_state(self):
        if self.egg_game.eggs > 0:
            self.break_egg_button.config(state="normal")
        else:
            self.break_egg_button.config(state="disabled")

    def buy_eggs(self):
        # Send 0.1 ETH to the host address
        try:
            tx = {
                'from': self.account_address,
                'to': self.host_address,
                'value': w3.to_wei(0.1, 'ether'),
                'gas': 2000000,
                'gasPrice': w3.to_wei('50', 'gwei')
            }
            w3.eth.send_transaction(tx)
            self.egg_game.buy_eggs(10)
            self.eggs_label.config(text=f"Eggs: {self.egg_game.eggs}")
            self.update_egg_button_state()
        except Exception as e:
            messagebox.showerror("Error", f"Transaction failed: {e}")

    def break_egg(self):
        result = self.egg_game.break_egg()
        if result:
            animal_info = f"{result['Tier']} {result['Animal']}"
            self.animals_listbox.insert(tk.END, animal_info)
            self.record_blockchain(animal_info)
            self.eggs_label.config(text=f"Eggs: {self.egg_game.eggs}")
            self.update_egg_button_state()

    def record_blockchain(self, animal_info):
        last_proof = self.blockchain.get_last_block().proof
        proof = self.blockchain.proof_of_work(last_proof)
        data = {"Animal": animal_info, "Player": self.account_address}
        self.blockchain.add_block(data, proof)

    def quit_game(self):
        blockchain_info = "\nBlockchain:\n"
        for block in self.blockchain.chain:
            blockchain_info += f"Index: {block.index}, Hash: {block.hash}, Data: {block.data}\n"

        messagebox.showinfo("Blockchain", blockchain_info)
        self.root.quit()

def main_game_window(account_address):
    root = tk.Tk()
    app = EggGameGUI(root, account_address)
    root.mainloop()

def main():
    login_root = tk.Tk()
    login_window = LoginWindow(login_root)
    login_root.mainloop()

if __name__ == "__main__":
    main()
