import pandas as pd
import re


df = pd.read_csv("armanide.csv")

def extract_number_from_string(s):
    match = re.search(r'[-+]?\d*\.\d+|\d+', s)
    if match:
        return match.group()
    elif len(s) > 10:
        return ''
    else:
        return s
    
df = df[df['url'] != 'url']

df['price'] = df['price'].astype(str)

df['size'] = df['size'].astype(str).apply(lambda x: extract_number_from_string(x))
df['color'] = df['color'].astype(str)
df['image_urls'] = df['image_urls'].apply(lambda x: ','.join([item for item in x.split(',') if not item.endswith('.html')]))

df['category'] = df['breadcrumbs'].apply(lambda x: x.split(">")[-1])

grouped_df = df.groupby('url').agg(
    {
        'price': '#'.join, 
        'image_urls': '#'.join, 
        'color': '#'.join,
        'size': '#'.join,
        "code": "first",
        "name": "first",
        "description": "first",
        "category": "first",
        "brand": "first",
        "details": "first",
        "breadcrumbs": "first",
        "attributes": "first"
    }
).reset_index()

grouped_df['image_urls'] = grouped_df['image_urls'].apply(lambda x: x.split('#')[0] if len(set(x.split('#'))) == 1 else x)

grouped_df['price'] = grouped_df['price'].apply(lambda x: x.split('#')[0] if len(set(x.split('#'))) == 1 else x)

grouped_df['size'] = grouped_df['size'].apply(lambda x: '#'.join(set(x.split("#"))))
grouped_df['color'] = grouped_df['color'].apply(lambda x: "#".join(set(x.replace('FürdieausgewählteGrößeistdieFarbenichterhältlich', '').split("#"))))
grouped_df['breadcrumbs'] = grouped_df['breadcrumbs'].apply(lambda x: ">".join(x.split(">")[:-2]))
grouped_df['category '] = grouped_df['breadcrumbs'].apply(lambda x: x.split(">")[-1])
grouped_df['size'] = grouped_df['size'].apply(lambda x: '#'.join(set([ extract_number_from_string(value) for value in x.split("#")])))
# grouped_df['size'].apply(lambda x: print(x))
# grouped_df.to_csv('merged_data.csv', index=False)