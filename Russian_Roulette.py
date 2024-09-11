import tkinter as tk
import hashlib
import time
import secrets
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

class RussianRoulette:
    def __init__(self):
        self.gun1_chambers = [0] * 6  # Empty chambers for Gun 1
        self.gun2_chambers = [0] * 6  # Empty chambers for Gun 2
        self.place_bullets()

    def place_bullets(self):
        # Randomly place a bullet in one chamber of each gun
        bullet_position1 = secrets.randbelow(6)
        bullet_position2 = secrets.randbelow(6)
        self.gun1_chambers[bullet_position1] = 1
        self.gun2_chambers[bullet_position2] = 1

    def pull_trigger(self, gun):
        # Randomly choose a chamber to "fire"
        chamber = secrets.randbelow(6)
        bullet_fired = gun[chamber] == 1
        return chamber, bullet_fired

class RussianRouletteGUI:
    def __init__(self, root):
        self.roulette = RussianRoulette()
        self.blockchain = Blockchain()
        self.lives = {"Player 1": 1, "Player 2": 1}  # Each player starts with 1 life

        # Set up the main window
        self.root = root
        self.root.title("Blockchain Russian Roulette")

        # Create game labels and buttons
        self.info_label = tk.Label(self.root, text="Welcome to Russian Roulette!", font=("Helvetica", 20))
        self.info_label.pack(pady=20)

        # Result labels for each player
        self.result_label_player1 = tk.Label(self.root, text="", font=("Helvetica", 20), fg="red")
        self.result_label_player1.pack(pady=10)

        self.result_label_player2 = tk.Label(self.root, text="", font=("Helvetica", 20), fg="blue")
        self.result_label_player2.pack(pady=10)

        # Fire both guns button
        self.fire_both_button = tk.Button(self.root, text="Fire Both Guns", command=self.fire_both_guns, font=("Helvetica", 16))
        self.fire_both_button.pack(pady=10)

        self.lives_label = tk.Label(self.root, text=f"Player 1 Lives: {self.lives['Player 1']} | Player 2 Lives: {self.lives['Player 2']}", font=("Helvetica", 16))
        self.lives_label.pack(pady=20)

        # Quit button
        self.quit_button = tk.Button(self.root, text="Quit", command=self.quit_game, font=("Helvetica", 16))
        self.quit_button.pack(pady=20)

    def fire_both_guns(self):
        # Fire gun 1 for Player 1
        chamber1, bullet_fired1 = self.roulette.pull_trigger(self.roulette.gun1_chambers)
        outcome1 = "Survived" if not bullet_fired1 else "Lost"

        # Fire gun 2 for Player 2
        chamber2, bullet_fired2 = self.roulette.pull_trigger(self.roulette.gun2_chambers)
        outcome2 = "Survived" if not bullet_fired2 else "Lost"

        # Increment block index for each click
        block_index = len(self.blockchain.chain)

        # Update blockchain for Player 1
        last_proof = self.blockchain.get_last_block().proof
        proof = self.blockchain.proof_of_work(last_proof)
        data1 = {
            "Block Index": block_index,
            "Player": "Player 1",
            "Gun": 1,
            "Chamber Fired": chamber1,
            "Bullet Location": self.roulette.gun1_chambers,
            "Outcome": outcome1,
            "Lives Before Spin": self.lives["Player 1"],
        }

        # Update blockchain for Player 2
        data2 = {
            "Block Index": block_index + 1,  # Increment the block index for Player 2
            "Player": "Player 2",
            "Gun": 2,
            "Chamber Fired": chamber2,
            "Bullet Location": self.roulette.gun2_chambers,
            "Outcome": outcome2,
            "Lives Before Spin": self.lives["Player 2"],
        }

        # Adjust lives and record outcomes
        if outcome1 == "Lost":
            self.lives["Player 1"] -= 1  # Player 1 loses a life
            data1["Lives After Spin"] = self.lives["Player 1"]
            self.result_label_player1.config(text=f"Player 1 LOST! Bullet was in chamber {chamber1}.")
            self.blockchain.add_block(data1, proof)

            # Check if Player 1 has no lives left
            if self.lives["Player 1"] <= 0:
                messagebox.showinfo("Game Over", "Player 1 has no more lives. Game over!")
                self.quit_game()
                return
        else:
            self.result_label_player1.config(text=f"Player 1 survived! No bullet in chamber {chamber1}.")
            self.blockchain.add_block(data1, proof)

        if outcome2 == "Lost":
            self.lives["Player 2"] -= 1  # Player 2 loses a life
            data2["Lives After Spin"] = self.lives["Player 2"]
            self.result_label_player2.config(text=f"Player 2 LOST! Bullet was in chamber {chamber2}.")
            self.blockchain.add_block(data2, proof)

            # Check if Player 2 has no lives left
            if self.lives["Player 2"] <= 0:
                messagebox.showinfo("Game Over", "Player 2 has no more lives. Game over!")
                self.quit_game()
                return
        else:
            self.result_label_player2.config(text=f"Player 2 survived! No bullet in chamber {chamber2}.")
            self.blockchain.add_block(data2, proof)

        # Update lives label
        self.lives_label.config(text=f"Player 1 Lives: {self.lives['Player 1']} | Player 2 Lives: {self.lives['Player 2']}")

    def quit_game(self):
        # Display blockchain information
        blockchain_info = "\nBlockchain:\n"
        for block in self.blockchain.chain:
            blockchain_info += f"Index: {block.index}, Hash: {block.hash}, Data: {block.data}\n"
        
        messagebox.showinfo("Blockchain", blockchain_info)
        self.root.quit()

def main():
    root = tk.Tk()
    app = RussianRouletteGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
