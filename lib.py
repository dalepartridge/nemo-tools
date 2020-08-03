import scipy.spatial
import numpy as np

def nearest(lon, lat, glon, glat):
    """
    Find the indices nearest to each point in the given list of
    longitudes and latitudes.

    Parameters
    ----------
    lon : ndarray,
        longitude of points to find
    lat : ndarray
        latitude of points to find

    Returns
    -------
    indices : tuple of ndarray
        The indices for each dimension of the grid that are closest
        to the lon/lat points specified
    """

    xy = np.dstack([glat.ravel(), glon.ravel()])[0]
    pts = np.dstack([np.atleast_1d(lat), np.atleast_1d(lon)])[0]
    grid_tree = scipy.spatial.cKDTree(xy)
    dist, idx = grid_tree.query(pts)
    return np.unravel_index(idx, glat.shape)

