import tkinter as tk
import hashlib
import time
import random
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

class BlackjackGame:
    def __init__(self):
        self.deck = self.create_deck()
        self.player_hand = []
        self.dealer_hand = []
        self.blockchain = Blockchain()

    def create_deck(self):
        # 4 sets of each card: J (10), Q (10), K (10) added along with 2 to 9
        return [2, 3, 4, 5, 6, 7, 8, 9, 10, 'J', 'Q', 'K'] * 4

    def shuffle_deck(self):
        random.shuffle(self.deck)

    def deal_card(self, hand):
        card = self.deck.pop()
        hand.append(card)

    def calculate_hand_value(self, hand):
        total = 0
        aces = 0
        for card in hand:
            if card in ['J', 'Q', 'K']:
                total += 10  # Face cards count as 10
            elif card == 'A':
                total += 11
                aces += 1
            else:
                total += card

        # Handle ace as 1 if total exceeds 21
        while total > 21 and aces:
            total -= 10
            aces -= 1

        return total

    def new_game(self):
        self.player_hand = []
        self.dealer_hand = []
        self.deck = self.create_deck()  # Reset the deck
        self.shuffle_deck()
        self.deal_card(self.player_hand)
        self.deal_card(self.dealer_hand)
        self.deal_card(self.player_hand)
        self.deal_card(self.dealer_hand)

    def play_dealer(self):
        while self.calculate_hand_value(self.dealer_hand) < 17:
            self.deal_card(self.dealer_hand)

    def check_winner(self):
        player_total = self.calculate_hand_value(self.player_hand)
        dealer_total = self.calculate_hand_value(self.dealer_hand)
        
        if player_total > 21:
            return "Player Busts", -1
        elif dealer_total > 21 or player_total > dealer_total:
            return "Player Wins", 1
        elif player_total < dealer_total:
            return "Dealer Wins", -1
        else:
            return "Tie", 0

class BlackjackGUI:
    def __init__(self, root):
        self.game = BlackjackGame()
        self.root = root
        self.root.title("Blockchain Blackjack")
        
        # Increase window size and font
        self.root.geometry("500x400")

        # Player cards
        self.player_cards_label = tk.Label(self.root, text="Player Cards: ", font=("Helvetica", 16))
        self.player_cards_label.pack()

        # Dealer cards (hidden)
        self.dealer_cards_label = tk.Label(self.root, text="Dealer Cards: ", font=("Helvetica", 16))
        self.dealer_cards_label.pack()

        # Status label
        self.status_label = tk.Label(self.root, text="", font=("Helvetica", 16))
        self.status_label.pack()

        # Hit and Stand buttons
        self.hit_button = tk.Button(self.root, text="Hit", command=self.hit, font=("Helvetica", 16))
        self.hit_button.pack(pady=5)

        self.stand_button = tk.Button(self.root, text="Stand", command=self.stand, font=("Helvetica", 16))
        self.stand_button.pack(pady=5)

        # Start new game button
        self.new_game_button = tk.Button(self.root, text="New Game", command=self.new_game, font=("Helvetica", 16))
        self.new_game_button.pack(pady=5)

        # Quit button
        self.quit_button = tk.Button(self.root, text="Quit", command=self.quit_game, font=("Helvetica", 16))
        self.quit_button.pack(pady=5)

    def update_display(self, reveal_dealer=False):
        # Convert face cards to their names ('J', 'Q', 'K') for display
        player_hand_display = [str(card) for card in self.game.player_hand]
        dealer_hand_display = [str(card) for card in self.game.dealer_hand]

        self.player_cards_label.config(text=f"Player Cards: {player_hand_display} (Total: {self.game.calculate_hand_value(self.game.player_hand)})")
        
        # Show only the first card of the dealer's hand unless reveal_dealer is True
        if reveal_dealer:
            dealer_text = f"Dealer Cards: {dealer_hand_display} (Total: {self.game.calculate_hand_value(self.game.dealer_hand)})"
        else:
            dealer_text = f"Dealer Cards: [{dealer_hand_display[0]}, ?]"
        self.dealer_cards_label.config(text=dealer_text)

    def new_game(self):
        # Reset the game state
        self.game.new_game()
        self.update_display(reveal_dealer=False)  # Only show the first dealer card at the start
        self.status_label.config(text="")  # Clear status message
        self.hit_button.config(state=tk.NORMAL)  # Re-enable hit button
        self.stand_button.config(state=tk.NORMAL)  # Re-enable stand button

    def hit(self):
        self.game.deal_card(self.game.player_hand)
        self.update_display(reveal_dealer=False)

        if self.game.calculate_hand_value(self.game.player_hand) > 21:
            self.end_game("Player Busts")

    def stand(self):
        self.game.play_dealer()
        self.end_game(self.game.check_winner()[0])

    def end_game(self, result):
        self.update_display(reveal_dealer=True)  # Reveal dealer's full hand when the game ends
        self.status_label.config(text=result)

        # Disable Hit and Stand buttons after game ends
        self.hit_button.config(state=tk.DISABLED)
        self.stand_button.config(state=tk.DISABLED)

        # Record the result on the blockchain
        last_proof = self.game.blockchain.get_last_block().proof
        proof = self.game.blockchain.proof_of_work(last_proof)
        data = {
            "Player Hand": self.game.player_hand,
            "Dealer Hand": self.game.dealer_hand,
            "Result": result
        }
        self.game.blockchain.add_block(data, proof)

        if result == "Player Busts" or result == "Dealer Wins":
            messagebox.showinfo("Game Over", f"{result}. You lost!")
        elif result == "Player Wins":
            messagebox.showinfo("Game Over", f"{result}. You won!")

    def quit_game(self):
        # Display blockchain information
        blockchain_info = "\nBlockchain:\n"
        for block in self.game.blockchain.chain:
            blockchain_info += f"Index: {block.index}, Hash: {block.hash}, Data: {block.data}\n"
        
        messagebox.showinfo("Blockchain", blockchain_info)
        self.root.quit()

if __name__ == "__main__":
    root = tk.Tk()
    app = BlackjackGUI(root)
    root.mainloop()


