import pandas as pd
import re


df = pd.read_csv("draft_armanide.csv")

df = df.drop_duplicates(subset='code')
df = df.rename(columns={'code': 'mpn'})
df['size'] = df['size'].astype(str)
df['color'] = df['color'].astype(str)
df['name'] = df['name'].astype(str)


def remove_text(x):
    x['name'] = split_by_capital(x['name'])
    x['size'] = x['size'].replace('FürdieausgewählteGrößeistdieFarbenichterhältlich', '')
    x['color'] = x['color'].replace('FürdieausgewählteGrößeistdieFarbenichterhältlich', '')
    x['sku'] = x['url'].split('.html')[0].split('cod')[-1]
    x['details'] = x['details'] + x['attributes'].replace("##", ": ").replace("||", " ")
    if len(x['breadcrumbs'].split(">")) < 2:
        print(x)
        return
    x['category'] = x['breadcrumbs'].split(">")[-2]
    x['breadcrumbs'] = '>'.join(x['breadcrumbs'].split('>')[:-2])
    return x

def split_by_capital(text):
    substrings = re.findall('[A-Z][^A-Z]*', text)
    return ' '.join(substrings)  

df = df.apply(lambda x: remove_text(x), axis=1)

orders = ["mpn", "sku", "name", "price", "description", "url", "image_urls", "category", "brand", "color", "size", "details", "breadcrumbs", "attributes"]

df = df[orders]
df['attributes'] = ''

df.to_csv('final_armanide.csv', index=False)