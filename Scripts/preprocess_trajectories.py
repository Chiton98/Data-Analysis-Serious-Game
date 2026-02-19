# Python file for preprocess the trajectories

import os
import pandas as pd
import numpy as np
import sys

if __name__ == "__main__":
    data_path = sys.argv[1]

    for user in os.listdir(data_path):
        positions_path = os.path.join(data_path, user, 'Positions')
        print(f'Modificando usuario {user}')
        for b in os.listdir(positions_path):
            trajectory_path = os.path.join(positions_path, b)
            trajectory_file = pd.read_csv(trajectory_path, index_col = "sample")
            trajectory_file.index.name = "samples"

            # Some players played more than 60 seconds(my error), so I need to deleted the data where t is not > 60, so t <=60
            filtered_df = trajectory_file[trajectory_file['t'] <=60.000]

            # For eliminating the duplicates caused by pausing the game
            filtered_df = filtered_df.drop_duplicates('t')

            # Update index of samples
            n_rows = filtered_df.shape[0] 
            new_samples = np.arange(0, n_rows)     
            filtered_df.index = new_samples
            filtered_df.index.name = 'sample'

            filtered_df.to_csv(trajectory_path)
