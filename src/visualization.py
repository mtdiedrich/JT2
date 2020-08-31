from scipy.stats import norm

import matplotlib.pyplot as plt

import analysis

def grade_over_time():
    df = analysis.comparative_performance()
    print()
    print('LENGTH', len(df))
    """
    df = df[~df['Extra'].str.contains('Kids')]
    df = df[~df['Extra'].str.contains('Teen')]
    df = df[~df['Extra'].str.contains('Celebrity')]
    df = df[~df['Extra'].str.contains('College')]
    df = df[~df['Extra'].str.contains('Senior')]
    df = df[~df['Extra'].str.contains('Tournament')]
    df = df[~df['Extra'].str.contains('Week')]
    """
    df = df.reset_index(drop=True)
    df = df.sort_values('SUBMITTED')
    
    plt.plot(df['PERF'].rolling(window=round(len(df)**(1/2))).mean().values)
    plt.plot(df['GRADE'].rolling(window=round(len(df)**(1/2))).mean().values)
    plt.show()

    m = df['TEAM BAT'].mean()
    s = df['TEAM BAT'].std()

    end = df['PERF'].rolling(window=round(len(df)**(1/2))).mean().values[-1]
    rv = norm(loc=m, scale=s).cdf(end)
    df = df.tail(round(len(df)**(1/2)))
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
    print(df)
    print()
