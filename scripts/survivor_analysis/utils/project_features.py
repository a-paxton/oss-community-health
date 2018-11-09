import numpy as np


def compute_bus_factor(commits, n_committers=5):
    """
    Compute bus factor

    Parameters
    ----------
    commits : pd.DataFrame
        Data Frame containing the commit information.

    n_committers : int, optional, default: 5
        Number of committers to consider in the bus factor

    Returns
    -------
    bus_factor: Lower is better
    """

    commits["author_name"] = commits["author_name"].replace(
        np.nan, "", regex=True)
    _, commits_counts = np.unique(commits["author_name"], return_counts=True)
    commits_counts.sort()
    commits_counts = commits_counts[::-1].astype(float)
    commits_counts /= commits_counts.max()
    bus_factor = np.mean(1 - commits_counts[:n_committers])
    return bus_factor
