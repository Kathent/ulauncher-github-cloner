import subprocess


def clipboard_items(max_size=10):
    proc = subprocess.run(["xsel", "-ob"], text=True, capture_output=True)

    if proc.returncode == 0:
        return [proc.stdout]
    return []


if __name__ == '__main__':
    clipboard_items(20)