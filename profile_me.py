import pandas as pd
import os
import io
import re
import cProfile
import pstats
from matplotlib import pyplot as plt




def profile_wrapper(instance):
	profiler = cProfile.Profile()
	profiler.enable()

	try:
		gf = instance()
	except Exception as e:
		raise e
	finally:
		profiler.disable()
		p_output = io.StringIO()
		prof_stats = pstats.Stats(profiler, stream = p_output).print_stats()
		# prof_stats.sort_stats('cumulative').print_stats(10)
		p_output = p_output.getvalue()
		p_output = 'ncalls'+p_output.split('ncalls')[-1]
		result = '\n'.join([','.join(line.rstrip().split(None,5)) for line in p_output.split('\n')])
		with open('g_profile_stats.csv', 'w') as f:
			print(result, file = f)
		show_results()

def clean(string):
	#lst.replace(':', ' ')
	string = string.strip(" '(){}\n'")
	lst = re.split('[,: ()]', string)
	a = ''
	for num in range(len(lst)):
		if lst[num] == 'of':
			a = f'{lst[num-1]} of {lst[num+1]}'
			break
	return a if a else lst[-1]
	
def show_results():
	df = pd.read_csv('g_profile_stats.csv')
	col_dict = {'ncalls': 'calls_num', 'tottime':'total_time', 'percall':'time_per_call',
			'cumtime':'cumulative_time', 'percall.1':'percall.1',
			'filename:lineno(function)':'name'}
	
	df = df.rename(columns = col_dict)
	df.name = df.name.apply(clean)
	cols = ('name', 'total_time', 'cumulative_time', 'time_per_call')
	nums = (0, 0.1, 0.5, 0.01)  #limit numbers to sort for columns

	for x in range(1,4):
		plt.subplot(2,2,x)
		plt.text(0,0, cols[x], horizontalalignment='center',verticalalignment='center')
		plt.suptitle(cols[x])
		p = get_subdata(df, cols[x], nums[x])
		ipie = plt.pie(p[cols[x]], labels = p['name'], autopct=make_autopct(p[cols[x]]), shadow=True, explode = p['explode'])
	plt.suptitle('Profiling')
	mng = plt.get_current_fig_manager().window.state('zoomed')
	plt.show()

def make_autopct(values):
	def my_autopct(pct):
		total = sum(values)
		val = round(pct*total/100.0,3)
		return f'{round(pct,2)}%\n{val}'#.format(p=pct,v=val)
	return my_autopct

def get_subdata(df, colname, num):
	tot_more_than = df[colname] > num
	df1 =df[tot_more_than]
	df1.sort_values(by=[colname], inplace=True)
	df1['explode'] = df1[colname].apply(lambda x: num/x) 
	
	return df1[:10] #(df1[colname], df1.name)



if __name__ == '__main__':
	show_results()