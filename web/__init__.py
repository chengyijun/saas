from pathlib import Path

uploads = Path(__file__).parent.parent.joinpath("uploads")
if not uploads.exists():
    uploads.mkdir(mode=777, exist_ok=True)
