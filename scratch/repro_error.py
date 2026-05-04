import pandas as pd
import numpy as np

# Create a sample dataframe similar to what calculate_event_distribution returns
df = pd.DataFrame({
    'timestamp': pd.to_datetime(['2023-01-01 10:00:00', '2023-01-01 11:00:00']),
    'BT': [98.6, 100.4]
})

print("Original DF:")
print(df)

try:
    # This should fail if pandas is new enough
    result = df.sub(32)
    print("\nResult of df.sub(32):")
    print(result)
except TypeError as e:
    print(f"\nCaught expected error: {e}")

# Correct way:
df['BT'] = (df['BT'] - 32) * 5 / 9
print("\nCorrected DF:")
print(df)
