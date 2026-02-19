import hashlib
import os
import json
import sys


def rename_file_directories(folder):
	for old_name in os.listdir(folder):
		word = 'Trial1'
		low_index = old_name.find(word)
		upper_index = low_index + len(word)
		
		new_name = old_name[0:low_index] + old_name[upper_index:]

		os.rename(os.path.join(folder, old_name), os.path.join(folder,new_name))		
	

DATA_PATH = sys.argv[1]

os.chdir(DATA_PATH)

if __name__ == "__main__":
	for person in os.listdir():
		# Generate secure name
		print("Generating secure name")
		hasher = hashlib.sha256()
		hasher.update(person.encode())
		secure_name = hasher.hexdigest()

		# Set the secure name to folder 
		print("Changing folder name")
		

		os.rename(person, secure_name)
 
		# Set the secure name to the file
		print("Changing Information.json")
		information_file = open(os.path.join(secure_name, "Information.json"), "r")	
		loaded_json = json.load(information_file)
		information_file.close()

		loaded_json['Name'] = secure_name

		new_information_file = open(os.path.join(secure_name, "Information.json"), "w")	

		json.dump(loaded_json, new_information_file)
		new_information_file.close()

	
		# Delete "Trial1"
		rename_file_directories(os.path.join(secure_name,"Collisions"))
		rename_file_directories(os.path.join(secure_name,"Positions"))
	




