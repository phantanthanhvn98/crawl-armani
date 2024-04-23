import pandas as pd
import re


df = pd.read_csv("draft_final_armaniturkiye.csv")

df['code'] = df['name'].apply(lambda x: x.split(" | ")[-1])

df = df.rename(columns={'code': 'sku'})
df['color'] = df['color'].apply(lambda x: '#'.join(list(set(x.split("#")))))

df.to_csv('final_armaniturkiye.csv', index=False)