import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

def analyze_flow_metrics(base_dir='outputs/exits'):
    """
    Analyze flow metrics for all ct and p combinations and create heatmaps.
    Returns a dictionary of DataFrames for different metrics.
    """
    base_path = Path(base_dir)

    # Initialize data storage
    data = {
        'ct': [],
        'p': [],
        'peak_flow': [],
        'avg_flow': [],
        'time_to_peak': [],
        'total_time': [],
        'early_flow': []  # Flow acumulado en primeros 60 segundos
    }

    # Process each ct & p combination
    for combo_dir in base_path.glob('t_*_&_p_*'):
        try:
            # Extract ct and p from directory name
            dir_parts = combo_dir.name.split('_')
            ct = int(dir_parts[1])
            p = float(dir_parts[3])

            # Find CSV file
            csv_files = list(combo_dir.glob('door_flow_rates*.csv'))
            if not csv_files:
                continue

            # Read flow data
            df = pd.read_csv(csv_files[0])

            # Calculate metrics
            peak_flow = df['Average_Flow'].max()
            avg_flow = df['Average_Flow'].mean()
            time_to_peak = df.loc[df['Average_Flow'].idxmax(), 'Time']
            total_time = df['Time'].max()

            # Calculate early flow (first 60 seconds or less if simulation is shorter)
            early_mask = df['Time'] <= 60
            early_flow = df.loc[early_mask, 'Average_Flow'].sum()

            # Store data
            data['ct'].append(ct)
            data['p'].append(p)
            data['peak_flow'].append(peak_flow)
            data['avg_flow'].append(avg_flow)
            data['time_to_peak'].append(time_to_peak)
            data['total_time'].append(total_time)
            data['early_flow'].append(early_flow)

        except Exception as e:
            print(f"Error processing {combo_dir.name}: {str(e)}")

    # Convert to DataFrame
    metrics_df = pd.DataFrame(data)

    # Create heatmaps for each metric
    metrics = {
        'peak_flow': 'Peak Flow Rate',
        'avg_flow': 'Average Flow Rate',
        'time_to_peak': 'Time to Peak Flow (s)',
        'total_time': 'Total Evacuation Time (s)',
        'early_flow': 'Cumulative Flow (60s)'
    }

    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    axes = axes.flatten()

    for idx, (metric, title) in enumerate(metrics.items()):
        if idx >= len(axes):
            break

        # Reshape data for heatmap
        pivot_data = metrics_df.pivot(index='ct', columns='p', values=metric)

        # Create heatmap
        sns.heatmap(pivot_data,
                    ax=axes[idx],
                    cmap='viridis',
                    annot=True,
                    fmt='.1f',
                    cbar_kws={'label': metric})

        axes[idx].set_title(title)
        axes[idx].set_xlabel('Probability (p)')
        axes[idx].set_ylabel('Contact Time (ct)')

    # Remove extra subplot if any
    if len(metrics) < len(axes):
        fig.delaxes(axes[-1])

    plt.tight_layout()

    # Save plot
    output_file = base_path / 'flow_metrics_heatmap.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()

    return metrics_df

if __name__ == "__main__":
    metrics_df = analyze_flow_metrics()
    # Save metrics to CSV
    metrics_df.to_csv('outputs/exits/flow_metrics_summary.csv', index=False)