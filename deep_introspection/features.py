import numpy as np
from scipy.cluster.vq import kmeans, whiten


def find_cluster(x, y, relevances, visited):
    queue = []
    cluster = []
    queue.append((x,y))
    visited[x, y] = True

    threshold = 1
    # Maximum distance that pixels can be added
    max_distance = 1.5
    max_distance_integer = int(np.ceil(max_distance))
    while queue:
        point = queue.pop()
        cluster.append(point)

        for i in range(-max_distance_integer,max_distance_integer+1):
            for j in range(-max_distance_integer,max_distance_integer+1):
                d = np.linalg.norm(np.array([point[0]+i,point[1]+j])-np.array(point))
                percentage_change = np.absolute(relevances[point[0]+i,point[1]+j]-relevances[point[0],point[1]])/relevances[point[0],point[1]]

                if point[0]+i >= 0 and point[0]+i < relevances.shape[0] and point[1]+j >= 0 and point[1]+j < relevances.shape[1] and not (i == 0 and j == 0) and not visited[point[0]+i,point[1]+j] and relevances[point[0]+i,point[1]+j] != 0 and d <= max_distance and percentage_change < threshold:
                    visited[point[0]+i,point[1]+j] = True
                    queue.append((point[0]+i,point[1]+j))
    return cluster

def extract_features_from_relevances(relevances):
    """Extracts "clusters" of relevant features from a set of LRP relevances
    inputs
    relevances: relevances generating from a particular neural network, test image and class label
    output
    array of clusters of relevant pixels
    """
    # normalise so that total relevance is 1
    relevances/=np.sum(relevances)

    # minimum absolute threshold for relevances to keep
    threshold = 5/relevances.flatten().shape[0]
    relevances[np.absolute(relevances) < threshold] = 0

    # minimum size for a cluster to keep
    min_cluster_size = 20

    # Remove relevances at edges
    mask = np.ones(relevances.shape, np.bool)
    mask[5:relevances.shape[0]-5,5:relevances.shape[1]-5] = 0
    relevances[mask] = 0

    visited = np.zeros(shape=relevances.shape,dtype=np.bool)
    clusters = []
    for x in range(relevances.shape[0]):
        for y in range(relevances.shape[1]):
        # start new cluster
            if not visited[x, y] and relevances[x,y] != 0:
                cluster = find_cluster(x, y, relevances, visited)
                clusters.append(cluster)
    clusters = map((lambda x: list(set(x))), clusters)
    # filter out small clusters
    clusters = filter((lambda x: len(x) > min_cluster_size), clusters)


    return list(clusters)

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
