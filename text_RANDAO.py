import tkinter as tk
import hashlib
import time
import secrets
from tkinter import messagebox
from PIL import Image, ImageTk

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

class HorseRace:
    def __init__(self):
        self.reels = [str(i) for i in range(1, 31)]

    def spin(self):
        return [int(secrets.choice(self.reels)) for _ in range(3)]

class HorseRaceGUI:
    def __init__(self, root):
        self.horse_race = HorseRace()
        self.blockchain = Blockchain()
        self.player_positions = [0, 0, 0]  # Positions of player 1, 2, 3
        self.steps_to_win = 200  # Set the goal to 200 steps to win
        self.auto_sprint = False  # Flag to control auto sprint
        self.commitment = None  # Commitment hash for RANDAO

        # Set up the main window
        self.root = root
        self.root.title("Blockchain Horse Race")
        self.root.geometry("1200x500")  # Width x Height
        self.root.eval('tk::PlaceWindow . center')  # Center the window

        # Create a frame for the race track
        self.track_frame = tk.Frame(self.root)
        self.track_frame.grid(row=0, column=1, padx=20, pady=20)

        # Create a race track (a Canvas for each player)
        self.track_length = 800
        self.finish_line_position = self.track_length  # Finish line position
        self.track_canvas = tk.Canvas(self.track_frame, width=self.track_length + 50, height=250)
        self.track_canvas.pack()

        # Create finish line on the canvas
        self.track_canvas.create_line(self.finish_line_position + 50, 0, self.finish_line_position + 50, 250, fill="black", width=8)

        # Create icons for each player
        self.player_icons = {
            1: ImageTk.PhotoImage(Image.open("img/player1.png").resize((50, 50))),
            2: ImageTk.PhotoImage(Image.open("img/player2.png").resize((50, 50))),
            3: ImageTk.PhotoImage(Image.open("img/player3.png").resize((50, 50))),
        }

        # Create icons for each player on the track
        self.player1_icon = self.track_canvas.create_image(0, 50, anchor=tk.NW, image=self.player_icons[1])
        self.player2_icon = self.track_canvas.create_image(0, 100, anchor=tk.NW, image=self.player_icons[2])
        self.player3_icon = self.track_canvas.create_image(0, 150, anchor=tk.NW, image=self.player_icons[3])

        # Create a frame for the step counters
        self.steps_frame = tk.Frame(self.root)
        self.steps_frame.grid(row=0, column=2, padx=20, pady=20, sticky="n")

        # Labels to display the number of steps each player takes
        self.player1_steps_label = tk.Label(self.steps_frame, text="Player 1 Steps: 0", font=("Helvetica", 16), fg="blue")
        self.player1_steps_label.pack(pady=5)

        self.player2_steps_label = tk.Label(self.steps_frame, text="Player 2 Steps: 0", font=("Helvetica", 16), fg="blue")
        self.player2_steps_label.pack(pady=5)

        self.player3_steps_label = tk.Label(self.steps_frame, text="Player 3 Steps: 0", font=("Helvetica", 16), fg="blue")
        self.player3_steps_label.pack(pady=5)

        # Sprint button
        self.sprint_button = tk.Button(self.root, text="Sprint", command=self.start_sprint, font=("Helvetica", 20))
        self.sprint_button.grid(row=1, column=1, pady=20)

        # Quit button
        self.quit_button = tk.Button(self.root, text="Quit", command=self.quit_game, font=("Helvetica", 20))
        self.quit_button.grid(row=2, column=1, pady=20)

    def start_sprint(self):
        self.auto_sprint = True
        self.commitment = hashlib.sha256(str(secrets.randbits(256)).encode()).hexdigest()  # Commitment phase
        self.spin_race()

    def spin_race(self):
        if not self.auto_sprint:
            return

        # Simulate the race step for 3 players
        spin_result = self.horse_race.spin()

        # Update player positions based on spin result
        for i in range(3):
            self.player_positions[i] += spin_result[i]

            # Move the players along the track
            new_position = min(self.player_positions[i] * 4, self.track_length)  # Scale step to canvas width
            if i == 0:
                self.track_canvas.coords(self.player1_icon, new_position, 50)
                self.player1_steps_label.config(text=f"Player 1 Steps: {self.player_positions[i]}")
            elif i == 1:
                self.track_canvas.coords(self.player2_icon, new_position, 100)
                self.player2_steps_label.config(text=f"Player 2 Steps: {self.player_positions[i]}")
            else:
                self.track_canvas.coords(self.player3_icon, new_position, 150)
                self.player3_steps_label.config(text=f"Player 3 Steps: {self.player_positions[i]}")

            # Check if a player has reached or passed the finish line
            if self.player_positions[i] >= self.steps_to_win:
                self.auto_sprint = False  # Stop automatic sprint
                messagebox.showinfo("Race Over", f"Player {i+1} wins!")
                self.record_result(spin_result)
                self.quit_game()
                return

        # Record outcome on blockchain
        last_proof = self.blockchain.get_last_block().proof
        proof = self.blockchain.proof_of_work(last_proof)
        data = {
            "Spin Result": spin_result,
            "Player Positions": self.player_positions.copy(),
            "Commitment": self.commitment
        }
        self.blockchain.add_block(data, proof)

        # Schedule the next sprint after 1 second
        self.root.after(1000, self.spin_race)

    def record_result(self, spin_result):
        # Record the revealed number for RANDAO
        revealed_number = secrets.randbits(256)  # Reveal phase
        commitment_match = hashlib.sha256(str(revealed_number).encode()).hexdigest() == self.commitment

        result_info = f"Commitment: {self.commitment}\nRevealed Number: {revealed_number}\nCommitment Match: {commitment_match}"
        messagebox.showinfo("RANDAO Result", result_info)

    def quit_game(self):
        # Display blockchain information
        blockchain_info = "\nBlockchain:\n"
        for block in self.blockchain.chain:
            blockchain_info += f"Index: {block.index}, Hash: {block.hash}, Data: {block.data}\n"
        
        messagebox.showinfo("Blockchain", blockchain_info)
        self.root.quit()

def main():
    root = tk.Tk()
    app = HorseRaceGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
