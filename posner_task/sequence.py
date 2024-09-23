from pathlib import Path
import collections
import csv
import numpy as np


class Block(collections.abc.Iterator):

    def __init__(self, n_trials, p_valid, min_dist=3, max_iter=1000):
        self.side, self.valid = self.make_trial_sequence(
            n_trials, p_valid, min_dist, max_iter
        )
        self.n_trials = n_trials
        self.this_n = 0
        self.response = [None] * n_trials
        self.response_time = [None] * n_trials

    def __next__(self):
        if self.this_n == self.n_trials:
            raise StopIteration
        else:
            self.this_n += 1
            return self.side[self.this_n - 1], self.valid[self.this_n - 1]

    @staticmethod
    def make_trial_sequence(n_trials, p_valid, min_dist=3, max_iter=1000):
        side, valid = [], []
        if n_trials / 2 * p_valid % 1 != 0:
            raise ValueError("Trials can't be evenly divided between conditions!")

        for s in ["left", "right"]:
            n = int(n_trials / 2)
            side += [s] * n
            n_valid = int(n * p_valid)
            valid += [True] * n_valid + [False] * (n - n_valid)

        ok, count = 0, 0
        while not ok:
            idx = np.random.choice(n_trials, n_trials, replace=False)
            side = np.asarray(side)[idx]
            valid = np.asarray(valid)[idx]
            dist = np.diff(np.where(valid == False)[0])
            if dist.min() >= min_dist:
                ok = 1
            count += 1
            if count >= max_iter:
                raise ValueError(f"Couldn't find sequence after {max_iter} iterations!")
        return side, valid

    def add_response(self, response, response_time):
        if self.this_n == 0:
            raise ValueError("Sequence has not been started!")
        else:
            self.response[self.this_n - 1] = response
            self.response_time[self.this_n - 1] = response_time

    def save(self, path, mkdir=False):
        path = Path(path)
        if not path.suffix == ".csv":
            path = path.parent / (path.name + ".csv")
        if not path.parent.exists():
            if mkdir:
                path.parent.mkdir(parents=True)
            else:
                raise ValueError(f"Folder {path.parent} does not exist!")
        rows = zip(self.side, self.valid, self.response, self.response_time)
        with open(path, "w", newline="") as csvfile:
            csvwriter = csv.writer(csvfile)
            csvwriter.writerow(["side", "valid", "response", "time"])  # header
            csvwriter.writerows(rows)  # data
