import subprocess
import sys
import re
from seaborn import violinplot
import matplotlib.pyplot as plt
from itertools import repeat
import scipy.stats as stats 
import pandas as pd


"""
This script creates 9 violin plot figures in the specified FIGURES_DIR, each with with 2 violin plots.
Each figure represents an experimental condition, and each of the 2 plots represent either ProACT
or HIV-TRACE.
"""

# Constants
#EXPERIMENTS = ['SAMPLE-FIRSTART_ARTRATE-4']
EXPERIMENTS = ['SAMPLE-FIRSTART_ARTRATE-4','SAMPLE-FIRSTART_ARTRATE-2','SAMPLE-FIRSTART_ARTRATE-1',
'SAMPLE-FIRSTART_STOPRATE-0.25x','SAMPLE-FIRSTART_STOPRATE-0.5x','SAMPLE-FIRSTART_STOPRATE-2x',
'SAMPLE-FIRSTART_STOPRATE-4x','SAMPLE-FIRSTART_EXPDEGREE-20','SAMPLE-FIRSTART_EXPDEGREE-30']

SIMS_DIR = 'simulations/'
FIGURES_DIR = 'figs/'

TRANSMISSIONFMT = ".transmissions.txt.gz"
PROACTFMT = ".time9.ft.mv.proact.txt.gz"
HIVTRACEFMT = ".time9.tn93.hivtrace.growth.ordering.txt.gz"
INTERMEDIATEFILE = "intermediate_file_violinplot.txt"

algorithms = [PROACTFMT, HIVTRACEFMT]
colors = { PROACTFMT : '#161f54', HIVTRACEFMT : '#a16c18'}

# Parameters of choice
START_TIME = 9
METRIC_CHOICE = 3.2


def calculateTauSimulation(transmissionFile: str, experiment: str, intStr: str, algm: str) -> float:
	"""
	Helper method for calculating the Tau value for a certain simulation.

	Parameters
	----------
	transmissionFile - Name of file containing transmission data
	experiment - Name of the experimental condition
	intStr - The specific "number" associated with this simulation
	algm - Current algorithm being evaluated (such as ProACT/HIV-TRACE)
	"""

	# Form the names of required files
	inputFile = SIMS_DIR + experiment + "/" + intStr + algm
	outputFile = open(INTERMEDIATEFILE, 'w')

	# Run compute_efficacy with inputFile and outputFile
	bashCommand = "py compute_efficacy.py -m " + str(METRIC_CHOICE) + " -i " + inputFile + " -t " + transmissionFile + " -s " + str(START_TIME)
	subprocess.call(bashCommand.split(), stdout=outputFile, shell=True)
	outputFile.close()

	efficacy = [[v.strip() for v in l.strip().split('\t')] for l in open(INTERMEDIATEFILE).read().strip().splitlines()]

    # Iterate over all the lines for efficacy
	for i in range(len(efficacy)):
		if len(efficacy[i]) != 2:
			raise ValueError("Input must be efficacy file as generated by ./compute_efficacy (TSV with 2 columns: PERSON<TAB>EFFICACY.", efficacy[i], inputFile, transmissionFile, efficacy)
			return
		efficacy[i] = float(efficacy[i][1]);

	optimalOrder = list(range(len(efficacy), 0, -1))
	tau, pvalue = stats.kendalltau(optimalOrder, efficacy)
	outputFile.close()

	return tau


# Script ====================================================================

# Initializing our dataframe
cols = ['Experiment', 'Tau','Algorithm']
df = pd.DataFrame(columns = cols)


# Iterate through experiments
for experiment in EXPERIMENTS:

	# Iterate over algorithms, PROACT then HIV-TRACE
	for a in algorithms:

		# For plotting the violin for a in this experiment
		x = [] # Denotes which prioritization method was used per Tau-b value
		y = [] # Tau-b values

		# Iterate over all 20 simulations per experiment
		for i in range(1,21):

			# Convert i into a str for the file names
			intStr = ''
			if i < 10:
				intStr = "0" + str(i)
			else:
				intStr = str(i)

			transmissionFile = SIMS_DIR +  experiment + "/" + intStr + TRANSMISSIONFMT

			# Calculate tau for this simulation w/ ProACT
			tau = calculateTauSimulation(transmissionFile, experiment, intStr, a)

			temp = pd.DataFrame([[experiment, tau, a]], columns= cols)
			df = df.append(temp)

		# End algorithm for-loop

	# End experiment for loop


# Make the violin plot for all simulations 
ax = violinplot(x="Experiment", y="Tau", hue="Algorithm", data=df, dodge=False, palette=colors)

# Reformat graph
ax.set_xticklabels(ax.get_xticklabels(), rotation=90, horizontalalignment='right')

# Save the fig automatically
fig = ax.get_figure(); fig.savefig(FIGURES_DIR + 'm' + str(METRIC_CHOICE) + '_tau' + '.png')

# print(df["Tau"])

# Clear current figure window
plt.clf()

#py ./compute_efficacy.py -i simulations/SAMPLE-FIRSTART_ARTRATE-4/01.time9.ft.mv.proact.txt.gz -t simulations/SAMPLE-FIRSTART_ARTRATE-4/01.transmissions.txt.gz -s 9 -m 3.2 -o out.txt