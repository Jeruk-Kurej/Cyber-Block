"""Chess clock Human: waktunya hanya berkurang saat giliran Human."""

from config import CLOCK_URGENT_SECONDS


class ChessClock:
    def __init__(self, seconds):
        self.total = seconds
        self.remaining = seconds
        self.running = False

    def start(self):
        self.running = True

    def stop(self):
        self.running = False

    def tick(self, dt):
        """Dipanggil setiap frame. dt = detik sejak frame sebelumnya."""
        if self.running:
            self.remaining = max(0.0, self.remaining - dt)

    def expired(self):
        return self.remaining <= 0.0

    def urgent(self):
        return self.remaining <= CLOCK_URGENT_SECONDS

    def fraction(self):
        """Sisa waktu dalam persen (0.0 - 1.0), untuk bar di layar."""
        return self.remaining / self.total
