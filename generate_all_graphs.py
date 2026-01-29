# Python file that contains all the functions 
# needed to generate the graph of the data

# There are going to be 4 different types of graphs to be generated
# with subcategories

import os 
import sys

from UserDataBase import UserDataBase

# ---------------- HELPER FUNCTIONS ---------------- 

# SET I. POSITION GRAPH
def generate_positions(data_base:UserDataBase, patient_names = []):
    print('CONJUNTO 1: GENERANDO LAS GRÁFICAS DE POSICIÓN\n')

    boards_id = 'c0 c1 c2 c3 c4 c5 c6 c7 c8'.split(" ")

    # ------------- If user does not provide patient_names, graph positions will be 
    # random generated
    if(len(patient_names) == 0):
        # a) Generate the 9 graph positions of the random patient of group AJS
        patient_ajs_name = data_base.generate_positions_group("AJS", boards_id)

        # b) Generate the 9 graph positions of the random patient of group AMS
        patient_ams_name = data_base.generate_positions_group("AMS", boards_id)

        # c) Generate the 9 graph positions of the random patient of group AMD
        patient_amd_name = data_base.generate_positions_group("AMD", boards_id)

        patient_list = [patient_ajs_name, patient_ams_name,patient_amd_name]

    # ---------------- Else, use the list of patients_names that is on the arguments.
    else:
        for patient in patient_list:
            data_base.generate_positions_patient(patient, boards_id)
    
    # d) Take each patient of of "patient_list" and compare 
    # its 3D position on one graph
    #print(f"Generando gráficas de los pacientes {patient_list}.")

    data_base.generate_comparing_positions_name(patient_list, boards_id)

# SET II. METRICS DESCRIPTION
def generate_metrics(data_base:UserDataBase):
    print('CONJUNTO 2: GENERANDO LAS GRÁFICAS DE LAS MÉTRICAS\n')

    boards_id = 'c0 c1 c2 c3 c4 c5 c6 c7 c8'.split(" ")
    metrics = 'Score NJS CompletedTime Avg.Speed'.split(" ")


    for b in boards_id:
        for m in metrics:
           #print(f'Generando tablero {b} de métrica {m}')
            data_base.generate_metric_graph(m,b)

# SET III. EFFECT OF DYNAMIC PARAMETERS
def generate_dynamic_parameters(data_base:UserDataBase):
    print('CONJUNTO 3: GENERANDO LAS GRÁFICAS DE LOS PARÁMETROS DINÁMICOS\n')

    groups_id = 'AJS AMS AMD'.split(" ")
    metrics = 'Score NJS CompletedTime Avg.Speed'.split(" ")

    for m in metrics:
        for g in groups_id:
            #print(f'Generando métrica {m} de grupo {g}')
            data_base.generate_effect_dynamic_parameters(g, m)

# SET IV. AVERAGE COLLISION PER BOARD
def generate_board_collisions(data_base:UserDataBase):
    print('CONJUNTO 4: GENERANDO LAS GRÁFICAS DE LAS COLISIONES DE LA TRAYECTORIA\n')

    boards_id = 'c0 c1 c2 c3 c4 c5 c6 c7 c8'.split(" ")

    for board in boards_id:
        data_base.generate_collision_graph(board)

# SET V. AVERAGE METRICS OF ALL BOARDS
def generate_avg_metrics_all_boards(data_base:UserDataBase):
    print('CONJUNTO 5: GENERANDO LAS GRÁFICAS DE LAS MÉTRICAS PROMEDIO DE LA TRAYECTORIA\n')

    metrics = 'Score NJS CompletedTime Avg.Speed'.split(" ")

    for m in metrics:
        data_base.generate_avg_metrics_all_boards(m)

# ---------------- MAIN PROGRAM ---------------- 

# 1. Initiliaze the database
data_folder = "Data"
DATASET_DIRECTORY = os.path.join(os.getcwd(), data_folder)
my_data_base = UserDataBase(DATASET_DIRECTORY)

# 2. Load the data of the data base
my_data_base.load_data()

extension_file = sys.argv[1]
# 3.- Set the extension for the image file
my_data_base.set_extension_file(extension_file)

# 2. Run all the functions to generate all the graphs
#functions_to_generate = [generate_positions, generate_metrics, generate_dynamic_parameters, generate_board_collisions, gene]

functions_to_generate = [generate_avg_metrics_all_boards]


for i in range(len(functions_to_generate)):
    f = functions_to_generate[i]

    f(my_data_base)
