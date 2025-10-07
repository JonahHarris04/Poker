import arcade
from card import Card
import math

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


class pokerGame(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        self.card_list = None
        self.background_color = arcade.color.CAL_POLY_GREEN

        self.table_center_x = SCREEN_WIDTH // 2
        self.table_center_y = SCREEN_HEIGHT // 2
        self.table_width = 800
        self.table_height = 500
        self.table_color = arcade.color.CAPUT_MORTUUM

    def setup(self):

        # 52 card sprite list
        self.card_list = arcade.SpriteList()

        # Create cards
        for card_suit in CARD_SUITS:
            for card_value in CARD_VALUES:
                card = Card(card_suit, card_value, CARD_SCALE)
                card.position = START_X, BOTTOM_Y
                self.card_list.append(card)

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

        # Render deck
        self.card_list.draw()

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


def main():
    window = pokerGame()
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()



