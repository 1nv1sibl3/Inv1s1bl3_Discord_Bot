import random
from typing import Dict, List, Optional, Tuple


DEFAULT_WORDS: List[Dict[str, str]] = [
    {"word": "python", "category": "Programming"},
    {"word": "discord", "category": "Technology"},
    {"word": "database", "category": "Technology"},
    {"word": "algorithm", "category": "Computer Science"},
    {"word": "variable", "category": "Programming"},
    {"word": "function", "category": "Programming"},
    {"word": "asynchronous", "category": "Development"},
    {"word": "elephant", "category": "Animals"},
    {"word": "giraffe", "category": "Animals"},
    {"word": "kangaroo", "category": "Animals"},
    {"word": "cheetah", "category": "Animals"},
    {"word": "tokyo", "category": "Geography"},
    {"word": "london", "category": "Geography"},
    {"word": "paris", "category": "Geography"},
    {"word": "jupiter", "category": "Space"},
    {"word": "neptune", "category": "Space"},
    {"word": "telescope", "category": "Science"},
    {"word": "microscope", "category": "Science"},
    {"word": "avocado", "category": "Food"},
    {"word": "lasagna", "category": "Food"},
]


class GuessAWordRound:
    def __init__(self, word: str, category: str, channel_id: int):
        self.word = word.lower().strip()
        self.category = category
        self.channel_id = channel_id
        self.revealed = ["_" for _ in self.word]
        self.attempts = 0
        self.max_attempts = 10

    def guess(self, guess: str) -> Tuple[bool, bool, str]:
        """
        Evaluate a guess.
        Returns: (is_correct, is_close, hint_string)
        """
        guess = guess.lower().strip()
        self.attempts += 1

        # Direct exact match
        if guess == self.word:
            self.revealed = list(self.word)
            return True, True, f"Correct! The word was **{self.word}**!"

        # Letter or substring match
        is_close = False
        if len(guess) == 1 and guess in self.word:
            is_close = True
            for i, ch in enumerate(self.word):
                if ch == guess:
                    self.revealed[i] = guess
            if "".join(self.revealed) == self.word:
                return True, True, f"Completed! The word was **{self.word}**!"
            return False, True, f"Good guess! Progress: `{' '.join(self.revealed)}`"

        if guess in self.word and len(guess) > 1:
            return False, True, f"'{guess}' is inside the secret word! Progress: `{' '.join(self.revealed)}`"

        return False, False, f"Incorrect. Progress: `{' '.join(self.revealed)}`"

    @property
    def mask(self) -> str:
        return " ".join(self.revealed)


class GuessAWordManager:
    """Manages active Guess A Word sessions keyed by channel ID."""

    def __init__(self):
        self._active_games: Dict[int, GuessAWordRound] = {}

    def start_game(self, channel_id: int) -> GuessAWordRound:
        item = random.choice(DEFAULT_WORDS)
        game = GuessAWordRound(word=item["word"], category=item["category"], channel_id=channel_id)
        self._active_games[channel_id] = game
        return game

    def get_game(self, channel_id: int) -> Optional[GuessAWordRound]:
        return self._active_games.get(channel_id)

    def end_game(self, channel_id: int) -> Optional[GuessAWordRound]:
        return self._active_games.pop(channel_id, None)


# Global game manager
gaw_manager = GuessAWordManager()
