import numpy as np
from scipy.cluster.vq import kmeans, whiten

def extract_features_from_relevances(relevances):
    """Extracts "blobs" of relevant features from a set of LRP relevances
    inputs
    relevances: relevances generating from a particular neural network, test image and class label
    output
    array of blobs of relevant pixels
    """

    threshold = 0.0001
    k = 5

    relevances[np.absolute(relevances) < threshold] = 0
    relevant_indices = np.argwhere(relevances != 0)
    whitened_features = whiten(relevant_indices)
    cluster_means = kmeans(whitened_features, k)[0]
    cluster_indices = list(np.apply_along_axis(get_cluster, 1, whitened_features, cluster_means))
    clusters = []
    for i in range(k):
        clusters.append([])

    for i, c in enumerate(cluster_indices):
        clusters[c].append(relevant_indices[i])

    for i in range(k):
        clusters[i] = np.array(clusters[i])

    return clusters

def get_cluster(point, means):
    """Given a specific point and cluster means, find the closest cluster
    point: point to test
    clusters: collection of cluster means
    output
    Index indicating the cluster associated with the poiint
    """

    distance = np.linalg.norm(point-means[0])
    closestIndex = 0

    for i in range(len(means)):
        mean = means[i]
        if  np.linalg.norm(point-mean) < distance:
            distance = np.linalg.norm(point-mean)
            closestIndex = i
    return closestIndex
