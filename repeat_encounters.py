'''
This script simulates how many repeat encounters with strangers
will be experienced by someone living in the same place for a
given number of years.
'''

from collections import Counter
from random import choices, sample

RESIDENTS = 50000
MOVE_RATE = 1/9
PASSERBYS = 15  # number seen per day
TRIALS = 100  # number of simulations to run
YEARS = 9

class Region:
	''' Define the parameters of a hypothetical place

	PARAMS
	  residents <int>: number of residents in this region
	  passerbys <int>: number of people passed each day
	'''
	def __init__(self, residents, passerbys):
		self.size = residents
		self.population = list(range(0, residents))
		self.passerbys = passerbys
		self.n_movers = round(MOVE_RATE * residents)
		self.former_residents = []
		self._moves = 1

	def simulate_moves(self):
		''' approximates yearly churn of residents '''
		ceiling = self.size * self._moves
		movers = set(sample(self.population, k=self.n_movers))  # set=speed
		self.former_residents.extend(movers)
		self.population = [x for x in self.population if x not in movers]
		new_residents = list(range(ceiling, ceiling + self.n_movers))
		self.population.extend(new_residents)
		self._moves += 1
		

results = []
for t in range(0, TRIALS):
	print('running trial: ' + str(t+1))
	l = Region(RESIDENTS, PASSERBYS)
	faces_passed = Counter()  # a record of all faces seen
	for year in range(0, YEARS):
		for day in range(0, 365):
			todays_faces = choices(l.population, k=l.passerbys)
			for face in todays_faces:
				faces_passed[face] += 1  # record sighting
		l.simulate_moves()
	matches = [k for k, v in faces_passed.items() if v > 1]
	results.append(len(matches))  # count of faces seen more than once

avg = sum(results)/len(results)  # the average of all trials
print(avg)
