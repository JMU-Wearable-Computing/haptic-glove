"""
Compute DTW distances for Sammy LatPulls trials (including variable trial)
and produce similarity scores using the same pipeline as dtw_macarena.py
"""
import os
import numpy as np
import math
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from scipy import stats


def load_elbow_angles(filename):
    base_dir = os.path.dirname(__file__)
    filepath = os.path.join(base_dir, "Sammy_MOCAP_Manipulated", filename)
    try:
        raw_data = np.genfromtxt(filepath, skip_header=7, delimiter=',', filling_values=0.0)
    except OSError:
        raise FileNotFoundError(f"Data file not found: {filepath}")

    if raw_data is None or raw_data.size == 0:
        return np.array([])
    if raw_data.ndim == 1:
        if raw_data.size < 10:
            return np.array([])
        raw_data = raw_data.reshape(1, -1)
    if raw_data.ndim == 2 and raw_data.shape[1] < 10:
        cols = raw_data.shape[1]
        new = np.zeros((raw_data.shape[0], 10))
        new[:, :cols] = raw_data
        raw_data = new

    time = raw_data[:, 0]
    shoulder_x = raw_data[:, 1]
    shoulder_y = raw_data[:, 2]
    shoulder_z = raw_data[:, 3]
    elbow_x = raw_data[:, 4]
    elbow_y = raw_data[:, 5]
    elbow_z = raw_data[:, 6]
    hand_x = raw_data[:, 7]
    hand_y = raw_data[:, 8]
    hand_z = raw_data[:, 9]

    angles = []
    for i in range(len(time)):
        ehx = elbow_x[i] - hand_x[i]
        ehy = elbow_y[i] - hand_y[i]
        ehz = elbow_z[i] - hand_z[i]
        esx = elbow_x[i] - shoulder_x[i]
        esy = elbow_y[i] - shoulder_y[i]
        esz = elbow_z[i] - shoulder_z[i]
        mag_eh = math.sqrt(ehx**2 + ehy**2 + ehz**2)
        mag_es = math.sqrt(esx**2 + esy**2 + esz**2)
        if mag_eh == 0 or mag_es == 0:
            angles.append(0.0)
        else:
            dot = ehx*esx + ehy*esy + ehz*esz
            cos_t = dot / (mag_eh * mag_es)
            cos_t = max(-1.0, min(1.0, cos_t))
            angles.append(math.degrees(math.acos(cos_t)))
    return np.array(angles)


def z_normalize(s):
    s = np.array(s, dtype=float)
    if s.size == 0:
        return s
    mu = np.mean(s)
    sigma = np.std(s)
    if sigma == 0:
        return s - mu
    return (s - mu) / sigma


def dtw_distance(s1, s2, window=None, return_path_len=False):
    n, m = len(s1), len(s2)
    if n == 0 or m == 0:
        return (float('inf'), 0) if return_path_len else float('inf')
    if window is None:
        window = max(n, m)
    window = max(window, abs(n - m))

    dtw = np.full((n+1, m+1), np.inf)
    dtw[0, 0] = 0.0

    for i in range(1, n+1):
        start_j = max(1, i - window)
        end_j = min(m, i + window)
        for j in range(start_j, end_j+1):
            cost = abs(s1[i-1] - s2[j-1])
            dtw[i, j] = cost + min(dtw[i-1, j], dtw[i, j-1], dtw[i-1, j-1])

    if not return_path_len:
        return float(dtw[n, m])

    i, j = n, m
    path_len = 0
    while i > 0 or j > 0:
        path_len += 1
        if i == 0:
            j -= 1
            continue
        if j == 0:
            i -= 1
            continue
        choices = [(dtw[i-1, j-1], i-1, j-1), (dtw[i-1, j], i-1, j), (dtw[i, j-1], i, j-1)]
        prev_cost, pi, pj = min(choices, key=lambda x: x[0])
        i, j = pi, pj
    return float(dtw[n, m]), path_len


def similarity_score_from_distances(D, alpha=0.005):
    n = D.shape[0]
    if n < 2:
        return None
    vals = []
    for i in range(n):
        for j in range(i+1, n):
            if np.isfinite(D[i, j]):
                vals.append(D[i, j])
    if len(vals) == 0:
        return None
    mean_dist = float(np.mean(vals))
    score = 100.0 * math.exp(-alpha * mean_dist)
    return score, mean_dist


if __name__ == '__main__':
    files = ['Sammy_LatPulls_1.csv', 'Sammy_LatPulls_2.csv', 'Sammy_LatPulls_3.csv']
    # include the variable trial only when needed:
    files.append('Sammy_LatPulls_Variable.csv')
    series = []
    labels = []
    for f in files:
        ang = load_elbow_angles(f)
        if ang.size == 0:
            print(f'Warning: {f} contained no data; skipping')
        else:
            series.append(ang)
            labels.append(f)

    if len(series) < 2:
        print('Not enough valid trials to compute DTW.')
    else:
        D = np.zeros((len(series), len(series)), dtype=float)
        for i in range(len(series)):
            for j in range(i+1, len(series)):
                D[i, j] = dtw_distance(series[i], series[j])
                D[j, i] = D[i, j]
        print('Labels:', labels)
        print('Pairwise DTW distance matrix (raw):')
        print(D)
        res = similarity_score_from_distances(D)
        if res is not None:
            score, mean_dist = res
            print(f'Mean DTW distance: {mean_dist:.4f}')
            print(f'Similarity score (0-100, higher = more similar): {score:.2f}')

        # normalized (z-normalize + divide by path length)
        z_series = [z_normalize(s) for s in series]
        n = len(z_series)
        D_norm = np.zeros((n, n), dtype=float)
        for i in range(n):
            for j in range(i+1, n):
                cost, path_len = dtw_distance(z_series[i], z_series[j], return_path_len=True)
                D_norm[i, j] = cost / path_len if path_len > 0 else float('inf')
                D_norm[j, i] = D_norm[i, j]
        print('\nPairwise DTW distance matrix (z-normalized, cost/path_len):')
        print(D_norm)
        res2 = similarity_score_from_distances(D_norm)
        if res2 is not None:
            score2, mean_dist2 = res2
            print(f'Mean normalized DTW distance: {mean_dist2:.6f}')
            print(f'Normalized similarity score (0-100, higher = more similar): {score2:.2f}')

        # Create heatmap for normalized DTW distances
        fig, ax = plt.subplots(figsize=(8, 6))
        im = ax.imshow(D_norm, cmap='YlOrRd', aspect='auto')
        
        # Add colorbar
        cbar = plt.colorbar(im, ax=ax)
        cbar.set_label('Normalized DTW Distance', rotation=270, labelpad=20)
        
        # Set ticks and labels
        trial_labels = [f.replace('Sammy_LatPulls_', 'Trial ').replace('.csv', '') for f in labels]
        ax.set_xticks(np.arange(len(trial_labels)))
        ax.set_yticks(np.arange(len(trial_labels)))
        ax.set_xticklabels(trial_labels)
        ax.set_yticklabels(trial_labels)
        
        # Rotate the tick labels for better readability
        plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")
        
        # Add text annotations with values
        for i in range(len(trial_labels)):
            for j in range(len(trial_labels)):
                text = ax.text(j, i, f'{D_norm[i, j]:.4f}',
                             ha="center", va="center", color="black" if D_norm[i, j] > 0.015 else "white",
                             fontsize=10)
        
        ax.set_title('Pairwise Normalized DTW Distance Matrix\nLat Pulls Trials')
        fig.tight_layout()
        plt.savefig('latpulls_dtw_heatmap.png', dpi=150, bbox_inches='tight')
        print('\nHeatmap saved as: latpulls_dtw_heatmap.png')
        plt.show()

        # --- Statistical Analysis: Test if trials are significantly different ---
        print('\n' + '='*60)
        print('STATISTICAL ANALYSIS: Testing for significant differences')
        print('='*60)
        
        # For each trial, collect its distances to all other trials
        trial_distances = {}
        for i in range(n):
            distances_to_others = []
            for j in range(n):
                if i != j:
                    distances_to_others.append(D_norm[i, j])
            trial_distances[labels[i]] = np.array(distances_to_others)
        
        # Display mean distance for each trial to others
        print('\nMean distance of each trial to all others:')
        all_means = []
        for lab, dists in trial_distances.items():
            mean_d = np.mean(dists)
            std_d = np.std(dists, ddof=1) if len(dists) > 1 else 0
            all_means.append(mean_d)
            trial_name = lab.replace('Sammy_LatPulls_', 'Trial ').replace('.csv', '')
            print(f'  {trial_name}: {mean_d:.6f} ± {std_d:.6f}')
        
        # Identify if Variable trial exists and compare it to standard trials
        variable_idx = None
        standard_indices = []
        for i, lab in enumerate(labels):
            if 'Variable' in lab:
                variable_idx = i
            else:
                standard_indices.append(i)
        
        if variable_idx is not None and len(standard_indices) >= 2:
            print('\n--- Comparing Variable trial vs. Standard trials (1-3) ---')
            
            # Get distances between standard trials (baseline consistency)
            standard_distances = []
            for i in standard_indices:
                for j in standard_indices:
                    if i < j:
                        standard_distances.append(D_norm[i, j])
            
            # Get distances from Variable trial to standard trials
            variable_distances = []
            for i in standard_indices:
                variable_distances.append(D_norm[variable_idx, i])
            
            standard_distances = np.array(standard_distances)
            variable_distances = np.array(variable_distances)
            
            print(f'\nStandard trial pairwise distances: {standard_distances}')
            print(f'  Mean: {np.mean(standard_distances):.6f}, Std: {np.std(standard_distances, ddof=1):.6f}')
            print(f'\nVariable trial distances to standards: {variable_distances}')
            print(f'  Mean: {np.mean(variable_distances):.6f}, Std: {np.std(variable_distances, ddof=1):.6f}')
            
            # Two-sample t-test: Are Variable distances significantly larger?
            t_stat, p_value = stats.ttest_ind(variable_distances, standard_distances)
            print(f'\nTwo-sample t-test (Variable vs. Standard distances):')
            print(f'  t-statistic: {t_stat:.4f}')
            print(f'  p-value: {p_value:.4f}')
            
            if p_value < 0.05:
                print(f'  → Variable trial is SIGNIFICANTLY DIFFERENT (p < 0.05)')
            else:
                print(f'  → No significant difference detected (p >= 0.05)')
            
            # Effect size (Cohen's d)
            pooled_std = np.sqrt(((len(variable_distances)-1)*np.var(variable_distances, ddof=1) + 
                                  (len(standard_distances)-1)*np.var(standard_distances, ddof=1)) / 
                                 (len(variable_distances) + len(standard_distances) - 2))
            cohens_d = (np.mean(variable_distances) - np.mean(standard_distances)) / pooled_std if pooled_std > 0 else 0
            print(f'  Cohen\'s d (effect size): {cohens_d:.4f}')
            if abs(cohens_d) < 0.2:
                print(f'    → Small effect')
            elif abs(cohens_d) < 0.8:
                print(f'    → Medium effect')
            else:
                print(f'    → Large effect')
        
        # Pairwise t-tests between all trials (using their distance profiles)
        print('\n--- Pairwise comparisons between individual trials ---')
        print('(Comparing each trial\'s distance profile to others)\n')
        
        for i in range(len(labels)):
            for j in range(i+1, len(labels)):
                trial_i = labels[i].replace('Sammy_LatPulls_', 'Trial ').replace('.csv', '')
                trial_j = labels[j].replace('Sammy_LatPulls_', 'Trial ').replace('.csv', '')
                
                # Get distance profiles (distances to all other trials except each other)
                dist_i = np.array([D_norm[i, k] for k in range(n) if k != i and k != j])
                dist_j = np.array([D_norm[j, k] for k in range(n) if k != i and k != j])
                
                if len(dist_i) >= 2 and len(dist_j) >= 2:
                    t_stat, p_value = stats.ttest_ind(dist_i, dist_j)
                    sig_marker = '**' if p_value < 0.05 else ''
                    print(f'{trial_i} vs {trial_j}: t={t_stat:.3f}, p={p_value:.4f} {sig_marker}')
                else:
                    # For small sample sizes, just report the direct distance
                    direct_dist = D_norm[i, j]
                    print(f'{trial_i} vs {trial_j}: Direct distance = {direct_dist:.6f} (insufficient data for t-test)')
        
        print('\n** indicates significant difference at p < 0.05')
        print('='*60)

        # --- Compare variability against the mean motion across trials ---
        # Resample z-normalized series to a common length (median length) and compute mean template
        lengths = [len(s) for s in z_series]
        if len(lengths) >= 1:
            L = int(np.median(lengths)) if len(lengths) > 0 else None
        else:
            L = None

        if L is None or L <= 1:
            print('Not enough data to build mean motion.')
        else:
            x_new = np.linspace(0.0, 1.0, L)
            resampled = []
            for s in z_series:
                if len(s) == 0:
                    resampled.append(np.zeros(L))
                    continue
                x_orig = np.linspace(0.0, 1.0, len(s))
                res = np.interp(x_new, x_orig, s)
                resampled.append(res)
            resampled = np.vstack(resampled)
            mean_series = np.mean(resampled, axis=0)

            # compute DTW distance of each (resampled) z-series to mean_series
            dist_to_mean = []
            for i, s in enumerate(resampled):
                cost, path_len = dtw_distance(s, mean_series, return_path_len=True)
                norm_cost = cost / path_len if path_len > 0 else float('inf')
                dist_to_mean.append(norm_cost)

            dist_to_mean = np.array(dist_to_mean)
            print('\nPer-trial normalized DTW distance to mean template:')
            for lab, d in zip(labels, dist_to_mean):
                print(f'  {lab}: {d:.6f}')

            # produce a score from mean distance to mean template
            finite = dist_to_mean[np.isfinite(dist_to_mean)]
            if finite.size == 0:
                print('Could not compute variability score (no finite distances).')
            else:
                mean_dist_mean = float(np.mean(finite))
                # reuse exponential mapping; optionally tweak alpha for sensitivity
                alpha_mean = 20.0
                score_mean = 100.0 * math.exp(-alpha_mean * mean_dist_mean)
                print(f'Mean distance to mean template: {mean_dist_mean:.6f}')
                print(f'Variability similarity score (0-100, higher = more similar to mean): {score_mean:.2f}')
