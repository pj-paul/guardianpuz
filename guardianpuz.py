# -*- coding: utf-8 -*-

# Code in Python 3
import puz
import requests 
import numpy as np
from bs4 import BeautifulSoup
import sys
import argparse
import json

parser = argparse.ArgumentParser()
parser.add_argument('-t', '--type')
parser.add_argument('number')

# Parse script arguments to extract crossword type and number 
args = parser.parse_args()
crossword_number = args.number
if args.type is None:
    crossword_type = 'cryptic'
else:
    crossword_type = args.type
crossword_url = "https://www.theguardian.com/crosswords/" + crossword_type + "/" + crossword_number

# Extract and load the json crossword data provided by Gurdian. 
res = requests.get(crossword_url)
soup = BeautifulSoup(res.text)
d = soup.findAll('div', {'class':'js-crossword'})[0]['data-crossword-data']
json_data = json.loads(d)


# Initialize a puz object. Fill in some metadata on the puzzle
p = puz.Puzzle()
p.height = 15
p.width = 15
p.title = "Guardian " + crossword_type.title() + json_data['name']
p.author = json_data['name']



class Clue:
    def __init__(self, number, direction, text):
        self.number = number
        self.direction = direction
        self.text = text.encode('iso-8859-1', 'ignore') #puzpy doesn't do unicode, even though it's 2019

    def __lt__(self, other):
        if self.number == other.number:
            if self.direction == 'D':
                return False
            else:
                return True
        else:
            return self.number < other.number

# Helper function to create the crossword blank position list 

def fill_blanks(blank_matrix, position_vector, clue_direction, clue_length):

	'''
	Function to identify the blank elements of a 15 * 15 crossword grid. 
	Takes in four arguments:
	1. blank_matrix: A 15*15 numpy matrix to indicate blank values
	2. position_vector: The starting position from which a clue is being filled. Should be of the form [x,y] where x and y are integers
	3. clue_direction: Down or Across
	4. clue_length: How many cells of the matrix does the answer to the clue fill. 
	'''

	def check_position_vector(position_vector):
		pass # To be implemented

	if clue_direction == "A":
		begin_index = position_vector['x']
		end_index = position_vector['x'] + clue_length
		row_index = position_vector['y']
		blank_matrix[row_index,begin_index:end_index] = 1
	else:
		begin_index = position_vector['y']
		end_index = position_vector['y'] + clue_length
		col_index = position_vector['x']
		blank_matrix[begin_index:end_index, col_index] = 1
		
	

clues = []
blank_matrix = np.zeros([15,15],dtype=int)

for clue in json_data['entries']:
	clue_number = clue['number']
	clue_direction = "D" if clue['direction'] == "down" else "A"
	clue_length = clue['length']
	clue_text = clue['clue']
	clues.append(Clue(clue_number, clue_direction, clue_text))

	# Edit the blanks matrix 
	position_vector = clue['position']
	#print(clue['position'],clue_direction, clue_length)
	fill_blanks(blank_matrix, position_vector,clue_direction, clue_length )
	#print(blank_matrix)

blank_matrix = blank_matrix.flatten().tolist()
blank_matrix = list(map(str, blank_matrix))
fill = [cell.replace('1', '-').replace('0', '.') for cell in blank_matrix] 
#print(fill)

fill = ''.join(fill)
#print(fill)
sorted_clue_texts = list(map(lambda c: c.text, sorted(clues)))
#print(sorted_clue_texts)

p.fill = fill
p.clues = sorted_clue_texts

p.solution = fill.replace("-", "A")

p.save('output.puz')
