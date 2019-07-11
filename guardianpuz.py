# -*- coding: utf-8 -*-

# Code in Python3

import puz
import re
import requests 
import numpy as np
from bs4 import BeautifulSoup
import sys
import argparse
import json

import helpers # Import functions in the file helpers.py

parser = argparse.ArgumentParser()
parser.add_argument('-t', '--type')
parser.add_argument('-n','--number')

# Parse script arguments to extract crossword type and number. Generate url of target crossword. 
args = parser.parse_args()

# Set crossword type
if args.type is None:
    crossword_type = 'cryptic'
    print("Crossword type not provided. Fetching Cryptic crossword of specified number.")
else:
    crossword_type = args.type

# Set crossword number
if args.number is None:
	crossword_number = helpers.get_latest_number(crossword_type)
	print("Crossword number not provided. Fetching latest %s crossword # %s." %(crossword_type, crossword_number))
else:
    crossword_number = args.number

crossword_url = "https://www.theguardian.com/crosswords/" + crossword_type + "/" + crossword_number

# Extract and load the json crossword data provided by Guardian. 
res = requests.get(crossword_url)
soup = BeautifulSoup(res.text, features="lxml")
d = soup.findAll('div', {'class':'js-crossword'})[0]['data-crossword-data']
json_data = json.loads(d)


# Initialize a puz object. Fill in some metadata on the puzzle
p = puz.Puzzle()
p.height = 15
p.width = 15
p.title = "Guardian " + crossword_type.title() + json_data['name']
p.author = json_data['name']


# Create a 'Clue' class to hold some attributes for each clue. 
class Clue:
    def __init__(self, number, direction, text):
        self.number = number
        self.direction = direction
        self.text = text # Removing the encoding as per Peter's suggestion

    def __lt__(self, other):
        if self.number == other.number:
            if self.direction == 'D':
                return False
            else:
                return True
        else:
            return self.number < other.number

clues = []
solution_matrix = np.array(['.']*225, dtype=object).reshape([15,15]) # Create a 15*15 grid populated with '.'s.

for clue in json_data['entries']:

	# Generate parameters for 'Clue' class instances and fill_grid function calls. 
	clue_number = clue['number']
	clue_direction = "D" if clue['direction'] == "down" else "A"
	clue_length = clue['length']
	clue_text = clue['clue']
	position_vector = clue['position']
	clue_solution = clue['solution']

	# Pass on the clues to separate class instances
	clues.append(Clue(clue_number, clue_direction, clue_text))

	# Invoke fill_grid function with earlier generated parameters
	helpers.fill_grid(solution_matrix, position_vector,clue_direction, clue_length, clue_solution)

# Generate the solution string, and the blanks-fill string to pass through to puz
solution_matrix = solution_matrix.flatten().tolist() # Flatten the solution matrix into a single row, and then covert into a list. 
solution_string = ''.join(solution_matrix) # Turn the solution_matrix list into one single string. 
										# This string will have filled in solutions + period for blanks. 
fill_string = re.sub(r'[A-Za-z]','-',solution_string)  #Substitute alphabets with - (hyphen), and leave the periods alone. 

sorted_clue_texts = list(map(lambda c: c.text, sorted(clues)))

## Pass the blanks and clues to puz and save the puzzle file. 
p.fill = fill_string
p.clues = sorted_clue_texts
p.solution = solution_string
save_file_name = "Guardian " + json_data['name'] + '.puz'
p.save(save_file_name)
