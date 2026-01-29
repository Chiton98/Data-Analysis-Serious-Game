# Python file for defining the user data base.

import os 
import os.path
import json
import random
import pathlib

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from Patient import Patient

class Board:
    def __init__(self,id, green_balls, figure, size):
        self.id = id
        self.green_balls = int(green_balls)
        self.figure = figure
        self.size = size

class UserDataBase:
    def __init__(self, path_data:str):
        
        self.path_database = path_data

        # For storing name/Patient object
        self.patients = {}

        # For storing each Patient for the designed group
        self.group_ajs = []
        self.group_ams = []
        self.group_amd = []
        

        # Extension for saving the graphs
        self.extension = "png"

        # Generate the list of boards
        self.boards = {}

        # List of groups
        self.groups_ids = ["AJS", "AMS", "AMD"]

        # List of metrics
        self.metrics_ids = ["NJS", "Score", "CompletedTime", "Avg.Speed"]

        self._generate_set_of_boards()

    def _generate_set_of_boards(self):
        self.sizes = ["3x3", "5x5", "7x7"]
        self.figures = ["Cuadrado", "Letra Z", "Ajedrez"]

        id = -1
        for size in self.sizes:
            for figure in self.figures:
                id+=1
                self.boards[f'c{id}'] = (size, figure)
    
    def load_data(self):
        """Loads the data stored in the disk

        Take the data of all the users that played the game 
        and load it to memory to its manipulation.
        
        """
        #List for map for old group to new name
        old_group_to_new = {"JOV":"AJS","NOR":"AMS","DCL":"AMD", 
                            "Control Sano": "AJS", "Adulto Sano":"AMS"}

        # Get
        user_names = os.listdir(self.path_database)
        
        for user in user_names:
            # Read the "Information.json file"
            user_path = os.path.join(self.path_database, user)

            json_file = open(os.path.join(user_path,"Information.json"))

            json_object = json.load(json_file)

            json_file.close()

            # Create a new patient from json information
            patient = Patient(json_object["Name"], json_object["Age"], json_object["Genre"], json_object["Condition"])

            # Load the patient collisions of all played boards
            self._load_collision_information_all_boards(user_path, patient)

            # Update group tag for patient
            p = patient.group == "JOV" or patient.group == "NOR" or patient.group == "DCL"
            q = patient.group =="Adulto Sano" or patient.group == "Control Sano"

            if p or q:
                patient.group = old_group_to_new[patient.group]
            
            # Assign patient to list
            self._asign_patient(patient)
    

    # -------------- GETTERS AND SETTERS OF PROPERTIES
    def set_extension_file(self, extension:str):
        self.extension = extension

    # --------------- SET OF FUNCTIONS TO GENERATE THE GRAPHS ---------------- 

    # ------------ SET 1: Generate Positions ------------------
    # Function 5
    def generate_positions_patient(self, patient_name:str, board_ids: list):
        """
        Generates the 3D position curve of the person with name "patient_name"
        for the boards presented on list "board_ids".
        
        """
        #Check if the patient_name exists
        if patient_name in self.patients:
            for board_id in board_ids:
                # Go to the path where user's position files are.
                positions_path = os.path.join(self.path_database, patient_name, 'Positions')

                # Set the file name of position
                board_to_load =  f'Board{board_id}Trial1.csv'

                path_to_board = os.path.join(positions_path, board_to_load)

                # Only plot the positions if the file exists

                if(pathlib.Path(path_to_board).exists()):
                    position_plot = self._preprocess_information(path_to_board)
                    self._plot_information(position_plot, patient_name, board_id, save_graph=True, show_name=False)
                else:
                    print(f"Lo siento. El paciente {patient_name} no completó el tablero {board_id}")
        else:
            print(f"Error. El paciente {patient_name} no existe.")
        
    # Function 7
    def generate_positions_group(self, group_name:str, board_ids:list)->str:
        """
        Generates the 3D position curve of a random patient of the group "group_name"
        for the list of boards "board_ids".
        """

        group_selected = 0

        if group_name == "AJS":
            group_selected = self.group_ajs
        elif group_name == "AMS":
            group_selected = self.group_ams
        elif group_name == "AMD":
            group_selected = self.group_amd
        
        #Check if group_name is valid
        if group_name in ["AJS", "AMS", "AMD"]:
            n = len(group_selected)

            i = random.randint(0, n - 1)

            # Get the object of the randomly selected object
            patient_selected = group_selected[i]

            # Call the function with name
           #print(f"Generando gráfica para {group_name}")
            self.generate_positions_patient(patient_selected.name, board_ids)

            # Return the patient_name after processing all the boards
            return patient_selected.name 
        else:
            print(f"Error. El grupo {group_name} seleccionado no existe.")

    # Function 8
    def generate_comparing_positions_name(self, patient_names:str, board_ids:list):
        """
            Generates 1 graph comparing the 3D positions of the patients 
            in "patient_names" of the boards in "board_ids". 
        """ 
    
        for board_id in board_ids:
            # print(f'Generando gráfica para el tablero {board_id}')
            # Check if board is on data base continue
            if board_id in self.boards:
                
                #Create the figure to plot the graph
                fig = plt.figure(figsize=(4,3), dpi=300)               

                #Create the figure to plot the graph
                axes = fig.add_subplot(projection = '3d')

                axes.set_title(f"Comparación de trayectorias para tablero {board_id}")

                label_legends = []

                # Add the plot of each patient to the "axes"
                for patient_name in patient_names:
                    
                    #print(f'    Generando gráfica del paciente {patient_name}')
                    
                    #Check if user is on data base
                    if patient_name in self.patients:  
                        path_to_board = self._get_path_to_board(patient_name, board_id)
                        trajectory = self._preprocess_information(path_to_board)
                        label_legends.append(self.patients[patient_name].group)

                        #Plot the trajectory on the axs
                        self._plot_on_axes(axes, trajectory)
                    else:
                        print("    Error. El paciente no existe. No es añadido a la gráfica.")

                    #Set the legend to the axis (Corregir mañana)
                    axes.legend(label_legends)

                    save_directory = os.path.join(os.getcwd(), "Multiple Trajectories Figures")
                    file_name = f'MultipleTrajectories-Board{board_id}.{self.extension}'

                    if(not(pathlib.Path(save_directory).exists())):
                        os.mkdir(save_directory)
                        fig.savefig(os.path.join(save_directory, file_name), bbox_inches='tight', pad_inches=0.3)
            


                    path_to_save = os.path.join(save_directory, file_name)

                    #Save the figure
                    fig.savefig(path_to_save)

                    plt.close()
        
            else:
                print(f'El tablero {board_id} no existe. No se pudo graficar.')


    # ------------ SET 2: Generate Metrics ------------------
    def generate_all_experiment_results(self, all_data_set = True, by_groups = True):
        """
        Generates a single csv file that contains the information of the 
        "ExperimentResults.csv" file of all individual patients.
        """     

        patient_dfs_list = []

        patient_ajs = []
        patient_ams = []
        patient_amd = []

        for patient_name in self.patients:

            experiment_results_path = os.path.join(self.path_database, patient_name, 'ExperimentResults.csv')

            # Load the csv file as a pandas 
            df = pd.read_csv(experiment_results_path)

            # Set the index the column of the board "Identifier"
            df = df.set_index('CompletedOrder')
    

            # Fix the columns "Std. Avg. Speed"
            df = df.rename({"Avg. Speed": "Avg.Speed", 
                            "Avg. Acc" : "Avg.Acc"}, axis=1)
            
            
            patient_dfs_list.append(df)

            if self.patients[patient_name].group == "AJS":
                patient_ajs.append(df)
            elif self.patients[patient_name].group == "AMS":
                patient_ams.append(df)
            elif self.patients[patient_name].group == "AMD":
                patient_amd.append(df)

        if(all_data_set):
            result = pd.concat(patient_dfs_list)
            result.to_csv('AllExperimentResults.csv')
        
        if(by_groups):
            ajs = pd.concat(patient_ajs)
            ams = pd.concat(patient_ams)
            amd = pd.concat(patient_amd)

            ajs.to_csv('AJS-AllExperimentResults.csv') 
            ams.to_csv('AMS-AllExperimentResults.csv') 
            amd.to_csv('AMD-AllExperimentResults.csv') 

    def generate_metric_graph(self, m:str, t: str):
        """
            Generates a box plot graph of groups AMS, AJS, AMD
            of the average metric "m" and board "t".
        
        """

        if(not(t in self.boards)):
            print(f"El tablero {t} no existe. Inserte otro.")
            return

        save_directory = os.path.join(os.getcwd(), "MetricsResponse")

        if ( not(os.path.isdir(save_directory)) ):
            os.mkdir(save_directory)

        # 1. Check if the file that have all the result experiments exists      
        file_path = 'AllExperimentResults.csv'

        if not(os.path.exists(file_path)):
            print(f'El archivo no existe. Generandolo.')
            self.generate_all_experiment_results()

        data_frames = []
        
        for g in self.groups_ids:
            # 2. Open the file as a pandas DataFrame
            df = pd.read_csv(f'{g}-AllExperimentResults.csv', index_col = 1)  #Column at position 1 is the index(Board Identifier)

            # 3. Extract only column 'm' and row 't'
            if m not in df.columns:
                print(f"Required column {m} not found in the DataFrame.")
            else:
                # Select the board 't'
                df_filtered = df.loc[t]
                
                # Select the metric 'm' and Change the column label
                metric_column = df_filtered[[m]].rename(columns = {m:g})    
                data_frames.append(metric_column)
        
        final_frame = pd.concat(data_frames)

        #Create figure and anxes
        figure, axes = plt.subplots(figsize = (5.2,3))
        
        # Change the style of the box plot -> Pendiente #AJS BLUE, AMS ORANGE, AMD GREEN
        metric_to_unit = self._metric_to_unit(m)
        axes.set_ylabel(f"{metric_to_unit}")

        y_min, y_max = self._metric_to_limits(m)

        axes.set_ylim(y_min, y_max)

        # Draw and horizontal line to show the max possible value 
        #

        if m == 'Score' or m == 'CompletedTime':
            y_max_possible_value = self._metric_to_max_possible_value(m, t)
            axes.hlines(y_max_possible_value, [1], 3, lw=2, colors='r', label= 'Valor máximo posible')
            axes.legend(loc='upper right')

        # Make the box plot
        final_frame.plot.box(ax = axes)

        # Create the folder to save the metric
        folder_metric = os.path.join(save_directory, f'{m}')

        if(not(os.path.isdir(folder_metric))):
            os.mkdir(folder_metric)

        # Add legends
        

        file_path = os.path.join(folder_metric,f"{m}-{t}.{self.extension}" )
        figure.savefig(file_path)
        plt.close()

    def _metric_to_unit(self, m:str):
        if m == 'NJS':
            return 'NJS'
        elif m == 'Score':
            return 'Puntaje'
        elif m == 'CompletedTime':
            return 'Segundos (s.)'
        
        elif m == 'Avg.Speed':
            return 'Rapidez promedio (mm/s)'
    
    def _metric_to_limits(self, m:str, dynamic_parameters = False):
        """
            Function that takes the metric 'm'
            and returns the limits corresponding to that metric
            
        """        
        # TODO: Lower and Upper limits are 5 std deviations away from the mean
        if(dynamic_parameters):
            limits = {'NJS':(0,6), 
                  'Score':(0,25),
                  'CompletedTime':(0, 65), 
                  'Avg.Speed':(0,60)}
        
        else:
            limits = {'NJS':(0,10), 
                  'Score':(0,30),
                  'CompletedTime':(0, 60*1.2), 
                  'Avg.Speed':(0,100*1.2)}
        
        return limits[m]
    
    def _metric_to_max_possible_value(self, m, t):
        
        max_score = {'c0':8, 'c1':16, 'c2':24,
                     'c3':7, 'c4':13, 'c5':19,
                     'c6':5, 'c7':13, 'c8':25}

        if m == 'CompletedTime':
            return 60
        elif m == 'Score':
            return max_score[t]

    # ------------ SET 3: Generate Dynamic Parameters ------------------
    def generate_effect_dynamic_parameters(self, g:str, m:str):
        """
            Generates a graph for group 'g' of metric 'm' as function
            of board size (t) and figure type(f).

            The plot has as horizontal axis three categories corresponding
            to the figure type, and in the vertical axis, the values of the metric 'm'.
            As a label, it has 3 labels, one for each board size(3x3, 5x5, 7x7).

            Plots the avg metric 'm' of all users
            that belong to group 'g' and saves
            it on a image file.

        Args:
            m: Metric of interest from [Puntaje, Suavidad, Tiempo]
            g: Group of interest from [AJS, AMS, AMDC]

        Returns:
            Nothing. It saves the image

        """

        # Check if group and metric exists
        if(not (g in self.groups_ids)):
            print(f'Error el grupo {g} no existe.')
            return 
        
        if not(m in self.metrics_ids):
            print(f'Error la métrica {m} no existe.')
            return 
        
        # Continue if there is not any error.

        fig, axes = plt.subplots()
        fig.set_size_inches(5,4)
        
        # Read the value metric of the group 'g' of metric 'm' -> CHECK HOW TO CORRECTLY
        # COMPUTE IT

        #Check if group file exists
        file_path = f'{g}-AllExperimentResults.csv'
        
        if(not(os.path.exists(file_path))):
            self.generate_all_experiment_results(all_data_set=False, by_groups=True)

        metric_data_frame = pd.read_csv(file_path, index_col=1)

               
        # Filtered the data to get info of group g and metric g
        avg_metrics_for_fixed_figure = []

        all_avg_metrics = []

        #Variables for store max score
        max_value_metric_by_group = 0


        for size in self.sizes:
            for figure in self.figures:
                board_id = self._get_board_id(figure, size)

                filtered_data_frame = metric_data_frame.loc[board_id]

                avg_metric = filtered_data_frame[m].mean()

                avg_metrics_for_fixed_figure.append(avg_metric)

                all_avg_metrics.append(avg_metric)

            #Plot
            axes.plot(self.figures,avg_metrics_for_fixed_figure, label = size)
            
            #Clear the list
            avg_metrics_for_fixed_figure = []

            axes.legend()

        #Get the maximum value of the 'm' for all the figures of the group 'g'
        max_value_metric_by_group = 1.2*max(all_avg_metrics)

        metric_label = self._metric_to_unit(m)
           
        #Put information to the axes
        axes.set_ylabel(f'{metric_label}')

        min_ylim, max_ylim = self._metric_to_limits(m, dynamic_parameters=True)

        axes.set_ylim(min_ylim, max_ylim)

        #Set a title
        axes.set_title(f'{g}')

        # Check if there is a folder to save the figure
        folder_name = 'EffectDynamicParameters'
        if (not(os.path.exists(folder_name))):
            os.mkdir(folder_name)

        #Save the figure
        fig.savefig(os.path.join(f'{folder_name}', f'{m}-{g}.{self.extension}'))


    # ------------ SET 4: Generate Board Collisions ------------------
    def generate_collision_graph(self, t:str):
        """
        Generates 1 bart plot with errors for board 't' for each of the 
        groups that finished the experiments.
        
        """

        if not(t in self.boards):
            print(f'Error. El tablero {t} no existe')
            return

        #Create the figure and axes where the graph will be plotted
        figure, axs = plt.subplots()
        
        figure.set_size_inches(5,4)

        #Get the number of collisions for each group of board 't'
        collisions_groups = self._generate_collisions_statistics(t)


        collision_by_ball_type = {
            'Verde': [[collision_information['Verde'] for group, collision_information in collisions_groups.items()], 'tab:green'],
            'Roja': [[collision_information['Roja']    for group, collision_information in collisions_groups.items()], 'tab:red']
        }

        x = np.arange(len(self.groups_ids))
        width = 0.25
        multiplier = 0
        
        # Assume that I have the average, the min and the max values.
        # key is the "label for the ball" and "value" is the avg collision of the group
        for ball_color, information in collision_by_ball_type.items():
            
            collisions_by_group = information[0]

            # Get the color 
            color_ball = information[1]

            # The order is AJS, AMS and AMD
            collision_avg_by_group = np.array([round(collisions_by_group[0][0]), 
                                      round(collisions_by_group[1][0]), 
                                      round(collisions_by_group[2][0])]) 

            std_by_group = np.array([collisions_by_group[0][1], 
                                     collisions_by_group[1][1], 
                                     collisions_by_group[2][1]]) 

            offset = width * multiplier

            rects = axs.bar(x + offset, collision_avg_by_group, width, label=ball_color, color = color_ball)

            multiplier += 1
            
            # Plot error bars on the axis
            lower_error  = std_by_group
            upper_error = std_by_group

            y_errors = [lower_error, upper_error]
            axs.errorbar(x + offset, collision_avg_by_group, yerr= y_errors, 
                         capsize= 6, fmt='ok',  linewidth=2, ecolor='black',
                         mfc='orange',mec='black')
            

            # Move labels to the right because when adding error plots the line hides the number
            for bar in rects:
                height = bar.get_height()

                x_text = bar.get_x() + 0.5*bar.get_width()
                y_text = bar.get_height()

                axs.text(x_text + 0.05, y_text + 0.5, f'{height}',fontsize = 14)

        # Add some text for labels, title and custom x-axis tick labels, etc.
        axs.set_ylabel('Colisiones', fontsize = 14)

        axs.set_title(f'Tablero {t}',fontsize=14)
        axs.set_xticks(x + width, self.groups_ids)
        axs.legend(loc='upper right', ncols=3, fontsize=11)

        
        max_green_balls = 30
        axs.set_ylim(0, max_green_balls)

        folder_name = "BarCharts"
        file_name = "Collisions"

        if (not(os.path.exists(folder_name))):
            os.mkdir(folder_name)
        
        #Save the figure
        figure.savefig(os.path.join(folder_name, f"{file_name}{t}.{self.extension}"))

        plt.close()

    # ------------- HELPER FUNCTIONS --------------------------- 

    def user_exists(self, name:str):
        """
        Checks if a user with a name "name" is part of the database.
        """

        if name in self.patients:
            return True

        return False
    
    def group_exists(self, group:str):
        """
        Checks if a group with a name "group" is part of the database
        """

        if group in ["AJS","AMS","AMD"]:
            return True
        return False
    
    def board_exists(self, board:str):
        """
        Checks if the board with id "board" was played by the user

        """
        ################# TO DO ####################
        pass


    def _asign_patient(self, patient:Patient):
        if patient.group == "AJS":
            self.group_ajs.append(patient)

        elif patient.group == "AMS":
            self.group_ams.append(patient)

        elif patient.group == "AMD":
            self.group_amd.append(patient)

        else:
            return 

        # Add to the dictionary 
        self.patients[patient.name] = patient

    def _preprocess_information(self, path_to_board:str) -> np.array:
    
        """Preprocess the trajectory followed by the user

        This functions preprocess the information from the .csv
        
        Args:
            path_to_board : Folder where .csv file of board to be analyzed is located

        Returns:
            position_plot: Array of the extracted position from the .csv file.

        
        """

        #Open the file
        file_end_effector_position = open(path_to_board, 'r')

        #Read first line(header line)
        file_end_effector_position.readline()
        time_passed = []
        position_end_effector = []

        #Save .csv on a python variables
        for line in file_end_effector_position:
            
            #Append, add position and update time
            sample, t, px, py, pz, hasCollision = line.split(",")
            time_passed.append(t)
            positions = np.array([np.float64(px), np.float64(py), np.float64(pz)])
            position_end_effector.append(positions)
        
        #Convert to "np.array" the "list" of elements
        position_plot = np.array(position_end_effector)

        file_end_effector_position.close()

        return position_plot

    def _plot_information(
        self,
        position_plot: np.array, 
        patient_name:str,
        id: str,
        *,
        save_graph = False,
        show_name = False
    ) -> None:
        
        """Plot the trajectory followed by the user

        This functions saves an image of the trajectory 
        that is stored on a directory as a .csv file.
        
        Args:
            position_plot : Position information(x, y, z) of the user as a np.array
    
        Returns:
            Nothing, just saves the image 
            of the file

        """
        #Create the figure to plot the graph
        fig = plt.figure(figsize=(4,3), dpi=300)
        
        axes = fig.add_subplot(projection = '3d')

        #Plot the graph
        x = position_plot[:, 0]
        y = position_plot[:, 1]
        z = position_plot[:, 2]

        #Plot to coincide with the unity coordinate system
        axes.plot(x, z, y)
        if show_name:
            axes.set_title(f"Trayectoria de {patient_name} tablero {id}")
        else:
            axes.set_title(f"Trayectoria de {self.patients[patient_name].group} tablero {id}")

        #Set the legends to the axis
        axes.set_xlabel("X (mm)")
        axes.set_ylabel("Z (mm)")
        axes.set_zlabel("Y (mm)")
        axes.set_proj_type('persp', focal_length =1)

        #Plot the initial and final point
        axes.plot(position_plot[0,0], position_plot[0,2], position_plot[0,1], 'gx')
        axes.plot(position_plot[-1,0], position_plot[-1,2], position_plot[-1,1], 'rx')
        #axes.legend(["Trayectoria recorrida", "Posición Inicial", "Posición Final"])
    
        patient = self.patients[patient_name]
        patient_name_splitted = patient_name.split(" ")

        if len(patient_name_splitted) > 1:
            if show_name:
                figure_name = f"{patient.group}EndEffectorPosition{patient_name_splitted[0]+patient_name_splitted[1][:3]}{id}"
            else:
                figure_name = f"{patient.group}EndEffectorPosition{id}"

        else:
            if show_name:
                figure_name = f"{patient.group}EndEffectorPosition{patient_name_splitted}{id}"
            else:
                figure_name = f"{patient.group}EndEffectorPosition{id}"

        if save_graph:
            save_directory = os.path.join(os.getcwd(), "Position Figures")
            
            if(not(pathlib.Path(save_directory).exists())):
                os.mkdir(save_directory)

            fig.savefig(os.path.join(save_directory, f"{figure_name}.{self.extension}"), bbox_inches='tight', pad_inches=0.3)
            
        else:
            fig.show()
        
        #Close the figure that was created by the plt interface
        plt.close()

    def _load_collision_information_all_boards(self, user_path:str, patient:Patient):
        user_collisions_path = os.path.join(user_path, "Collisions")

        green_balls = 0 
        red_balls = 0
        
        # Compute the metrics for all the boards
        for board_id in self.boards:
            green_balls = 0
            red_balls = 0

            collision_file = open(os.path.join(user_collisions_path, f'Board{board_id}Trial1.csv'))

            collision_file.readline()

            for line in collision_file.readlines():

                splitted_line = line.split(",")
                
                if splitted_line[-1] == "Green\n":
                    green_balls+=1
                
                elif splitted_line[-1] == "Red\n":
                    red_balls+=1

            # Set user collisions for board "board_id"
            patient.collisions[board_id] = (green_balls, red_balls)

            collision_file.close()

    def _generate_collisions_statistics(self, t:str):
        """
            Evaluates the collision of user of all groups for the board 't'.      
        """

        collisions = {}
        green_collisions = []
        red_collisions = []
        
        letters_to_object_group = {"AJS":self.group_ajs, "AMS":self.group_ams, "AMD":self.group_amd}

        for g in self.groups_ids:  
            green_collisions = []
            red_collisions = []  
            for patient in letters_to_object_group[g]:

                collision_pair = patient.collisions[t]

                green_collisions.append(collision_pair[0])
                red_collisions.append(collision_pair[1])
                
                green_collisions_np =np.array(green_collisions)
                red_collisions_np = np.array(red_collisions)

            group_collisions = {"Verde": [np.average(green_collisions_np), np.std(green_collisions_np)], 
                                "Roja": [np.average(red_collisions_np), np.std(red_collisions_np)]}
            
            collisions[g] = group_collisions


        return collisions

    def _get_path_to_board(self, patient_name:str, board_id:str):
        user_path = os.path.join(self.path_database, patient_name, 'Positions')
        board_to_load = f'Board{board_id}Trial1.csv'

        path_to_board = os.path.join(user_path, board_to_load)

        return path_to_board

    def _plot_on_axes(self, axes:plt.Axes, position_plot: np.array):
         #Plot the graph
        x = position_plot[:, 0]
        y = position_plot[:, 1]
        z = position_plot[:, 2]

        #Plot to coincide with the unity coordinate system
        axes.plot(x, z, y)

        #Set the legends to the axis
        axes.set_xlabel("X (mm)")
        axes.set_ylabel("Z (mm)")
        axes.set_zlabel("Y (mm)")
        axes.set_proj_type('persp', focal_length =1)
        
    def _get_board_id(self, figure: str, size:str):

        """
            Function to get the board id of the form 
            ci given 'size' and 'figure'
        
        """
        if figure == 'Cuadrado':
            if size == '3x3':
                return 'c0'
            elif size == '5x5':
                return 'c1'
            elif size == '7x7':
                return 'c2'
        
        elif figure == 'Letra Z':
            if size == '3x3':
                return 'c3'
            elif size == '5x5':
                return 'c4'
            elif size == '7x7':
                return 'c5'
            
        elif figure == 'Ajedrez':
            if size == '3x3':
                return 'c6'
            elif size == '5x5':
                return 'c7'
            elif size == '7x7':
                return 'c8'


    # ------------ SET 5: Generate Board Collisions ------------------
    def generate_avg_metrics_all_boards(self, m:str)-> None:
        """Generates a bar plot of the average metric 'm' for all the boards.

        Args:
          m: Metric to compute the average.

        Returns:
          Nothing. It will save the image as a self.extension file.

        Raises:
          Nothing
        """ 

        group_metrics = []

        for g in self.groups_ids:
            group_metric = self._get_avg_metric_all_boards(m, g)
            group_metrics.append(group_metric)

        max_metric = max(group_metrics)

        fig, ax = plt.subplots(figsize = (6,4.5), dpi=300)

        bar_labels = ['AJS', 'AMS', 'AMD']
        bar_colors = ['tab:blue', 'tab:orange', 'tab:green']

        ax.bar(self.groups_ids, group_metrics, color=bar_colors)

        y_label = self._metric_to_unit(m)

        ax.set_ylabel(y_label)
        ax.set_title(f'Valor promedio de {y_label}')

        ax.set_ylim(0, max_metric * 1.2)


        folder_path = 'AverageMetrics'
        if (not(os.path.exists(folder_path))):
            os.mkdir(os.path.join(os.getcwd(), folder_path))
        
        file_name = f'AverageMetric-AllBoards-{m}.{self.extension}'
        graph_path = os.path.join(folder_path, file_name)


        fig.savefig(graph_path)


            
    def _get_avg_metric_all_boards(self, m:str, g:str) -> float:
        """Compute the average metric 'm' of all boards for the group 'g'.
        
        Args:
          m: Metric to compute the average
          g: Group of interest
    
        Returns:
          avg_metric: The average metric
        
        Raises:
          Nothing
        """

        file_path = f'{g}-AllExperimentResults.csv'

        file = pd.read_csv(file_path)

        metric_column = file[m]

        avg_metric = metric_column.mean()

        return avg_metric
