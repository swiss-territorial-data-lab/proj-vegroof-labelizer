import pandas as pd

# Example DataFrame
data = pd.DataFrame({
    "A": [10, 20, 30, 40, 50],
    "B": [15, 25, 35, 45, 55]
}, index=[1, 2, 3, 4, 5])

# List of indices to select
indices_to_select = [2, 4]
indices_to_select_2 = [4, 2]

# Filter DataFrame
subset = data[data.index.isin(indices_to_select)]
subset_2 = data[data.index.isin(indices_to_select_2)]

print("Original DataFrame:")
print(data.sort_index(ascending=False))

print("\nSubset DataFrame:")
print(subset)
print(subset_2)
