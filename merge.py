import pandas as pd
import re


df1 = pd.read_csv("final_armanide.csv")
df2 = pd.read_csv("draft_armanide2.csv")

df = pd.concat([df1, df1])

df.to_csv('final_armanide_.csv', index=False)