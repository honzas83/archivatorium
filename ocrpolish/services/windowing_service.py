from typing import Any

import tiktoken


class SlidingWindowService:
    """
    Service for splitting large documents into overlapping windows
    to stay within LLM context limits while maintaining context continuity.
    """

    def __init__(
        self, window_size: int = 28000, overlap: int = 2000, encoding_name: str = "cl100k_base"
    ):
        self.window_size = window_size
        self.overlap = overlap
        self.encoding: Any = None
        try:
            self.encoding = tiktoken.get_encoding(encoding_name)
        except Exception:
            # Fallback if tiktoken encoding is not available
            self.encoding = None

    def get_windows(self, text: str) -> list[str]:
        """
        Splits text into overlapping windows.
        """
        if not self.encoding:
            return self._get_windows_heuristic(text)

        tokens = self.encoding.encode(text)
        total_tokens = len(tokens)

        if total_tokens <= self.window_size:
            return [text]

        windows = []
        start = 0
        while start < total_tokens:
            end = min(start + self.window_size, total_tokens)
            window_tokens = tokens[start:end]
            windows.append(self.encoding.decode(window_tokens))

            if end == total_tokens:
                break

            # Move forward by window_size - overlap
            start += self.window_size - self.overlap

        return windows

    def _get_windows_heuristic(self, text: str) -> list[str]:
        """
        Fallback windowing using word count if tiktoken is unavailable.
        """
        words = text.split()
        total_words = len(words)

        # Heuristic: 1.33 tokens per word
        words_per_window = int(self.window_size / 1.33)
        overlap_words = int(self.overlap / 1.33)

        if total_words <= words_per_window:
            return [text]

        windows = []
        start = 0
        while start < total_words:
            end = min(start + words_per_window, total_words)
            chunk = " ".join(words[start:end])
            windows.append(chunk)

            if end == total_words:
                break

            start += words_per_window - overlap_words

        return windows
