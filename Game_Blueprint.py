import arcade
import mysql.connector # will update with supabase 11/5
from hangman_agent import hangman_agent

SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700
SCREEN_TITLE = "The Last Rodeo - Hangman Duel"

class HangmanGame(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        arcade.set_background_color(arcade.color.SAND)
        
        # Game state
        self.phrase = ""
        self.human_guessed = set()
        self.ai_guessed = set()
        self.human_attempts = 6
        self.ai_attempts = 6
        self.current_turn = "human"
        self.game_over = False
        self.winner = None
        
        # Database connection
        self.conn = None
        self.cursor = None
        
        # Visual elements
        self.message = "Press SPACE to start a new game!"
        self.ai_delay_timer = 0
        self.ai_should_move = False
        
        # Load cowboy parts (png)
        self.cowboy_images = {}
        try:
            self.cowboy_images['head'] = arcade.load_texture("cbhead.png")
            self.cowboy_images['hat'] = arcade.load_texture("cbhat.png")
            self.cowboy_images['larm'] = arcade.load_texture("cblarm.png")
            self.cowboy_images['rarm'] = arcade.load_texture("cbrarm.png")
            self.cowboy_images['lleg'] = arcade.load_texture("cblleg.png")
            self.cowboy_images['rleg'] = arcade.load_texture("cbrleg.png")
            self.cowboy_images['lfoot'] = arcade.load_texture("cblfoot.png")
            self.cowboy_images['rfoot'] = arcade.load_texture("cbrfoot.png")
        except Exception as e:
            print(f"Error loading images: {e}")
            self.message = f"Error loading images: {e}"
        
    def setup(self):
        """Initialize game with a new phrase"""
        try:
            self.conn = mysql.connector.connect(
                host="Hangmanhost",
                user="HangmanTeam",
                password="DKDonkeyKong",
                database="hangDb"
            )
            self.cursor = self.conn.cursor()
            self.phrase = self.get_random_phrase()
            
            if not self.phrase:
                self.message = "No phrases in database!"
                return
                
        except Exception as e:
            self.message = f"Database error: {str(e)}"
            return
        
        # Reset game state
        self.human_guessed = set()
        self.ai_guessed = set()
        self.human_attempts = 6
        self.ai_attempts = 6
        self.current_turn = "human"
        self.game_over = False
        self.winner = None
        self.message = "Your turn! Type a letter..."
        self.ai_delay_timer = 0
        self.ai_should_move = False
        
    def get_random_phrase(self):
        """Fetch random phrase from database"""
        self.cursor.execute("SELECT phraseText FROM phrases ORDER BY RAND() LIMIT 1;")
        res = self.cursor.fetchone()
        return res[0] if res else None
    
    def display_progress(self, guessed_set):
        """Return the phrase with unguessed letters as underscores"""
        return ' '.join([
            char if not char.isalpha() or char.lower() in guessed_set else '_'
            for char in self.phrase
        ])
    
    def check_win_condition(self):
        """Check if game is over"""
        all_guessed = self.human_guessed | self.ai_guessed
        revealed = ''.join([
            char if not char.isalpha() or char.lower() in all_guessed else '_'
            for char in self.phrase
        ])
        
        if '_' not in revealed:
            self.game_over = True
            self.winner = self.current_turn
        elif self.human_attempts <= 0:
            self.game_over = True
            self.winner = "ai"
        elif self.ai_attempts <= 0:
            self.game_over = True
            self.winner = "human"
    
    def draw_cowboy_images(self, x, y, mistakes): # will update posiiton based on final image size
        """Display cowboy parts as images based on mistakes"""
        # Order: head, hat, left arm, right arm, left leg, right leg, left foot, right foot
        
        if mistakes >= 1 and 'head' in self.cowboy_images:
            # Head
            arcade.draw_lrwh_rectangle_textured(
                x - 15, y + 35, 30, 30, self.cowboy_images['head']
            )
        
        if mistakes >= 2 and 'hat' in self.cowboy_images:
            # Hat
            arcade.draw_lrwh_rectangle_textured(
                x - 20, y + 65, 40, 25, self.cowboy_images['hat']
            )
        
        if mistakes >= 3 and 'larm' in self.cowboy_images:
            # Left arm
            arcade.draw_lrwh_rectangle_textured(
                x - 40, y + 5, 25, 30, self.cowboy_images['larm']
            )
        
        if mistakes >= 4 and 'rarm' in self.cowboy_images:
            # Right arm
            arcade.draw_lrwh_rectangle_textured(
                x + 15, y + 5, 25, 30, self.cowboy_images['rarm']
            )
        
        if mistakes >= 5 and 'lleg' in self.cowboy_images:
            # Left leg
            arcade.draw_lrwh_rectangle_textured(
                x - 25, y - 40, 20, 35, self.cowboy_images['lleg']
            )
        
        if mistakes >= 6 and 'rleg' in self.cowboy_images:
            # Right leg
            arcade.draw_lrwh_rectangle_textured(
                x + 5, y - 40, 20, 35, self.cowboy_images['rleg']
            )
        
        if mistakes >= 7 and 'lfoot' in self.cowboy_images:
            # Left foot
            arcade.draw_lrwh_rectangle_textured(
                x - 30, y - 55, 25, 15, self.cowboy_images['lfoot']
            )
        
        if mistakes >= 8 and 'rfoot' in self.cowboy_images:
            # Right foot
            arcade.draw_lrwh_rectangle_textured(
                x + 5, y - 55, 25, 15, self.cowboy_images['rfoot']
            )
    
    def process_guess(self, guess):
        """Handle a guess from current player"""
        guess = guess.lower()
        all_guessed = self.human_guessed | self.ai_guessed
        
        if guess in all_guessed:
            self.message = "Letter already guessed!"
            return
        
        if self.current_turn == "human":
            self.human_guessed.add(guess)
        else:
            self.ai_guessed.add(guess)
        
        is_correct = any(char.lower() == guess for char in self.phrase if char.isalpha())
        
        if is_correct:
            self.message = f"{'You' if self.current_turn == 'human' else 'AI'} got '{guess.upper()}'! Go again."
        else:
            if self.current_turn == "human":
                self.human_attempts -= 1
                self.current_turn = "ai"
                self.message = f"Wrong! AI's turn..."
                self.ai_delay_timer = 1.0  # 1 second delay before AI moves
                self.ai_should_move = True
            else:
                self.ai_attempts -= 1
                self.current_turn = "human"
                self.message = f"AI missed '{guess.upper()}'! Your turn."
        
        self.check_win_condition()
    
    def ai_turn(self):
        """Execute AI's turn"""
        all_guessed = self.human_guessed | self.ai_guessed
        current_revealed = ''.join([
            char if not char.isalpha() or char.lower() in all_guessed else '_'
            for char in self.phrase
        ])
        
        guess = hangman_agent(all_guessed, current_revealed, self.phrase)
        if guess:
            guess = guess.lower()
            self.message = f"AI guesses: {guess.upper()}"
            self.process_guess(guess)
        self.ai_should_move = False
    
    def on_draw(self):
        """Render the game"""
        self.clear()
        
        # Title
        arcade.draw_text(
            " THE LAST RODEO ",
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT - 40,
            arcade.color.DARK_RED,
            font_size=36,
            anchor_x="center",
            bold=True
        )
        
        if not self.phrase:
            arcade.draw_text(
                self.message,
                SCREEN_WIDTH // 2,
                SCREEN_HEIGHT // 2,
                arcade.color.BLACK,
                font_size=20,
                anchor_x="center"
            )
            return
        
        # Display phrase progress
        all_guessed = self.human_guessed | self.ai_guessed
        progress = self.display_progress(all_guessed)
        arcade.draw_text(
            progress,
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT - 120,
            arcade.color.BLACK,
            font_size=32,
            anchor_x="center",
            bold=True
        )
        
        # Human side (left)
        arcade.draw_text(
            "YOU",
            200,
            SCREEN_HEIGHT - 200,
            arcade.color.BLUE_VIOLET,
            font_size=24,
            anchor_x="center",
            bold=True
        )
        
        # Draw cowboy with pngs
        human_mistakes = 6 - self.human_attempts
        self.draw_cowboy_images(200, SCREEN_HEIGHT - 280, human_mistakes)
        
        arcade.draw_text(
            f"Lives: {self.human_attempts}",
            200,
            SCREEN_HEIGHT - 460,
            arcade.color.BLACK,
            font_size=18,
            anchor_x="center"
        )
        
        guessed_text = ', '.join(sorted(self.human_guessed)) if self.human_guessed else "none"
        arcade.draw_text(
            f"Guessed: {guessed_text}",
            200,
            SCREEN_HEIGHT - 490,
            arcade.color.BLACK,
            font_size=14,
            anchor_x="center",
            width=300,
            align="center"
        )
        
        # AI side (right)
        arcade.draw_text(
            "AI OUTLAW",
            SCREEN_WIDTH - 200,
            SCREEN_HEIGHT - 200,
            arcade.color.RED,
            font_size=24,
            anchor_x="center",
            bold=True
        )
        
        # Draw AI cowboy with images
        ai_mistakes = 6 - self.ai_attempts
        self.draw_cowboy_images(SCREEN_WIDTH - 200, SCREEN_HEIGHT - 280, ai_mistakes)
        
        arcade.draw_text(
            f"Lives: {self.ai_attempts}",
            SCREEN_WIDTH - 200,
            SCREEN_HEIGHT - 460,
            arcade.color.BLACK,
            font_size=18,
            anchor_x="center"
        )
        
        ai_guessed_text = ', '.join(sorted(self.ai_guessed)) if self.ai_guessed else "none"
        arcade.draw_text(
            f"Guessed: {ai_guessed_text}",
            SCREEN_WIDTH - 200,
            SCREEN_HEIGHT - 490,
            arcade.color.BLACK,
            font_size=14,
            anchor_x="center",
            width=300,
            align="center"
        )
        
        # Turn indicator
        turn_color = arcade.color.BLUE_VIOLET if self.current_turn == "human" else arcade.color.RED
        arcade.draw_text(
            f"{'YOUR' if self.current_turn == 'human' else 'AI'} TURN",
            SCREEN_WIDTH // 2,
            100,
            turn_color,
            font_size=20,
            anchor_x="center",
            bold=True
        )
        
        # Message/Status
        arcade.draw_text(
            self.message,
            SCREEN_WIDTH // 2,
            60,
            arcade.color.BLACK,
            font_size=16,
            anchor_x="center"
        )
        
        # Game over screen
        if self.game_over:
            arcade.draw_rectangle_filled(
                SCREEN_WIDTH // 2,
                SCREEN_HEIGHT // 2,
                500,
                250,
                (240, 240, 240, 250)
            )
            arcade.draw_rectangle_outline(
                SCREEN_WIDTH // 2,
                SCREEN_HEIGHT // 2,
                500,
                250,
                arcade.color.BLACK,
                4
            )
            
            win_text = " YOU WIN! " if self.winner == "human" else " AI WINS! "
            win_color = arcade.color.GREEN if self.winner == "human" else arcade.color.RED
            arcade.draw_text(
                win_text,
                SCREEN_WIDTH // 2,
                SCREEN_HEIGHT // 2 + 60,
                win_color,
                font_size=36,
                anchor_x="center",
                bold=True
            )
            arcade.draw_text(
                f'The phrase was: "{self.phrase}"',
                SCREEN_WIDTH // 2,
                SCREEN_HEIGHT // 2,
                arcade.color.BLACK,
                font_size=18,
                anchor_x="center",
                width=450,
                align="center"
            )
            arcade.draw_text(
                "Press SPACE for new game",
                SCREEN_WIDTH // 2,
                SCREEN_HEIGHT // 2 - 60,
                arcade.color.GRAY,
                font_size=16,
                anchor_x="center"
            )
    
    def on_key_press(self, key, modifiers):
        """Handle keyboard input"""
        if key == arcade.key.SPACE:
            self.setup()
            return
        
        if self.game_over or self.current_turn != "human":
            return
        
        # Handle letter input
        if arcade.key.A <= key <= arcade.key.Z:
            letter = chr(key)
            self.process_guess(letter)
    
    def update(self, delta_time):
        """Game logic updates"""
        # AI turn with delay
        if self.ai_should_move:
            self.ai_delay_timer -= delta_time
            if self.ai_delay_timer <= 0:
                self.ai_turn()
    
    def on_close(self):
        """Clean up database connection"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        super().on_close()


def main():
    game = HangmanGame()
    game.setup()
    arcade.run()


if __name__ == "__main__":
    main()
