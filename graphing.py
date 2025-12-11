import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Read the CSV file
df = pd.read_csv('test_results.csv')

ordered_reversed = df[df['Order Given'].isin(['Ordered', 'Reversed'])].copy()
separate_data = df[df['Order Given'] == 'Separate'].copy()

# Set the style
plt.style.use('seaborn-v0_8')
plt.figure(figsize=(10, 6))

# Create grouped bar chart
ax = sns.barplot(data=ordered_reversed, x='Order Given', y='Score', hue='Ignore Order', 
                estimator='mean', errorbar=None, palette='Set2')


# Calculate average for Separate
separate_avg = separate_data['Score'].mean()

# Add the Separate bar manually
x_pos = 2  # Position for third group
bar_width = 0.4
separate_bar = ax.bar(x_pos, separate_avg, bar_width, 
                     color='lightgray', label='Separate')

# Update x-axis
ax.set_xticks([0, 1, 2])
ax.set_xticklabels(['Ordered', 'Reversed', 'Separate'])

plt.title('Average Scores by Order Given and Ignore Order Setting', fontsize=14, fontweight='bold')
plt.ylabel('Average Score', fontsize=12)
plt.xlabel('Order Given', fontsize=12)
plt.ylim(0, 100)
plt.legend(title='Ignore Order', title_fontsize=12, fontsize=11)

# Add value labels on bars
for container in ax.containers:
    ax.bar_label(container, fmt='%.1f', fontweight='bold')

# Add label for separate bar
#ax.text(x_pos, separate_avg + 2, f'{separate_avg:.1f}', 
#        ha='center', va='bottom', fontweight='bold')

plt.tight_layout()
plt.show()