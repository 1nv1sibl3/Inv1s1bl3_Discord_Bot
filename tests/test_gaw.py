from src.bot.games.gaw import GuessAWordRound, GuessAWordManager


def test_gaw_round_mechanics():
    round_game = GuessAWordRound(word="python", category="Programming", channel_id=123)
    assert round_game.category == "Programming"
    assert len(round_game.revealed) == 6
    assert round_game.mask == "_ _ _ _ _ _"

    # Incorrect guess
    is_corr, is_close, _ = round_game.guess("z")
    assert is_corr is False
    assert is_close is False

    # Letter match
    is_corr, is_close, _ = round_game.guess("p")
    assert is_corr is False
    assert is_close is True
    assert round_game.revealed[0] == "p"

    # Exact full word match
    is_corr, is_close, msg = round_game.guess("python")
    assert is_corr is True
    assert "Correct!" in msg


def test_gaw_manager():
    mgr = GuessAWordManager()
    game = mgr.start_game(channel_id=999)
    assert game is not None
    assert mgr.get_game(999) is game

    ended = mgr.end_game(999)
    assert ended is game
    assert mgr.get_game(999) is None
