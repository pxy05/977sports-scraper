import sys

def print_progress_bar(percent: int, decimal: bool = False):
    if decimal:
        sys.stdout.write(f"[{">"*int(percent * 30)}{"-"*(30-int(percent * 30))}] {percent * 100:.2f}%\r")
    else:
        sys.stdout.write(f"[{">"*int(percent * 30)}{"-"*(30-int(percent * 30))}] {int(percent * 100)}%\r")
    sys.stdout.flush()
