import pandas as pd

df = pd.read_excel("../data/key.xlsx")
# Prepare data
df_agg = df.loc[:, ['body_key','bundle_id_len']].groupby(['body_key']).agg({'count':'sum'})
df_agg.to_excel("../data/key_group.xlsx")


