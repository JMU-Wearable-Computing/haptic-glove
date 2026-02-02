"""
Compute DTW distances between Sammy Macarena elbow-angle trials
and produce a similarity score (higher = less variance).

Usage: run this file. It will print pairwise DTW distances and
an overall similarity score scaled 0-100.
"""
import os
import numpy as np
import math


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

    # compute elbow angle same as in main script
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
    """Compute DTW distance between 1D sequences s1 and s2.
    If window is provided (int), limit warping window (Sakoe-Chiba).
    If return_path_len is True, also return the length of the optimal warping path.
    """
    n, m = len(s1), len(s2)
    if n == 0 or m == 0:
        return (float('inf'), 0) if return_path_len else float('inf')
    if window is None:
        window = max(n, m)
    window = max(window, abs(n - m))

    # initialize cost matrix with infinities
    dtw = np.full((n+1, m+1), np.inf)
    dtw[0, 0] = 0.0

    for i in range(1, n+1):
        start_j = max(1, i - window)
        end_j = min(m, i + window)
        for j in range(start_j, end_j+1):
            cost = abs(s1[i-1] - s2[j-1])
            dtw[i, j] = cost + min(dtw[i-1, j],    # insertion
                                   dtw[i, j-1],    # deletion
                                   dtw[i-1, j-1])  # match

    if not return_path_len:
        return float(dtw[n, m])

    # backtrack path length
    i, j = n, m
    path_len = 0
    while i > 0 or j > 0:
        path_len += 1
        # when at edges, step accordingly
        if i == 0:
            j -= 1
            continue
        if j == 0:
            i -= 1
            continue
        # choose predecessor with smallest cumulative cost
        choices = [(dtw[i-1, j-1], i-1, j-1), (dtw[i-1, j], i-1, j), (dtw[i, j-1], i, j-1)]
        prev_cost, pi, pj = min(choices, key=lambda x: x[0])
        i, j = pi, pj
    return float(dtw[n, m]), path_len


def pairwise_dtw(series_list, window=None):
    n = len(series_list)
    D = np.zeros((n, n), dtype=float)
    for i in range(n):
        for j in range(i+1, n):
            d = dtw_distance(series_list[i], series_list[j], window=window)
            D[i, j] = d
            D[j, i] = d
    return D


def similarity_score_from_distances(D):
    # D: symmetric pairwise distance matrix, zeros on diagonal
    # compute mean of upper-triangle distances (excluding inf)
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
    # map to 0-100 where higher means more similar (less variance)
    # use exponential scaling so differences compress and produce a more intuitive score
    # alpha controls steepness; smaller alpha -> higher scores for same mean_dist
    alpha = 0.005
    score = 100.0 * math.exp(-alpha * mean_dist)
    return score, mean_dist


if __name__ == '__main__':
    # load macarena trials
    files = ['Sammy_Macarena_000.csv', 'Sammy_Macarena_001.csv', 'Sammy_Macarena_002.csv', 'Sammy_Macarena_003.csv']
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
        # option 1: raw DTW distances
        D = pairwise_dtw(series, window=None)
        print('Labels:', labels)
        print('Pairwise DTW distance matrix (raw):')
        print(D)
        res = similarity_score_from_distances(D)
        if res is None:
            print('Could not compute similarity score (no finite distances).')
        else:
            score, mean_dist = res
            print(f'Mean pairwise DTW distance: {mean_dist:.4f}')
            print(f'Similarity score (0-100, higher = more similar) [exp scaling]: {score:.2f}')

        # option 2: z-normalize series and use DTW normalized by warping path length
        z_series = [z_normalize(s) for s in series]
        n = len(z_series)
        D_norm = np.zeros((n, n), dtype=float)
        for i in range(n):
            for j in range(i+1, n):
                cost, path_len = dtw_distance(z_series[i], z_series[j], window=None, return_path_len=True)
                if path_len > 0:
                    norm_cost = cost / path_len
                else:
                    norm_cost = float('inf')
                D_norm[i, j] = norm_cost
                D_norm[j, i] = norm_cost

        print('\nPairwise DTW distance matrix (z-normalized, cost/path_len):')
        print(D_norm)
        res2 = similarity_score_from_distances(D_norm)
        if res2 is None:
            print('Could not compute normalized similarity score.')
        else:
            score2, mean_dist2 = res2
            print(f'Mean normalized DTW distance: {mean_dist2:.6f}')
            print(f'Normalized similarity score (0-100, higher = more similar): {score2:.2f}')

        # --- Compare variability against the mean motion across trials ---
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

            finite = dist_to_mean[np.isfinite(dist_to_mean)]
            if finite.size == 0:
                print('Could not compute variability score (no finite distances).')
            else:
                mean_dist_mean = float(np.mean(finite))
                alpha_mean = 20.0
                score_mean = 100.0 * math.exp(-alpha_mean * mean_dist_mean)
                print(f'Mean distance to mean template: {mean_dist_mean:.6f}')
                print(f'Variability similarity score (0-100, higher = more similar to mean): {score_mean:.2f}')
