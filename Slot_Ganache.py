
import tkinter as tk
import hashlib
import time
import secrets
from tkinter import messagebox
from PIL import Image, ImageTk
from web3 import Web3

# Ganache connection
web3 = Web3(Web3.HTTPProvider("http://127.0.0.1:7545"))

if web3.is_connected():
    print("Connected to Ethereum blockchain via Ganache")
else:
    raise Exception("Failed to connect to Ganache")

web3.eth.default_account = '0x5f4075d2D8e2597032a0A05F26D366e7edE924B5'


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


class SlotMachine:
    def __init__(self):
        self.reels = ["Cherry", "Lemon", "Orange", "Plum", "Grape", "Coin", "Gold", "Heart", "Spade", "Diamond", "Club", "Bell", "Bar", "7"]

    def spin(self):
        return [secrets.choice(self.reels) for _ in range(3)]

    def evaluate_spin(self, spin_result):
        if spin_result[0] == spin_result[1] == spin_result[2] == "7":
            return "Win", 1000  # Triple match 7 gives 500 units
        elif spin_result[0] == spin_result[1] == spin_result[2]:
            return "Win", 100  # Triple match gives 100 units
        elif spin_result[0] == spin_result[1] or spin_result[1] == spin_result[2] or spin_result[0] == spin_result[2]:
            return "Win", 10  # Two matches give 10 units
        else:
            return "Loss", -5  # No match results in losing 5 units


class BlockchainSlotMachine:
    def __init__(self, player_account):
        self.slot_machine = SlotMachine()
        self.balance = 1.0  # Start with 1 ETH
        self.host_account = '0x84488CcDAe6ABCF8A7cB269bd5dB873A0f968326'
        self.player_account = player_account

    def spin_slot_machine(self):
        spin_result = self.slot_machine.spin()
        outcome, amount = self.slot_machine.evaluate_spin(spin_result)

        # If player wins, host sends ETH to player
        if amount > 0:
            self.balance += amount / 1000  # Simulate Ethereum balance increment

            txn = {
                'from': self.host_account,
                'to': self.player_account,
                'value': web3.to_wei(amount / 1000, 'ether'),  # Host sends winnings to player
                'gas': 2000000,
                'gasPrice': web3.to_wei('50', 'gwei')
            }
            tx_hash = web3.eth.send_transaction(txn)

        # If player loses, player sends 0.01 ETH to the host
        else:
            self.balance -= 0.01  # Simulate losing 0.01 ETH per loss

            txn = {
                'from': self.player_account,
                'to': self.host_account,
                'value': web3.to_wei(0.01, 'ether'),  # Correct method for converting to Wei
                'gas': 2000000,
                'gasPrice': web3.to_wei('50', 'gwei')  # Correct method for converting gasPrice to Wei
            }
            tx_hash = web3.eth.send_transaction(txn)

        return spin_result, outcome, amount, tx_hash


class SlotMachineGUI:
    def __init__(self, root):
        self.blockchain = Blockchain()

        # Prompt player to enter their Ethereum account address
        self.account_prompt = tk.Toplevel(root)
        self.account_prompt.title("Enter Ethereum Account")
        self.account_prompt.geometry("400x200")

        self.account_label = tk.Label(self.account_prompt, text="Enter your Ethereum Account Address:", font=("Helvetica", 12))
        self.account_label.pack(pady=10)

        self.account_entry = tk.Entry(self.account_prompt, width=40, font=("Helvetica", 12))
        self.account_entry.pack(pady=10)

        self.confirm_button = tk.Button(self.account_prompt, text="Confirm", command=self.start_game, font=("Helvetica", 12))
        self.confirm_button.pack(pady=20)

        # Set up the main window but don't show it yet
        self.root = root
        self.root.title("Blockchain Slot Machine")
        self.root.geometry("1200x400")
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_columnconfigure(2, weight=1)
        self.root.withdraw()  # Hide main window until the account is entered

    def start_game(self):
        player_account = self.account_entry.get()

        # Validate if the Ethereum address is valid
        if web3.is_address(player_account):
            self.slot_machine = BlockchainSlotMachine(player_account)
            self.root.deiconify()  # Show the main window
            self.account_prompt.destroy()  # Close the prompt window

            # Set up the slot machine interface
            self.setup_slot_machine_gui()
        else:
            messagebox.showerror("Invalid Address", "Please enter a valid Ethereum account address.")

    def setup_slot_machine_gui(self):
        # Set up slot machine images (reel icons)
        self.images = {
            "Cherry": ImageTk.PhotoImage(Image.open("img/cherry.png").resize((64, 64))),
            "Lemon": ImageTk.PhotoImage(Image.open("img/lemon.png").resize((64, 64))),
            "Orange": ImageTk.PhotoImage(Image.open("img/orange.png").resize((64, 64))),
            "Plum": ImageTk.PhotoImage(Image.open("img/plum.png").resize((64, 64))),
            "Grape": ImageTk.PhotoImage(Image.open("img/grape.png").resize((64, 64))),
            "Coin": ImageTk.PhotoImage(Image.open("img/coin.png").resize((64, 64))),
            "Gold": ImageTk.PhotoImage(Image.open("img/gold.png").resize((64, 64))),
            "Heart": ImageTk.PhotoImage(Image.open("img/heart.png").resize((64, 64))),
            "Spade": ImageTk.PhotoImage(Image.open("img/spade.png").resize((64, 64))),
            "Diamond": ImageTk.PhotoImage(Image.open("img/diamond.png").resize((64, 64))),
            "Club": ImageTk.PhotoImage(Image.open("img/club.png").resize((64, 64))),
            "Bell": ImageTk.PhotoImage(Image.open("img/bell.png").resize((64, 64))),
            "Bar": ImageTk.PhotoImage(Image.open("img/bar.png").resize((64, 64))),
            "7": ImageTk.PhotoImage(Image.open("img/7.png").resize((64, 64))),
        }

        # Image labels for the reels
        self.reel_1_label = tk.Label(self.root)
        self.reel_1_label.grid(row=0, column=0, padx=20)
        self.reel_2_label = tk.Label(self.root)
        self.reel_2_label.grid(row=0, column=1, padx=20)
        self.reel_3_label = tk.Label(self.root)
        self.reel_3_label.grid(row=0, column=2, padx=20)

        # Spin button
        self.spin_button = tk.Button(self.root, text="Spin", command=self.spin_slot_machine, font=("Helvetica", 20))
        self.spin_button.grid(row=1, column=0, columnspan=3, pady=20)

        # Labels for displaying results
        self.result_label = tk.Label(self.root, text="", font=("Helvetica", 20))
        self.result_label.grid(row=2, column=0, columnspan=3)
        self.balance_label = tk.Label(self.root, text=f"Balance: {self.slot_machine.balance} ETH", font=("Helvetica", 20))
        self.balance_label.grid(row=3, column=0, columnspan=3)

        # Quit button
        self.quit_button = tk.Button(self.root, text="Quit", command=self.quit_game, font=("Helvetica", 20))
        self.quit_button.grid(row=4, column=0, columnspan=3, pady=20)

    def spin_slot_machine(self):
        spin_result, outcome, amount, tx_hash = self.slot_machine.spin_slot_machine()

        # Update reel image labels
        self.reel_1_label.config(image=self.images[spin_result[0]])
        self.reel_2_label.config(image=self.images[spin_result[1]])
        self.reel_3_label.config(image=self.images[spin_result[2]])

        # Update result and balance labels
        self.result_label.config(text=f"{outcome}! Transaction: {tx_hash.hex()}")
        self.balance_label.config(text=f"Balance: {self.slot_machine.balance} ETH")

        # Record the outcome and blockchain transaction details
        last_proof = self.blockchain.get_last_block().proof
        proof = self.blockchain.proof_of_work(last_proof)
        data = {
            "Spin Result": spin_result,
            "Outcome": outcome,
            "Amount": amount,
            "Transaction Hash": tx_hash.hex(),
            "Balance After Spin": self.slot_machine.balance
        }
        self.blockchain.add_block(data, proof)

        # Check if balance falls below 0 and end the game
        if self.slot_machine.balance <= 0:
            messagebox.showinfo("Game Over", "You have run out of balance! Game Over.")
            self.quit_game()

    def quit_game(self):
        # Display the blockchain record in a new window
        blockchain_window = tk.Toplevel(self.root)
        blockchain_window.title("Blockchain Records")
        blockchain_window.geometry("600x400")

        # Create a text widget to display the blockchain data
        blockchain_text = tk.Text(blockchain_window, wrap=tk.WORD, font=("Helvetica", 10))
        blockchain_text.pack(fill=tk.BOTH, expand=True)

        # Loop through each block and append its data to the text widget
        for block in self.blockchain.chain:
            blockchain_text.insert(tk.END, f"Block {block.index}:\n")
            blockchain_text.insert(tk.END, f"  Timestamp: {time.ctime(block.timestamp)}\n")
            blockchain_text.insert(tk.END, f"  Data: {block.data}\n")
            blockchain_text.insert(tk.END, f"  Proof: {block.proof}\n")
            blockchain_text.insert(tk.END, f"  Hash: {block.hash}\n")
            blockchain_text.insert(tk.END, "-"*50 + "\n")

        # Add a quit button to close the blockchain window
        close_button = tk.Button(blockchain_window, text="Close", command=blockchain_window.destroy, font=("Helvetica", 12))
        close_button.pack(pady=10)

        # Quit the main game
        self.root.quit()


if __name__ == "__main__":
    root = tk.Tk()
    app = SlotMachineGUI(root)
    root.mainloop()
