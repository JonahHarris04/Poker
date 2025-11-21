# This goes after self.clear() at the top of def on_draw():
# Title Screen
if self.show_title_screen:
    # Simple dark background (override the table drawing)
    arcade.draw_lbwh_rectangle_filled(
        0, SCREEN_WIDTH, SCREEN_HEIGHT, 0, arcade.color.DARK_GREEN
    )

    # Title
    arcade.draw_text(
        "CS 3050 Poker",
        SCREEN_WIDTH // 2,
        SCREEN_HEIGHT // 2 + 80,
        arcade.color.WHITE,
        48,
        anchor_x="center",
        anchor_y="center",
    )

    # Subtitle
    arcade.draw_text(
        "Texas Hold'em",
        SCREEN_WIDTH // 2,
        SCREEN_HEIGHT // 2 + 30,
        arcade.color.LIGHT_GRAY,
        24,
        anchor_x="center",
        anchor_y="center",
    )
    # Instructions
    arcade.draw_text(
        "Use READY to toggle your status.\n"
        "When all players are ready, click START GAME.",
        SCREEN_WIDTH // 2,
        SCREEN_HEIGHT // 2 - 40,
        arcade.color.WHITE,
        18,
        anchor_x="center",
        anchor_y="center",
        align="center",
        width=600,
    )


    arcade.draw_text(self.status_text, 10, 20, arcade.color.WHITE, 16)

    # Draw ready and start buttons
    self.ui.draw()
    return

# This goes with other buttons in __init__
self.placeholder_button = None
self.placeholder_button2 = None

# Flag for showing title screen goes in __init__
self.show_title_screen = True

# Goes with other buttons in def setup_ui()
self.placeholder_button = gui.UIFlatButton(text="Place", width=140)
self.placeholder_button2 = gui.UIFlatButton(text="Place2", width=140)

# Goes with other column additions in setup_ui()
self.left_column.add(self.placeholder_button)
self.left_column.add(self.placeholder_button2)

# goes in on_round() near the top
self.show_title_screen = False

