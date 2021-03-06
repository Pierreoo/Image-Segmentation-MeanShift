import numpy as np
import scipy.spatial.distance


def findpeak(data, idx, r):
    data_point = data[idx, :].reshape(1, -1)
    threshold = 0.01
    # Initialization of high shift to enable converging in the while statement
    shift = np.amax(data) - np.amin(data)
    # The index of surrounding data points are retained for shift manipulation
    while shift > threshold:
        distances = scipy.spatial.distance.cdist(data_point, data, metric='euclidean')
        neighbors = np.where(distances <= r)[-1]
        data_points_neighbors = data[neighbors, :]
        mean = np.mean(data_points_neighbors, axis=0).reshape(1, 3)
        shift = scipy.spatial.distance.cdist(data_point, mean, metric='euclidean')
        data_point = mean
    # When shift becomes relatively small, peak is reached ans defined
    else:
        peak = mean
    return peak


def meanshift(data, r):
    # Labels of data point are initialize at 0
    labels = np.zeros((len(data), 1), dtype=int)
    peaks = np.empty((0, len(data[0])))
    peak_labels = []
    # Every data point's corresponding peak is tested if it entails a newly discovered peak
    for i in range(0, len(data)):
        peak_potential = findpeak(data, i, r)
        distances_peak = scipy.spatial.distance.cdist(peak_potential, peaks, metric='euclidean')
        neighbors_peak = np.where(distances_peak <= r / 2)[-1]
        # The first peak found has logically no neighbors and thus added to the list of unique peaks
        # The same applies for an isolated peak which can be considered new
        if neighbors_peak.size == 0:
            # !Labelling starts from 1
            labels[i] = np.amax(labels) + 1
            peak_labels = np.append(peak_labels, labels[i], axis=0)
            peaks = np.append(peaks, peak_potential, axis=0)
        # When a potential peak is close to another, they are assumed the same.
        # Therefore, the same label as the close one is assigned to the data point
        elif neighbors_peak.size == 1:
            labels[i] = peak_labels[neighbors_peak]
        # Similar peaks were merged and considered the same
        else:
            labels[i] = peak_labels[np.random.choice(neighbors_peak)]
    return labels, peaks


def meanshift_opt(data, r, c):
    labels = np.zeros((len(data), 1))
    peaks = np.empty((0, len(data[0])))
    peak_labels = []
    for i in range(0, len(data)):
        # Data point with other than initialized label 0 has a peak already, so continue to the next data point
        if labels[i] != 0:
            continue
        peak_potential, cpts = findpeak_opt(data, i, r, c)
        distances_peak = scipy.spatial.distance.cdist(peak_potential, peaks, metric='euclidean')
        neighbors_peak = np.where(distances_peak <= r / 2)[-1]
        if neighbors_peak.size == 0:
            labels[i] = np.amax(labels) + 1
            peak_labels = np.append(peak_labels, labels[i], axis=0)
            peaks = np.append(peaks, peak_potential, axis=0)

            # Optimization techniques
            distances_peak_points = scipy.spatial.distance.cdist(peak_potential, data, metric='euclidean')
            # First speedup
            peak_basin = (distances_peak_points <= r)
            # First + second speedup are merged according to index
            speedup = (peak_basin + cpts.transpose())
            # Indices which were marked by the speedups with non zero values are retained
            speedup_close = np.nonzero(speedup)[-1]
            # Close data points are marked the same label as the performed data point i
            labels[speedup_close] = labels[i]
        elif neighbors_peak.size == 1:
            labels[i] = peak_labels[neighbors_peak]
            speedup = cpts.transpose()
            speedup_close = np.nonzero(speedup)[-1]
            labels[speedup_close] = labels[i]
        else:
            labels[i] = peak_labels[np.random.choice(neighbors_peak)]
            speedup = cpts.transpose()
            speedup_close = np.nonzero(speedup)[-1]
            labels[speedup_close] = labels[i]
    return labels, peaks


def findpeak_opt(data, idx, r, c):
    data_point = data[idx, :].reshape(1, -1)
    cpts = np.zeros((len(data), 1))
    threshold = 0.01
    shift = np.amax(data) - np.amin(data)
    while shift > threshold:
        distances = scipy.spatial.distance.cdist(data_point, data, metric='euclidean')
        neighbors = np.where(distances <= r)[-1]
        data_points_neighbors = data[neighbors, :]
        mean = np.mean(data_points_neighbors, axis=0).reshape(1, -1)
        shift = scipy.spatial.distance.cdist(data_point, mean, metric='euclidean')
        data_point = mean

        # Second speedup: indices of close points are marked with the value 1
        neighbors_close = np.where(distances <= r / c)[-1]
        cpts[neighbors_close] = 1
    else:
        peak = mean
    return peak, cpts
