import numpy as np
from matplotlib import pyplot as plt

def foo(days, times):
    days_later = [3**t for t in range(times)]

    temp = [int(round(day + d)) for d in days_later for day in range(days)]
    unique = list(set(list(temp)))
    counts = [temp.count(u) for u in unique]

    plt.bar(unique, counts, align='center', alpha=0.5)
    plt.show()

