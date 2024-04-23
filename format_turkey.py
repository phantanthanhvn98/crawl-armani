import pandas as pd
import re


df = pd.read_csv("draft_final_armaniturkiye.csv")
print(df['description'])
df['size'] = df['size'].astype(str)
df['color'] = df['color'].astype(str)
df['name'] = df['name'].astype(str)
df = df.rename(columns={'code': 'sku'})


def remove_text(x):
    x['pmn'] = x['url'].split('.html')[0].split('p-')[-1]
    return x

def split_by_capital(text):
    substrings = re.findall('[A-Z][^A-Z]*', text)
    return ' '.join(substrings)  

df = df.apply(lambda x: remove_text(x), axis=1)

orders = ["mnp", "name", "price", "description", "url", "image_urls", "category", "brand", "color", "size", "details", "breadcrumbs", "sku"]
df['code'] = df['name'].apply(lambda x: x.split(" | ")[-1])

df = df.rename(columns={'code': 'sku'})
df['color'] = df['color'].apply(lambda x: '#'.join(list(set(x.split("#")))))

df.to_csv('final_armaniturkiye.csv', index=False)