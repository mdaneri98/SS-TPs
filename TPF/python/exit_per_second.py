import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

def calculate_door_flow(ct_value, p_value, dt):
    # Modify the path structure to match your directory format
    input_path = Path('outputs/probabilistic_analysis') / f't_{ct_value}_&_p_{p_value:.2f}'
    output_path = Path('outputs/exits') / f't_{ct_value}_&_p_{p_value:.2f}'

    print(f"Checking paths...")
    print(f"Input exists: {input_path.exists()}")

    # Create output directory if it doesn't exist
    output_path.mkdir(parents=True, exist_ok=True)

    # Store data for all simulations
    all_flows = []
    all_times = []

    # Process each simulation in the directory
    for sim_dir in input_path.glob('sim_*'):
        dynamic_file = sim_dir / 'dynamic.txt'
        if not dynamic_file.exists():
            continue

        print(f"Processing {sim_dir.name}")

        # Read data
        dynamic_data = []
        with open(dynamic_file, 'r') as f:
            current_time = None
            particles = []
            for line in f:
                line = line.strip()
                if ',' not in line:
                    if particles:
                        dynamic_data.append({'time': current_time, 'particles': particles})
                    current_time = float(line)
                    particles = []
                else:
                    particle = list(map(float, line.split(',')))
                    particles.append(particle)
            if particles:
                dynamic_data.append({'time': current_time, 'particles': particles})

        # Sort by time to ensure order
        dynamic_data.sort(key=lambda x: x['time'])

        # Create time windows
        max_time = dynamic_data[-1]['time']
        time_windows = np.arange(0, max_time, dt)

        times = []
        flows = []

        # Calculate flow for each window
        for t in time_windows:
            # Find closest states before and after t
            states_before = [s for s in dynamic_data if s['time'] <= t]
            states_after = [s for s in dynamic_data if s['time'] > t and s['time'] <= t + dt]

            if not states_before or not states_after:
                continue

            state1 = states_before[-1]
            state2 = states_after[0]

            count1 = len(state1['particles'])
            count2 = len(state2['particles'])

            times.append(t)
            flows.append(count1 - count2)

        if flows:
            all_flows.append(flows)
            all_times.append(times)

    if all_flows:
        # Calculate average flow across all simulations
        max_len = min(len(flow) for flow in all_flows)
        times = all_times[0][:max_len]  # Use times from first simulation
        avg_flows = np.mean([flow[:max_len] for flow in all_flows], axis=0)
        std_flows = np.std([flow[:max_len] for flow in all_flows], axis=0)

        # Plot
        plt.figure(figsize=(12, 6))
        plt.plot(times, avg_flows, label='Average flow', color='blue')
        plt.fill_between(times,
                         avg_flows - std_flows,
                         avg_flows + std_flows,
                         alpha=0.2,
                         color='blue',
                         label='Standard deviation')

        plt.xlabel('Time (s)')
        plt.ylabel('Flow Rate (particles/interval)')
        plt.title(f'Average Particle Flow Rate\n(ct = {ct_value}, p = {p_value:.2f}, dt = {dt})')
        plt.legend()
        plt.grid(True)

        output_file = output_path / 'door_flow_rates.png'
        print(f"Saving plot to: {output_file}")
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()

        # Save data
        flow_df = pd.DataFrame({
            'Time': times,
            'Average_Flow': avg_flows,
            'Std_Flow': std_flows
        })
        csv_file = output_path / 'door_flow_rates.csv'
        print(f"Saving CSV to: {csv_file}")
        flow_df.to_csv(csv_file, index=False)

if __name__ == "__main__":
    dt = 1
    ct_value = 100
    p_value = 0.5
    calculate_door_flow(ct_value, p_value, dt)