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

# Function to extract latest crossword numbers
def get_latest_number():
	'''
	Function to get the number of the latest Cryptic crossword from the Guardian website.
	'''
	crossword_url = 'https://www.theguardian.com/crosswords/series/' + crossword_type 
	re_string = '.*\/crosswords\/' + crossword_type + '\/[0-9]+'

	res = requests.get(crossword_url)
	soup = BeautifulSoup(res.text, features="lxml")
	latest_url = soup.find_all(href = re.compile(re_string))[0]['href']

	number_search = re.search('.*\/([0-9]+)', latest_url)
	if number_search:
   	 latest_number = number_search.group(1)
   	 
	return latest_number

# Set crossword number
if args.number is None:
	crossword_number = get_latest_number()
	print("Crossword number not provided. Fetching latest Cryptic crossword.")
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

blank_matrix = blank_matrix.flatten().tolist() # Flatten the blank matrix into a single row, and then covert into a list. 
blank_matrix = list(map(str, blank_matrix)) # Convert the blank matrix list of integers into strings.
fill = [cell.replace('1', '-').replace('0', '.') for cell in blank_matrix]  # Replace '1' with -, and '0' with . to pass onto puz. 
fill = ''.join(fill) #Convert the list of "-" and "." into a single string. This is what puz accepts as input. 

sorted_clue_texts = list(map(lambda c: c.text, sorted(clues)))

## Pass the blanks and clues to puz and save the puzzle file. 
p.fill = fill
p.clues = sorted_clue_texts
p.solution = fill.replace("-", "A")
p.save('output.puz')
