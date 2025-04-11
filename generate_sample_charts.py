# generate_sample_charts.py
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import numpy as np
import os

# --- Setup ---
output_dir = os.path.join('static', 'images')
os.makedirs(output_dir, exist_ok=True)

# --- Styling Configuration ---
# Try to mimic the target style more closely
plt.style.use('seaborn-v0_8-whitegrid') # Start with a clean base
plt.rcParams['figure.dpi'] = 180 # Higher DPI
plt.rcParams['font.family'] = 'sans-serif'
# Common sans-serif fonts, adjust if you have specific ones installed
plt.rcParams['font.sans-serif'] = ['Arial', 'DejaVu Sans', 'Verdana', 'Tahoma']
plt.rcParams['font.size'] = 7 # Smaller base font size
plt.rcParams['axes.titlesize'] = 9 # Title font size
plt.rcParams['axes.labelsize'] = 7 # Axis label font size
plt.rcParams['xtick.labelsize'] = 6 # X tick label font size
plt.rcParams['ytick.labelsize'] = 6 # Y tick label font size
plt.rcParams['axes.edgecolor'] = 'lightgrey' # Lighter axis border color
plt.rcParams['axes.linewidth'] = 0.8 # Thinner axis line
plt.rcParams['grid.color'] = '#EAEAEA' # Lighter grid color
plt.rcParams['grid.linestyle'] = '-'
plt.rcParams['grid.linewidth'] = 0.5
plt.rcParams['figure.facecolor'] = 'white' # Ensure figure bg is white
plt.rcParams['axes.facecolor'] = 'white' # Ensure axes bg is white


print(f"Generating improved sample charts in '{output_dir}'...")

# --- Common Save Function ---
def save_chart(filename, fig):
    filepath = os.path.join(output_dir, filename)
    try:
        # Adjust layout tightly
        fig.tight_layout(pad=0.1)
        # Save with transparent background to better fit containers
        fig.savefig(filepath, dpi=plt.rcParams['figure.dpi'], bbox_inches='tight', transparent=True, pad_inches=0.05)
        plt.close(fig)
        print(f"Generated: {filepath}")
    except Exception as e:
        print(f"Error generating {filepath}: {e}")
        plt.close(fig)


# --- Chart Generation Functions with More Styling ---

def style_axis(ax):
    """Apply common styling to axes: remove top/right spines, customize grid."""
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color(plt.rcParams['axes.edgecolor'])
    ax.spines['bottom'].set_color(plt.rcParams['axes.edgecolor'])
    ax.xaxis.grid(False) # No vertical grid lines
    ax.yaxis.grid(True) # Horizontal grid lines based on rcParams
    ax.tick_params(axis='x', length=0) # No x-axis ticks
    ax.tick_params(axis='y', length=3, color='lightgrey') # Small y-axis ticks

# --- 1. Bar Chart: Customer Breakdown (Simulated Time Series) ---
fig1, ax1 = plt.subplots(figsize=(4, 2.5)) # Adjust size
N = 30 # Simulate 30 data points (e.g., days)
x = np.arange(N)
y = 15000 + np.random.randint(-3000, 3000, size=N).cumsum() # Simulate some variation
y = np.maximum(y, 5000) # Ensure positive values
colors = ['skyblue' if i % 2 == 0 else 'lightsteelblue' for i in range(N)] # Alternating colors
ax1.bar(x, y, color=colors, width=0.7)
ax1.set_title('Customer Breakdown (Sample Trend)', fontsize=plt.rcParams['axes.titlesize'])
ax1.set_ylabel('Count', fontsize=plt.rcParams['axes.labelsize'])
ax1.set_xticks([]) # Hide x-axis labels for dense bars
style_axis(ax1)
# Format y-axis nicely
ax1.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, p: format(int(x), ',')))
save_chart('sample_bar_chart_1.png', fig1)

# --- 2. Bar Chart: Sales by Category (Simulated Time Series) ---
fig2, ax2 = plt.subplots(figsize=(4, 2.5))
N = 30
x = np.arange(N)
y = 60000 + np.random.randint(-10000, 10000, size=N).cumsum()
y = np.maximum(y, 10000)
colors = ['lightgreen' if i % 2 == 0 else 'darkseagreen' for i in range(N)]
ax2.bar(x, y, color=colors, width=0.7)
ax2.set_title('Sales Trend (Sample)', fontsize=plt.rcParams['axes.titlesize'])
ax2.set_ylabel('Sales ($)', fontsize=plt.rcParams['axes.labelsize'])
ax2.set_xticks([])
style_axis(ax2)
ax2.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, p: f'{int(x/1000)}k')) # Format as thousands
save_chart('sample_bar_chart_2.png', fig2)

# --- 3. Heatmap: Customer Retention ---
fig3, ax3 = plt.subplots(figsize=(4.5, 3)) # Slightly adjusted size
data = np.array([
    [1.00, 0.38, 0.28, 0.20, 0.15, 0.11, 0.09], # More columns
    [np.nan, 1.00, 0.42, 0.33, 0.25, 0.18, 0.13],
    [np.nan, np.nan, 1.00, 0.48, 0.38, 0.29, 0.21],
    [np.nan, np.nan, np.nan, 1.00, 0.52, 0.41, 0.33],
    [np.nan, np.nan, np.nan, np.nan, 1.00, 0.55, 0.45]
    ])
sns.heatmap(data, annot=True, fmt=".0%", cmap="GnBu", linewidths=.5, linecolor='lightgrey', cbar=False, annot_kws={"size": 6}, ax=ax3) # Different cmap, smaller text
ax3.set_title('Sample Customer Retention (%)', fontsize=plt.rcParams['axes.titlesize'])
ax3.set_xlabel('Weeks Since First Order', fontsize=plt.rcParams['axes.labelsize'])
ax3.set_ylabel('Cohort Week', fontsize=plt.rcParams['axes.labelsize'])
# Adjust ticks based on new data shape
ax3.set_xticks(np.arange(data.shape[1]) + 0.5)
ax3.set_yticks(np.arange(data.shape[0]) + 0.5)
ax3.set_xticklabels([f'Wk {i}' for i in range(data.shape[1])], rotation=0, ha='center')
ax3.set_yticklabels([f'Wk {i}' for i in range(data.shape[0])], rotation=0)
ax3.tick_params(axis='both', length=0) # Hide ticks
save_chart('sample_heatmap.png', fig3)

# --- 4. Bar Chart: Purchase Frequency ---
# Keeping this simpler as target image also looks simple
fig4, ax4 = plt.subplots(figsize=(4, 2.5))
labels = ['1', '2', '3', '4+'] # Fewer categories might look cleaner
values = [17500, 4200, 1826, 500] # Adjusted distribution
colors = ['mediumpurple', 'plum', 'thistle', 'lavender']
bars = ax4.bar(labels, values, color=colors, width=0.6)
ax4.set_title('Purchase Frequency Distribution', fontsize=plt.rcParams['axes.titlesize'])
ax4.set_ylabel('# Customers', fontsize=plt.rcParams['axes.labelsize'])
ax4.set_xlabel('Number of Orders', fontsize=plt.rcParams['axes.labelsize'])
ax4.tick_params(axis='both', which='major', labelsize=plt.rcParams['xtick.labelsize'])
style_axis(ax4)
ax4.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, p: format(int(x), ',')))
save_chart('sample_bar_chart_3.png', fig4)


# generate_sample_charts.py

# ... (保持顶部的 imports 和 styling 不变) ...
# ... (保持 Bar Charts 和 Heatmap 的代码不变) ...

# --- 5. Donut Chart: Age (With Legend) ---
fig5, ax5 = plt.subplots(figsize=(3, 2.5)) # Adjust figsize slightly if needed for legend
labels = ['18-24', '25-34', '35-44', '45-54', '55+']
sizes = [20, 38, 27, 10, 5]
colors = sns.color_palette('colorblind', n_colors=len(labels))

# Draw pie chart wedges WITHOUT labels directly on them
wedges, texts = ax5.pie(sizes, colors=colors, startangle=90,
                        wedgeprops=dict(width=0.4, edgecolor='w')) # No labels or autopct here

# Draw circle in the center
centre_circle = plt.Circle((0,0),0.65,fc='white') # Slightly smaller hole?
ax5.add_artist(centre_circle)

# Set title and ensure aspect ratio
ax5.set_title('Age Distribution', fontsize=plt.rcParams['axes.titlesize'], pad=8)
ax5.axis('equal')

# --- ADD LEGEND ---
# Create legend outside the pie chart
# bbox_to_anchor controls position: (x, y, width, height) relative to axes
# loc specifies which part of the legend box anchors to bbox_to_anchor
ax5.legend(wedges, labels,
           title="Age Group",
           loc="center left",
           bbox_to_anchor=(0.95, 0, 0.5, 1), # Position right of the chart
           fontsize=6, # Smaller font for legend
           frameon=False # No border around legend
          )
# --- End Legend ---

save_chart('sample_donut_age.png', fig5)


# --- 6. Donut Chart: Gender (With Legend) ---
fig6, ax6 = plt.subplots(figsize=(3, 2.5)) # Adjust figsize
labels = ['Female', 'Male', 'Other']
sizes = [49, 46, 5]
colors = ['#ff8787', '#4dabf7', '#dee2e6'] # Use specific colors if desired

# Draw pie chart wedges WITHOUT labels
wedges, texts = ax6.pie(sizes, colors=colors, startangle=90,
                         wedgeprops=dict(width=0.4, edgecolor='w'))

# Draw circle
centre_circle = plt.Circle((0,0),0.65,fc='white')
ax6.add_artist(centre_circle)

# Set title and aspect ratio
ax6.set_title('Gender Distribution', fontsize=plt.rcParams['axes.titlesize'], pad=8)
ax6.axis('equal')

# --- ADD LEGEND ---
ax6.legend(wedges, labels,
           title="Gender",
           loc="center left",
           bbox_to_anchor=(0.95, 0, 0.5, 1), # Position right of the chart
           fontsize=6,
           frameon=False
          )
# --- End Legend ---

save_chart('sample_donut_gender.png', fig6)


print("--- Improved sample chart generation complete ---")