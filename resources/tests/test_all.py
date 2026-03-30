from pathlib import Path

for f in sorted(Path(__file__).parent.glob("*.ttl")):
    if "invalid" in str(f):
        print(f"invalid: {f}")
    else:
        print(f"valid: {f}")
