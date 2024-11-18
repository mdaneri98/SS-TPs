import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import pandas as pd
import os

base_output_dir = "outputs/analysis/dcm_plots"

def ensure_directory_exists(directory):
    """Create directory if it doesn't exist"""
    os.makedirs(directory, exist_ok=True)

def process_simulation(n, v, i, path):
    input_filename = f"{path}/v_{v}/{i}/particles.csv"
    df = pd.read_csv(input_filename)
    df = df[df['id'] == 0]
    collision_data = {row['time']: row for _, row in df.iterrows()}
    return collision_data

def plot_dcm_over_time(iterations, big_particle_data):
    ensure_directory_exists(base_output_dir)

    delta_t = 0.02
    initial_x = initial_y = 0.05000
    msd_values_all_runs = []

    for i in range(iterations):
        iteration_data = big_particle_data[i]
        times = sorted(iteration_data.keys())
        filtered_times = []
        current_time = times[0]
        while current_time <= times[-1]:
            closest_time = min(times, key=lambda x: abs(x - current_time))
            filtered_times.append(closest_time)
            current_time += delta_t

        msd_values = []
        for t in filtered_times:
            collision = iteration_data[t]
            x = collision['x']
            y = collision['y']
            msd = (x - initial_x)**2 + (y - initial_y)**2
            msd_values.append(msd)

        msd_values_all_runs.append(msd_values)

        lengths = [len(sublist) for sublist in msd_values_all_runs]
        if len(set(lengths)) != 1:
            min_length = min(lengths)
            msd_values_all_runs = [sublist[:min_length] for sublist in msd_values_all_runs]
            filtered_times = filtered_times[:min_length]

    msd_array = np.array(msd_values_all_runs)
    msd_mean = np.mean(msd_array, axis=0)
    msd_std = np.std(msd_array, axis=0)

    plt.figure(figsize=(10, 6))
    plt.errorbar(filtered_times, msd_mean, fmt='o-', capsize=3, label='DCM')
    plt.xlabel('Tiempo (s)')
    plt.ylabel('DCM ($m^{2}$)')
    ax = plt.gca()
    ax.yaxis.set_major_formatter(ticker.ScalarFormatter(useMathText=True))
    ax.yaxis.get_offset_text().set_fontsize(12)
    ax.ticklabel_format(style='sci', axis='y', scilimits=(-2, 2))
    plt.grid(True)
    plt.legend()
    plt.savefig(f'{base_output_dir}/dcm_over_time.png')
    plt.close()

    return msd_mean[:15], msd_std[:15], filtered_times[:15]

def plot_min_error_for_msd(times, msd_mean):
    errors = []
    c_values = np.arange(0.000, 0.006, 0.0000001)

    for c in c_values:
        fc = np.array([c*t for t in times])
        error = np.sum((msd_mean - fc) ** 2)
        errors.append(error)

    min_error = min(errors)
    min_c = c_values[np.argmin(errors)]

    print(f"El valor óptimo de c es c={min_c} con un error de ajuste E={min_error}")

    plt.figure(figsize=(10, 6))
    plt.plot(c_values, errors, color='r')
    plt.scatter(min_c, min_error, color='b', zorder=5, label=f'Error mínimo en c={min_c:.5f}')
    plt.xlabel('c', fontsize=14)
    plt.ylabel('E(c)', fontsize=14)
    plt.grid(True, linestyle='--', linewidth=0.5)
    plt.legend()
    plt.savefig(f'{base_output_dir}/min_error.png')
    plt.close()

    return min_c

def plot_msd_with_linear_fit(times, msd_mean, msd_std, min_c):
    continuous_times = np.linspace(0.0, max(times), 15)
    model_msd = min_c * continuous_times

    plt.figure(figsize=(10, 6))
    plt.plot(times, model_msd, '--', color='red', label=f'Ajuste lineal (D={round(min_c*1e3, 3)}x$10^{{-3}}$)')
    plt.errorbar(times, msd_mean, yerr=msd_std, fmt='o-', capsize=3, label='DCM')
    plt.xlabel('Tiempo (s)')
    plt.ylabel('DCM ($m^{2}$)')
    ax = plt.gca()
    ax.yaxis.set_major_formatter(ticker.ScalarFormatter(useMathText=True))
    ax.yaxis.get_offset_text().set_fontsize(12)
    ax.ticklabel_format(style='sci', axis='y', scilimits=(-2, 2))
    plt.grid(True)
    plt.legend()
    plt.savefig(f'{base_output_dir}/msd_with_linear_fit.png')
    plt.close()

def main():
    N = 200
    V = "1.00"
    ITERATIONS = 10
    base_path = "outputs/common_solution"

    big_particle_data = []

    for i in range(0, ITERATIONS):
        sim_dict = process_simulation(N, V, i, base_path)
        big_particle_data.append(sim_dict)

    msd_mean, msd_std, times = plot_dcm_over_time(ITERATIONS, big_particle_data)
    min_c = plot_min_error_for_msd(times, msd_mean)
    plot_msd_with_linear_fit(times, msd_mean, msd_std, min_c)

if __name__ == "__main__":
    main()