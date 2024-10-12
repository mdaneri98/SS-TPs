import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

def get_k_folders(base_path='outputs/multiple'):
    return sorted([f for f in os.listdir(base_path) if f.startswith('k_')],
                  key=lambda x: float(x.split('_')[1]))

def get_verlet_folders(k_folder_path):
    return sorted([f for f in os.listdir(k_folder_path) if f.startswith('verlet_')],
                  key=lambda x: float(x.split('_')[1]))

def extract_value(folder_name, prefix):
    return float(folder_name.split(prefix)[1])

def analyze_data(base_path='outputs/multiple'):
    k_folders = get_k_folders(base_path)
    all_data = {}

    for k_folder in k_folders:
        k_value = extract_value(k_folder, 'k_')
        k_path = os.path.join(base_path, k_folder)
        verlet_folders = get_verlet_folders(k_path)

        w_values = []
        max_amplitudes = []

        for verlet_folder in verlet_folders:
            verlet_path = os.path.join(k_path, verlet_folder)
            static_df = pd.read_csv(os.path.join(verlet_path, 'static.csv'), header=None, skiprows=1)
            particle_df = pd.read_csv(os.path.join(verlet_path, 'particle.csv'))

            static_df.columns = ['n', 'k', 'mass', 'distance', 'amplitud', 'w0', 'wf']
            wf = float(static_df['wf'].values[0])
            max_amplitude = particle_df['position'].abs().max()

            w_values.append(wf)
            max_amplitudes.append(max_amplitude)

        all_data[k_value] = {'w': np.array(w_values), 'amp': np.array(max_amplitudes)}

    return all_data

def plot_results(all_data):
    num_k = len(all_data)
    fig, axs = plt.subplots(num_k, 1, figsize=(12, 6*num_k), sharex=True)
    if num_k == 1:
        axs = [axs]

    colors = plt.cm.viridis(np.linspace(0, 1, num_k))

    for i, (k, data) in enumerate(all_data.items()):
        sorted_indices = np.argsort(data['w'])
        w_sorted = data['w'][sorted_indices]
        amp_sorted = data['amp'][sorted_indices]

        axs[i].plot(w_sorted, amp_sorted, marker='o', linestyle='-', color=colors[i], label=f'k = {k:.2f}')
        axs[i].set_title(f'k = {k:.2f}')
        axs[i].set_ylabel('Amplitud máxima')
        axs[i].set_xlabel('Frecuencia angular externa (w)')
        axs[i].grid(True)
        axs[i].legend()

        # Añadir texto con el valor máximo de amplitud
        max_amp_index = np.argmax(amp_sorted)
        axs[i].annotate(f'Max: {amp_sorted[max_amp_index]:.2f} at w={w_sorted[max_amp_index]:.2f}',
                        xy=(w_sorted[max_amp_index], amp_sorted[max_amp_index]),
                        xytext=(5, 5), textcoords='offset points')

    plt.tight_layout()
    plt.savefig('outputs/multiple/amplitud_vs_w_all_k.jpg', format='jpg', dpi=300)
    plt.close()

if __name__ == "__main__":
    all_data = analyze_data()
    plot_results(all_data)
    print("Análisis completado. Gráfico guardado en outputs/multiple/amplitud_vs_w_all_k.jpg")