import pandas as pd


df = pd.read_csv("armanide.csv")


df['price'] = df['price'].astype(str)
df['size'] = df['size'].astype(str)
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

print(len(grouped_df))
grouped_df['image_urls'] = grouped_df['image_urls'].apply(lambda x: x.split('#')[0] if len(set(x.split('#'))) == 1 else x)

grouped_df['price'] = grouped_df['price'].apply(lambda x: x.split('#')[0] if len(set(x.split('#'))) == 1 else x)

grouped_df.to_csv('merged_data.csv', index=False)