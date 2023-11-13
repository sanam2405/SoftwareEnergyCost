from pstats import Stats
from io import StringIO
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

# Printing stats to a string
result=StringIO()
stats = Stats("cprofile_train.prof",stream=result)
stats.strip_dirs()
stats.sort_stats('cumulative')
stats.print_stats()

result=result.getvalue()

# Chopping the string into a csv-like buffer
result='ncalls'+result.split('ncalls')[-1]
result='\n'.join([', '.join(line.rstrip().split(None,6)) for line in result.split('\n')])
print(result)

# Saving it to the local disk
f=open('cprofile_train.csv','w')
f.write(result)
f.close()

# Using 3 decimal places in output display
pd.set_option("display.precision", 4)

# Preventing wrapping repr(DataFrame) across additional lines
pd.set_option("display.expand_frame_repr", False)

# Setting max rows displayed in output to 25
pd.set_option("display.max_rows", 100)

df = pd.read_csv('cprofile_train.csv',skipinitialspace=True)
# Displaying Column names
df.columns
# Renaming pandas col
df.rename(columns={'percall.1':'module_name'},inplace=True)
df = df.drop(['filename:lineno(function)'],axis=1)
df=df[:-1] # Deleting last row as part of data cleaning
df['total_num_calls']=""
df['total_num_calls']=df.index # Resetting index
df[['total_num_calls', 'num_recursion']] = df['total_num_calls'].str.split("/", n=1, expand=True)
# Changing the data type
convert_dict = {'module_name': str, 
                'total_num_calls': int,
                'tottime':float   ,
                'cumtime':float,
                'ncalls' :float,
                'percall':float                
                               } 
df = df.astype(convert_dict)

# Deriving column total time = Time taken per call * Total num of calls
df['total_time']=df['percall'] * df['total_num_calls']
df['total_time']=df['total_time'].apply(np.ceil)
# Converting to seconds
df['total_time'] = df['total_time'] / 1000.0 

# Create extra copy for safety 
df1=df
# Extracting only module name
df1['module_name']= df['module_name'].str.extract('(\\w+.py)')
# Dropping if any NaN exist
df1=df1.dropna(subset=['module_name'])
# Removing extra White Space
df1['module_name']=df1['module_name'].str.strip()
df2=df1
# Adding same modules' total time
df2 = df1.groupby(["module_name"])["total_time"].sum()

df2 = pd.DataFrame(df2)
df2=df2.reset_index()
df2 = df2[df2['total_time']>1]
df2 = df2.sort_values(by='total_time',ascending=False)

top20 = df2.head(20)
g = sns.catplot(x='module_name', y='total_time', data=top20, kind='bar')
g.set_xticklabels(rotation=90)
g.set_xlabels("function called")
g.set_ylabels("Total_Time in seconds")
g.fig.suptitle('cProfile_train', weight='bold', fontsize=16)
plt.show()
