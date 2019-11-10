<<<<<<< HEAD
"""
File implements several methods used in compute_efficiency.py and compute_taub.py
"""


from sys import stderr
=======
#!/usr/bin/env python3
from collections import OrderedDict
>>>>>>> 553db54767aa061cd799dc8c549efda6b131c47e
import scipy
import scipy.stats as stats # run 'pip install scipy' in your terminal


def countInfections(transmissionHist, lowerBound: int, upperBound: int) -> dict:
	"""
	Counts the number of times each individual infected someone else in a file.	
	
	Returns a dictionary where each key is an individual and their value
	is their corresponding infection count.

	Parameters
	----------
	tranmissionHist - the file object with data on tranmissions used to build the 
					  dictionary
	lowerBound - lower bound of years range
	upperBound - upper bound of years range
	"""

	infectedPersons= []
	people = []

	numInfected = dict()

	# Loop over each line in the file.
	for line in transmissionHist.readlines():
	    u,v,t = line.split('\t')
	    u = u.strip()
	    v = v.strip()

	    # Only considers infections within a given range of years
	    if (lowerBound > float(t)) | (float(t) > upperBound):
	    	continue

	    if u == 'None':
	    	continue

	    if u not in numInfected:
	    	numInfected[u] = 0

	    numInfected[u] += 1
	    
	"""
	# Print the output of all individuals, unsorted
	for u in numInfected:
		print("%s\t%d" % (u, numInfected[u]))
	"""

	return numInfected


def matchInfectorCounts(infectionsDict: dict, infile, outfile) -> None:
	"""
	Matches the infectors in a user inputted file to their corresponding
	infection count. Returns void.

	Outputs lines with the format: "<individual> <count>", 
	maintaing the original order of individuals in input.

	Parameters
	----------
	infectionsDict - a dict with keys as infectors and values as
					 their infection counts
	infile - a file with the user's ordering of individuals
	outfile - a file where each line of output is written
	"""

	for line in infile.readlines():

		p = line.strip()

		if p not in infectionsDict.keys():
			print("Individual", line, "is not in the transmission histories file.", stderr)

		else:
			outfile.write("%s\t%d\n" % (p, infectionsDict[p]))


def calculateTauB(infile, outfile, reverse: bool) -> None:
	"""
	Calculates the Kendall Tau B correlation coefficient between user ordering
	and most optimal ordering, assuming that the counts of individuals in 
	infile sorted is the most optimal. 
	Outputs coefficient and pvalue in the following format: "<tau> <pvalue>".
	Returns void.

	Parameters
	----------
	infile- a file containing an ordering of infectors and their counts - 
			generated by the user's algorithm
	outfile - the file the tau and pvalue are outputted
	reverse - bool, true if user's ordering is compared to order sorted descending,
					false if comparing to order sorted ascending
	"""

	userOrder = []

	for line in infile:
		p,count = line.split('\t')
		p = p.strip()
		count = count.strip()
		userOrder.append(int(count))

	optimalOrder = sorted(userOrder, reverse=reverse)
	print(userOrder, "\n")
	print(optimalOrder)

	tau, pvalue = stats.kendalltau(optimalOrder, userOrder)

	outfile.write("%d\t%d\n" % (tau, pvalue))

