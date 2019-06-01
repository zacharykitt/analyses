from io import BytesIO

import requests
import numpy as np
import pandas as pd
from tabulate import tabulate

def calc_prob(m, n):
	return ((np.e**(-1*m)) * (m**n)) / (np.math.factorial(n))

def yates_corrected_chi_square(exp, obs, thresh):
	print('Running Yate\'s corrected chi-squared test...')
	sum = 0
	for i, o in enumerate(obs):
		sum += ((abs((o - exp[i])) - .5)**2/exp[i])
	if sum < thresh:
		print('{:.2f}: Fail to reject null hypothesis.'.format(sum))
	else:
		print('{:.2f}: Reject the null hypothesis.'.format(sum))
	return sum

DATA_SRC = 'https://www.prio.org/Global/upload/CSCW/Data/UCDP/2009/Main%20Conflict%20Table.xls'

# download dataset and feed into pandas
res = requests.get(DATA_SRC)
raw_data = pd.read_excel(BytesIO(res.content))

# ignore observations that don't reflect interstate conflict
subset = raw_data[raw_data.Type == 2]

# merge observations for the same conflict
grouped = subset.groupby('ID')

# build a dataframe of the number of interstate conflicts per year
# also remove any years that Richardson would have looked at
years = range(1952, 2010)
yearly_counts = {i: 0 for i in years}
for n, group in grouped:
	year = group['StartDate'].iloc[0].year
	if year > 1951:
		yearly_counts[year] += 1
yearly_counts = pd.DataFrame.from_dict(yearly_counts, 'index')

# build a frequency table from yearly counts
o_cnts = pd.crosstab(index=yearly_counts[0], columns='cnt')
o_pcts = pd.crosstab(index=yearly_counts[0], columns='pct', normalize='columns')


# calculate expected frequencies for poisson distribution with same mean
mean = yearly_counts.mean().iloc[0]
p_pcts= [calc_prob(mean, i) for i in o_cnts.index]
p_cnts= [p_pcts[i] * len(years)  for i in o_cnts.index]

df = pd.DataFrame({'cnt_o': o_cnts['cnt'], 'cnt_p': p_cnts, 'pct_o': o_pcts['pct'], 'pct_p': p_pcts})

print(tabulate(df, headers=['', 'count (observed)', 'count (expected)', 'freq. (observed)', 'freq. (expected)'], floatfmt=".2f"))

# bonus chi-squared test (with Yate's correction)
yates_corrected_chi_square(p_cnts, o_cnts['cnt'], .5991) # for 2 degrees of freedom at 95% confidence
