import json
from collections import Counter

with open('output/processing_errors.json') as f:
    errors = json.load(f)

# Count error types
error_msgs = [e['error'][:100] for e in errors]
counts = Counter(error_msgs)

print(f"Total errors: {len(errors)}")
print("\nTop 5 error types:")
for msg, count in counts.most_common(5):
    print(f"{count}: {msg}")

# Check a few specific errors
print("\n\nFirst 3 full errors:")
for i, e in enumerate(errors[:3]):
    print(f"\nError {i+1}:")
    print(f"  Transaction date: {e['transaction'].get('date')}")
    print(f"  Error: {e['error']}")