import tkinter as tk
import hashlib
import time
import secrets
from tkinter import messagebox
from PIL import Image, ImageTk  # Importing PIL for image handling

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
            return "Win", 500  # Triple match 7 gives 500 units
        elif spin_result[0] == spin_result[1] == spin_result[2]:
            return "Win", 100  # Triple match gives 100 units
        elif spin_result[0] == spin_result[1] or spin_result[1] == spin_result[2]:
            return "Win", 10  # Two matches give 10 units
        else:
            return "Loss", -5  # No match results in losing 10 units


class SlotMachineGUI:
    def __init__(self, root):
        self.slot_machine = SlotMachine()
        self.blockchain = Blockchain()
        self.balance = 100

        # Set up the main window
        self.root = root
        self.root.title("Blockchain Slot Machine")

        # Set a larger window size
        self.root.geometry("600x400")  # Width x Height

        # Configure grid to center elements
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_columnconfigure(2, weight=1)

        # Load images for the slot machine reels using Pillow
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

        self.balance_label = tk.Label(self.root, text=f"Balance: {self.balance} units", font=("Helvetica", 20))
        self.balance_label.grid(row=3, column=0, columnspan=3)

        # Quit button
        self.quit_button = tk.Button(self.root, text="Quit", command=self.quit_game, font=("Helvetica", 20))
        self.quit_button.grid(row=4, column=0, columnspan=3, pady=20)

    def spin_slot_machine(self):
        # Spin the slot machine
        spin_result = self.slot_machine.spin()

        # Update reel image labels
        self.reel_1_label.config(image=self.images[spin_result[0]])
        self.reel_2_label.config(image=self.images[spin_result[1]])
        self.reel_3_label.config(image=self.images[spin_result[2]])

        # Evaluate the result
        outcome, amount = self.slot_machine.evaluate_spin(spin_result)
        self.balance += amount

        # Update result and balance labels
        self.result_label.config(text=f"{outcome}! You {'won' if amount > 0 else 'lost'} {abs(amount)} units.")
        self.balance_label.config(text=f"Balance: {self.balance} units")

        # Record outcome on blockchain
        last_proof = self.blockchain.get_last_block().proof
        proof = self.blockchain.proof_of_work(last_proof)
        data = {
            "Spin Result": spin_result,
            "Outcome": outcome,
            "Amount": amount,
            "Balance After Spin": self.balance,
        }
        self.blockchain.add_block(data, proof)

        # Check if balance is 0 or negative
        if self.balance <= 0:
            messagebox.showinfo("Game Over", "Your balance is zero. Game over!")
            self.quit_game()

    def quit_game(self):
        # Display blockchain information
        blockchain_info = "\nBlockchain:\n"
        for block in self.blockchain.chain:
            blockchain_info += f"Index: {block.index}, Hash: {block.hash}, Data: {block.data}\n"
        
        messagebox.showinfo("Blockchain", blockchain_info)
        self.root.quit()


def main():
    root = tk.Tk()
    app = SlotMachineGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()