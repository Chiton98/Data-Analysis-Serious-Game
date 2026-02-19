"""Python file to compute the metrics from users.

""" 

import os
import pandas as pd
import numpy as np
import sys


def compute_numerical_velocity(trajectory_path: str):
    trajectory_file = pd.read_csv(trajectory_path, index_col="sample")

    t = np.asarray(trajectory_file["t"])
    px = trajectory_file["x"]
    py = trajectory_file["y"]
    pz = trajectory_file["z"]

    n = len(t)

    # Use the 1st numerical derivative to compute the velocity
    vx = np.zeros(n)
    vy = np.zeros(n)
    vz = np.zeros(n)

    for i in range(1, n - 1):
        deltaT = t[i + 1] - t[i - 1]
        vx[i] = (px[i + 1] - px[i - 1]) / deltaT
        vy[i] = (py[i + 1] - py[i - 1]) / deltaT
        vz[i] = (pz[i + 1] - pz[i - 1]) / deltaT

    return t, vx, vy, vz

def compute_numerical_jerk(t: np.ndarray, vx: np.ndarray, vy: np.ndarray, vz: np.ndarray):

    n = len(t)

    # Use the 2nd numerical centered derivative to compute the jerk
    jx = np.zeros(n)
    jy = np.zeros(n)
    jz = np.zeros(n)

    for i in range(2, n - 2):
        deltaT = t[i + 1] - t[1]
        jx[i] = (vx[i + 1] - 2 * vx[i] + vx[i - 1]) / (deltaT**2)
        jy[i] = (vy[i + 1] - 2 * vy[i] + vy[i - 1]) / (deltaT**2)
        jz[i] = (vz[i + 1] - 2 * vz[i] + vz[i - 1]) / (deltaT**2)
    return jx, jy, jz

def compute_arc_length(t: np.ndarray, vx: np.ndarray, vy: np.ndarray, vz: np.ndarray):
    n = len(t)
    # Compute the arc length
    S = 0
    for i in range(1, n - 1):
        deltaT = t[i] - t[i - 1]
        S += np.sqrt((vx[i] ** 2 + vy[i] ** 2 + vz[i] ** 2)) * deltaT

    return S

def compute_njs(trajectory_path: str):
    """Function that computes the NJS using the trajectory file
    as a pandas data frame"""

    t, vx, vy, vz = compute_numerical_velocity(trajectory_path)
    jx, jy, jz = compute_numerical_jerk(t, vx, vy, vz)

    n = len(t)

    time = t[n - 1] - t[0]
    arc_length = compute_arc_length(t, vx, vy, vz)
    sumaNJS = 0

    for i in range(2, n - 2):
        squareJerk = jx[i] ** 2 + jy[i] ** 2 + jz[i] ** 2
        squareJerk2 = jx[i + 1] ** 2 + jy[i + 1] ** 2 + jz[i + 1] ** 2
        deltaT = t[i] - t[i - 1]
        sumaNJS += (squareJerk + squareJerk2) * 0.5 * deltaT

    njs = np.sqrt(0.5 * (time**5 / arc_length**2) * sumaNJS)

    return np.log(njs)

def compute_avg_speed(trajectory_path: str):

    t, vx, vy, vz = compute_numerical_velocity(trajectory_path)

    avg_speed = 0

    n = len(t)
    avg_speed = 0

    for i in range(1, n - 1):
        avg_speed += np.sqrt(vx[i] ** 2 + vy[i] ** 2 + vz[i] ** 2)

    avg_speed = avg_speed / (n - 2)

    return t, avg_speed

def compute_score(collisions_path: str):

    try:
        collisions_file = pd.read_csv(collisions_path)

        red_balls = collisions_file[collisions_file[" Ball Color"] == "Red"].shape[0]

        green_balls = collisions_file[collisions_file[" Ball Color"] == "Green"].shape[
            0
        ]

        score = green_balls - red_balls
    except:
        score = 0

    return score

def compute_time(t: np.ndarray):
    n = len(t)
    return t[n - 1] - t[0]


# ---------------- MAIN PROGRAM ---------------- #
if __name__ == "__main__":
    # Data path is given from command line
    data_path = sys.argv[1]

    boards = ["c0", "c1", "c2", "c3", "c4", "c5", "c6", "c7", "c8", "c9", "c10", "c11"]

    metrics = ["NJS", "Avg. Speed", "Score", "CompletedTime"]

    metric_information_njs = {}
    metric_information_avg_speed = {}
    metric_information_score = {}
    metric_information_time = {}

    metrics_information_dicts = [0, 1, 3, 4]

    for user in os.listdir(data_path):
        user_path = os.path.join(data_path, user)
        positions_path = os.path.join(user_path, "Positions")
        collisions_path = os.path.join(user_path, "Collisions")

        print(f"Generando resultados para {user}")

        # Open experiment results.csv
        experiment_results = pd.read_csv(
            os.path.join(user_path, "ExperimentResults.csv"), index_col="CompletedOrder"
        )

        # Iterate trough each board to get the metrics
        for b in boards:
            trajectory_path = os.path.join(positions_path, f"Board{b}.csv")
            collisions_file = os.path.join(collisions_path, f"Board{b}.csv")

            njs = compute_njs(trajectory_path)
            metric_information_njs[b] = np.round(njs, 3)

            t, avg_speed = compute_avg_speed(trajectory_path)
            metric_information_avg_speed[b] = np.round(avg_speed, 3)

            score = compute_score(collisions_file)
            metric_information_score[b] = np.round(score, 3)

            time = compute_time(t)
            metric_information_time[b] = np.round(time, 3)

        # Go from label to value
        experiment_results["NJS"] = (
            experiment_results["Identifier"]
            .map(metric_information_njs)
            .combine_first(experiment_results["NJS"])
        )

        experiment_results["Avg. Speed"] = (
            experiment_results["Identifier"]
            .map(metric_information_avg_speed)
            .combine_first(experiment_results["Avg. Speed"])
        )

        experiment_results["CompletedTime"] = (
            experiment_results["Identifier"]
            .map(metric_information_time)
            .combine_first(experiment_results["CompletedTime"])
        )

        experiment_results["Score"] = (
            experiment_results["Identifier"]
            .map(metric_information_score)
            .combine_first(experiment_results["Score"])
        )

        # Save the modified file
        experiment_results.to_csv(os.path.join(user_path, "ExperimentResults.csv"))
