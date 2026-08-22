from __future__ import annotations


def lan_ip() -> str:
    """Best-effort detection of the machine's primary LAN IPv4 address."""
    import socket

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
    except OSError:
        return ""
