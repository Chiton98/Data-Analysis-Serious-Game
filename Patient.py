# Class for storing the user information

class Patient:
    def __init__(self, name:str, age:int, genre:str, group:str, id = 0):
        self.name = name
        self.age = age
        self.genre = genre 
        self.group = group

        self.id = id

        # Experiment results of the patient
        
        self.collisions = {}

        #Compute the initials
        #splitted_name = name.split(" ")
        #self.initials = splitted_name[0][0] + splitted_name[1][0]

    def get_collision_information(self,t):
        return self.collisions[t]
    
