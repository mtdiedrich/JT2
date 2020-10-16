from scipy.stats import norm
from analysis import analysis

import matplotlib.pyplot as plt


def grade_over_time():
    df = analysis.comparative_performance()
    #df = df[df['Extra']=='']
    df = df.reset_index(drop=True)
    df = df.sort_values('SUBMITTED')
    print()
    print('LENGTH', len(df))

    sqrt = len(df)**(1/3)
    
    plt.plot(df['PERF'].rolling(window=round(len(df)**(sqrt/(sqrt+1)))).mean().values)
    plt.plot(df['GRADE'].rolling(window=round(len(df)**(sqrt/(sqrt+1)))).mean().values)
    plt.show()

    m = df['TEAM BAT'].mean()
    s = df['TEAM BAT'].std()

    end = df['PERF'].rolling(window=round(len(df)**(sqrt/(sqrt+1)))).mean().values[-1]
    rv = norm(loc=m, scale=s).cdf(end)
    df = df.tail(round(len(df)**(sqrt/(sqrt+1))))
    print()
    print('SCORE', rv)
    print()
    print('PERF')
    print('MEAN:', df['PERF'].mean())
    print('STD:', df['PERF'].std())
    print()
    print('GRADE')
    print('MEAN:', df['GRADE'].mean())
    print('STD:', df['GRADE'].std())
    print()
    print(df.head(5))
    print()
    print(df.tail(5))
    print()
