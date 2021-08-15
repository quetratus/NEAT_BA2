import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd


df = pd.read_csv('scores_per_generation.csv')
df = df.groupby(by='generation').max().reset_index(drop=True)
sns.set_theme(style='whitegrid')
# print(df)
fig = plt.figure(figsize=(10,10))
gen = [str(i+1) for i in range(df.shape[0])]
plt.plot(gen, df['score'], marker='o')

#plt.yscale('log')
plt.title("NEAT - Score each generation | Constant Game Speed")
plt.xlabel("Generations")
plt.ylabel("Score")
fig.savefig('neat_score_gamespeed.jpeg')
plt.show()
