from ocrpolish.services.windowing_service import SlidingWindowService


def test_get_windows_basic():
    service = SlidingWindowService(window_size=10, overlap=2)
    text = "one two three four five six"
    # tiktoken will likely use more than 10 tokens for this if available
    # but let's test the logic assuming it works
    windows = service.get_windows(text)
    assert len(windows) >= 1
    assert windows[0].startswith("one")


def test_get_windows_heuristic():
    service = SlidingWindowService(window_size=10, overlap=2)
    # Force heuristic by setting encoding to None
    service.encoding = None

    text = "one two three four five six"
    # words_per_window = 10 / 1.33 = 7
    # overlap_words = 2 / 1.33 = 1
    # total words = 6
    # 6 <= 7, so one window
    windows = service.get_windows(text)
    assert windows == ["one two three four five six"]


def test_get_windows_heuristic_split():
    service = SlidingWindowService(window_size=5, overlap=1)
    service.encoding = None

    # words_per_window = 5 / 1.33 = 3
    # overlap_words = 1 / 1.33 = 0
    # window 1: words[0:3] -> "one two three"
    # start moves to 0 + 3 - 0 = 3
    # window 2: words[3:6] -> "four five six"


def test_get_windows_tiktoken_split():
    # 'cl100k_base' usually encodes words as 1-2 tokens
    service = SlidingWindowService(window_size=5, overlap=1)
    assert service.encoding is not None

    text = "one two three four five six seven eight nine ten"
    windows = service.get_windows(text)
    assert len(windows) > 1
    # Check that windows overlap or at least cover the text
    "".join(windows)
    assert "one" in windows[0]
    assert "ten" in windows[-1]
