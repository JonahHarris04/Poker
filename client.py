import arcade
import socketio
import threading
from Card import Card
import math
import random
import time

SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
SCREEN_TITLE = "Poker"

# Constants for sizing
CARD_SCALE = 0.6

# Size of the cards
CARD_WIDTH = 140 * CARD_SCALE
CARD_HEIGHT = 190 * CARD_SCALE

# Size of the mat
MAT_PERCENT_OVERSIZE = 1.25
MAT_HEIGHT = int(CARD_HEIGHT * MAT_PERCENT_OVERSIZE)
MAT_WIDTH = int(CARD_WIDTH * MAT_PERCENT_OVERSIZE)

# Space between card mats
VERTICAL_MARGIN_PERCENT = 0.10
HORIZONTAL_MARGIN_PERCENT = 0.10

# The Y of the bottom row (2 piles)
BOTTOM_Y = MAT_HEIGHT / 2 + MAT_HEIGHT * VERTICAL_MARGIN_PERCENT

# The X of where to start putting things on the left side
START_X = MAT_WIDTH / 2 + MAT_WIDTH * HORIZONTAL_MARGIN_PERCENT

# Card constants
CARD_VALUES = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
CARD_SUITS = ["Clubs", "Hearts", "Spades", "Diamonds"]

# Stools around table
SEAT_COUNT = 8
STOOL_RADIUS = 25
STOOL_COLOR = arcade.color.SADDLE_BROWN
STOOL_RING_COLOR = arcade.color.BEIGE
STOOL_RING_THICKNESS = 3

# How far outside the table edge to place the stool centers.
SEAT_CLEARANCE = 35

CARD_BACK_ASSET = ":resources:images/cards/cardBack_red2.png"


class PokerGame(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        self.background_color = arcade.color.CAL_POLY_GREEN

        self.table_center_x = SCREEN_WIDTH // 2
        self.table_center_y = SCREEN_HEIGHT // 2
        self.table_width = 800
        self.table_height = 500
        self.table_color = arcade.color.CAPUT_MORTUUM

        # Card storage for each hand and the deck
        self.hand_cards = arcade.SpriteList()
        self.community_cards = arcade.SpriteList()
        # self.card_list = arcade.SpriteList()

        # Deck variables
        self.deck = []
        self.deck_back_sprites = arcade.SpriteList()

        # List for dealing animations
        self.deal_animations = []

        # Networking
        self.sio = socketio.Client()
        self.server_url = "http://127.0.0.1:5000" # Change to servers IP when flask starts running

        # GUI state
        self.status_text = "Not Connected"
        self.player_name = "Player 1"

        # Thread-safe queue for hands
        self.incoming_hands = []
        self.incoming_lock = threading.Lock()

    def setup(self):
        self.register_socket_events()
        threading.Thread(target=self.connect_to_server, daemon=True).start()
        self.shuffled_deck()

    def register_socket_events(self):
        # List of how the GUI will react to server events

        @self.sio.event
        def connect():
            print("Connected to server.")
            self.status_text = "Connected!"
            self.sio.emit("set_name", {"player_name": self.player_name})

        @self.sio.on("player_list")
        def update_player_list(data):
            print("Player list", data)
            self.status_text = f"Players: {', '.join(data)}"

        @self.sio.on("hand")
        def receive_hand(data):
            print("Received hand", data)
            # Store in thread-safe queue
            with self.incoming_lock:
                self.incoming_hands.append(data["cards"])

        @self.sio.on("your_turn")
        def your_turn(data):
            print(data["message"])
            self.status_text = data["message"]

        @self.sio.on("error")
        def on_error(data):
            print("Error:", data)
            self.status_text = f"Error: {data['message']}"


    def connect_to_server(self):
        # Connect to the SocketIO server
        try:
            self.sio.connect(self.server_url)
        except Exception as e:
            print("Connection failed:", e)
            self.status_text = "Failed to connect."


    def on_update(self, delta_time):

        # Animate active deals
        self.update_deal_animations()

        # Process hands received from server
        with self.incoming_lock:
            while self.incoming_hands:
                cards = self.incoming_hands.pop(0)
                self.display_hand(cards)

    # Creates the deck for the game
    def shuffled_deck(self):
        # Model shuffled deck
        self.deck = [(s, v) for s in CARD_SUITS for v in CARD_VALUES]
        random.shuffle(self.deck)

        # Clear any tabled cards and animations
        self.hand_cards = arcade.SpriteList()
        self.community_cards = arcade.SpriteList()
        self.deal_animations = []

        # Visual deck pile
        self.deck_back_sprites = arcade.SpriteList()
        deck_x = START_X
        deck_y = BOTTOM_Y
        pile_height = min(15, len(self.deck))

        w = int(CARD_WIDTH)
        h = int(CARD_HEIGHT)

        for i in range(pile_height):
            back = arcade.SpriteSolidColor(w, h, arcade.color.DARK_BLUE)
            # layered pile
            back.center_x = deck_x + i * 0.6
            back.center_y = deck_y + i * 0.6
            self.deck_back_sprites.append(back)

    def setup_card_deck(self):
        self.shuffled_deck()


    def on_draw(self):
        # Render screen
        self.clear()

        # Main Table
        center_x = SCREEN_WIDTH // 2
        center_y = SCREEN_HEIGHT // 2
        width = 800  # Width of the ellipse
        height = 500  # Height of the ellipse
        color = arcade.color.CAPUT_MORTUUM
        arcade.draw_ellipse_filled(center_x, center_y, width, height, color)

        # Draw stools
        self.draw_stools_around_table()

        self.deck_back_sprites.draw()

        # # Render deck
        # self.card_list.draw()

        # Render hand
        self.hand_cards.draw()
        # Render deck
        self.community_cards.draw()

        # Draw status
        arcade.draw_text(self.status_text, 10, 20, arcade.color.WHITE, 16)

    def right_of_deck_slots(self, n, gap=30, start_gap=40):
        # Spots for pre_flop() cards
        base_x = START_X + int(CARD_WIDTH / 2) + start_gap + CARD_WIDTH / 2
        y = BOTTOM_Y
        slots = []
        for i in range(n):
            x = base_x + i * (CARD_WIDTH + gap)
            slots.append((x, y))
        return slots

    def community_slots(self):
        # Positions for dealt cards in the middle of table
        total = 5
        gap = 18
        start_x = self.table_center_x - (total * CARD_WIDTH + (total - 1) * gap) / 2 + CARD_WIDTH / 2
        y = self.table_center_y
        return [(start_x + i * (CARD_WIDTH + gap), y) for i in range(total)]

    def display_hand(self, cards):
        # Display cards received from server
        self.hand_cards = arcade.SpriteList()
        start_x = SCREEN_WIDTH // 2 - (len(cards) * 50) // 2
        y = 100
        for i, card_str in enumerate(cards):
            value, _, suit = card_str.partition(" of ")
            card = Card(suit, value, CARD_SCALE)
            card.center_x = start_x + i * 100
            card.center_y = y
            self.hand_cards.append(card)


    # Removes one card from the deck
    def pop_deck_card(self):
        if not self.deck:
            return None
        card_tuple = self.deck.pop()
        # Remove one visual back
        if len(self.deck_back_sprites) > 0:
            self.deck_back_sprites.pop()
        return card_tuple

    # Burn a card
    def burn(self):
        _ = self.pop_deck_card()

    def deal_flop(self):
        if len(self.community_cards) > 0:
            return
        # Burn and turn
        self.burn()
        # define where cards will be placed on table
        center_positions = self.community_slots()[:3]
        for i in range(3):
            card_tup = self.pop_deck_card()
            if card_tup is None:
                self.status_text = "Deck empty."
                return
            suit, value = card_tup
            card = Card(suit, value, CARD_SCALE)
            self.hand_cards.append(card)
            # Actually deals the flop out
            self.enqueue_deal(card, center_positions[i], duration=0.28, delay= i * 0.10)

    def deal_turn(self):
        if len(self.community_cards) != 3:
            return

    def deal_river(self):
        if len(self.community_cards) != 4:
            return



    def on_mouse_press(self, x, y, button, key_modifiers):
        pass


    def on_mouse_release(self, x: float, y: float, button: int, key_modifiers: int):
        pass


    def on_mouse_motion(self, x: float, y: float, dx: float, dy: float):
        pass


    def draw_stools_around_table(self):
        cx, cy = self.table_center_x, self.table_center_y
        rx = self.table_width / 2 + SEAT_CLEARANCE
        ry = self.table_height / 2 + SEAT_CLEARANCE

        for i in range(SEAT_COUNT):
            theta = 2 * math.pi * i / SEAT_COUNT
            x = cx + rx * math.cos(theta)
            y = cy + ry * math.sin(theta)

            # Stool top
            arcade.draw_circle_filled(x, y, STOOL_RADIUS, STOOL_COLOR)
            # Light ring
            arcade.draw_circle_outline(x, y, STOOL_RADIUS, STOOL_RING_COLOR, STOOL_RING_THICKNESS)

            # Cast shadow
            leg_len = 8
            leg_dx = math.cos(theta) * -1
            leg_dy = math.sin(theta) * -1
            arcade.draw_line(x, y, x + leg_dx * leg_len, y + leg_dy * leg_len, STOOL_COLOR, 4)

    # Handles deal animations
    def enqueue_deal(self, sprite: arcade.Sprite, end_xy, duration=0.25, delay=0.0):
        # Deal animation
        start_xy = (START_X, BOTTOM_Y)
        t0 = time.time() + delay
        self.deal_animations.append({
            "sprite": sprite,
            "start": start_xy,
            "end": end_xy,
            "t0": t0,
            "dur": duration
        })
        # Start at deck position
        sprite.center_x, sprite.center_y = start_xy

    # keeps track of ongoing deal animations
    def update_deal_animations(self):
        # List of active deal animations
        now = time.time()
        still_running = []
        for anim in self.deal_animations:
            t0 = anim["t0"]
            dur = anim["dur"]
            if now < t0:
                still_running.append(anim)
                continue
            u = min(1.0, (now - t0) / dur)
            sx, sy = anim["start"]
            ex, ey = anim["end"]
            x = sx + (ex - sx) * u
            y = sy + (ey - sy) * u
            anim["sprite"].center_x = x
            anim["sprite"].center_y = y
            if u < 1.0:
                still_running.append(anim)
        self.deal_animations = still_running


    def on_key_press(self, key, modifiers):
        # Press 'S' tp start the game manually
        if key == arcade.key.S:
            print("Requesting to start game...")
            self.sio.emit("start_game", {})

        # Local dealing (temporary)
        if key == arcade.key.N:  # New deck (reset)
            self.shuffled_deck()
            self.status_text = "New shuffled deck."

        if key == arcade.key.F:
            self.deal_flop()
            self.status_text = "Flop dealt."

        # if key == arcade.key.T:
        #     self.deal_turn()
        #     self.status_text = "Turn dealt."
        #
        # if key == arcade.key.R:
        #     self.deal_river()
        #     self.status_text = "River dealt."



def main():
    window = PokerGame()
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()

