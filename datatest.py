import pandas as pd

df = pd.read_csv("trainer_dataset.csv")

print(df.columns.tolist())
print(df.head())
print(df["Strength"].value_counts())