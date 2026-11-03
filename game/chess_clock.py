"""Chess clock Human: waktunya hanya berkurang saat giliran Human."""

from config import CLOCK_URGENT_SECONDS


class ChessClock:
    """Jam catur untuk Human: berkurang hanya saat giliran Human."""

    def __init__(self, seconds):
        """Jam penuh (seconds detik) dan belum berjalan."""
        self.total = seconds
        self.remaining = seconds
        self.running = False

    def start(self):
        """Jalankan jam (awal giliran Human)."""
        self.running = True

    def stop(self):
        """Hentikan jam (giliran AI atau game selesai)."""
        self.running = False

    def tick(self, dt):
        """Dipanggil setiap frame. dt = detik sejak frame sebelumnya."""
        if self.running:
            self.remaining = max(0.0, self.remaining - dt)

    def expired(self):
        """True jika waktu Human habis."""
        return self.remaining <= 0.0

    def urgent(self):
        """True jika waktu hampir habis (jam berkedip merah)."""
        return self.remaining <= CLOCK_URGENT_SECONDS

    def fraction(self):
        """Sisa waktu dalam persen (0.0 - 1.0), untuk bar di layar."""
        return self.remaining / self.total
