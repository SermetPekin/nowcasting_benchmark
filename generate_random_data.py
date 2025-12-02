import pandas as pd
import numpy as np

# Load original data
input_path = 'data/data_tf.csv'
output_path = 'data/data_randomized.csv'

print(f"Loading {input_path}...")
df = pd.read_csv(input_path)

# Shuffle the target variable 'gdpc1'
# We only shuffle non-NaN values to keep the structure valid
target_col = 'gdpc1'
mask = ~df[target_col].isna()
values = df.loc[mask, target_col].values

print(f"Shuffling {len(values)} observations of {target_col}...")
np.random.shuffle(values)
df.loc[mask, target_col] = values

# Save to new file
df.to_csv(output_path, index=False)
print(f"✓ Created {output_path} with randomized target variable.")
print("You can now update the configuration in the notebook to use this file.")
