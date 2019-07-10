# A couple of helper functions used by guardianpuz main function. 

import re
import requests 
from bs4 import BeautifulSoup


# Function to extract the ID of the latest crossword of a particular type (Cryptic, Quick, Genius etc)
def get_latest_number(crossword_type):
	'''
	Function to get the number of the latest Cryptic crossword from the Guardian website.
	Takes in the type of crossword as parameter. 
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

# Helper function to create the crossword blank position list 
def fill_grid(solution_matrix, position_vector, clue_direction, clue_length, clue_solution):

	'''
	Function to fill a 15 * 15 crossword grid. 
	Takes in five arguments:
	1. solution_matrix: A 15*15 numpy character matrix to hold solutions and blank value indicators.
	2. position_vector: The starting position from which a clue is being filled. Should be of the form [x,y] where x and y are integers
	3. clue_direction: Down or Across
	4. clue_length: How many cells of the matrix does the answer to the clue fill. 
	5. clue_solution: Final solution of the clue. 
	'''

	def check_position_vector(position_vector):
		pass # To be implemented

	if clue_direction == "A":
		begin_index = position_vector['x']
		end_index = position_vector['x'] + clue_length
		row_index = position_vector['y']
		solution_matrix[row_index,begin_index:end_index] = list(clue_solution)
	else:
		begin_index = position_vector['y']
		end_index = position_vector['y'] + clue_length
		col_index = position_vector['x']
		solution_matrix[begin_index:end_index, col_index] = list(clue_solution)