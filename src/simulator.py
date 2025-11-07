import time
from typing import Iterator


class SimpleSimulator:
    """A tiny lap-level simulator that yields lap rows one-by-one.

    The simulator expects a pandas DataFrame where each row represents a lap event
    for a single vehicle (for MVP we operate at lap granularity).
    """

    def __init__(self, laps_df, speed: float = 1.0):
        # laps_df is expected to be ordered by timestamp
        self.laps = laps_df.reset_index(drop=True)
        self.pos = 0
        self.speed = float(speed) if speed > 0 else 1.0

    def has_next(self) -> bool:
        return self.pos < len(self.laps)

    def next(self):
        if not self.has_next():
            raise StopIteration
        row = self.laps.iloc[self.pos]
        self.pos += 1
        return row

    def replay(self, delay_callback=None) -> Iterator[object]:
        """Yield rows with a small sleep between them scaled by speed.

        delay_callback(optional): function(seconds) -> None; called to sleep, can be time.sleep
        """
        delay = delay_callback or time.sleep
        while self.has_next():
            row = self.next()
            yield row
            # basic pacing: 1.0 / speed seconds between steps
            delay(max(0.01, 1.0 / self.speed))
