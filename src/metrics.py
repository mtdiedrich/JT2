def get_episode_measure(df):
    return get_cryt(df), get_batting_average(df)

def get_batting_average(df):
    temp = df.copy()
    temp = temp[temp['Round'] < 3]
    #corr = len(temp[temp['NumCorrect'] > 0])
    #return corr/len(temp)
    corr = sum(temp['NumCorrect'])
    incorr = sum(temp['NumIncorrect'])
    return corr/(len(temp) + incorr)

def get_cryt(df):
    temp = df.copy()
    temp = temp[temp['Round'] < 3]
    temp['Ignore'] = (temp['DailyDouble'].astype(bool)) & (temp['NumIncorrect'] > 0)
    temp['Calc'] = (temp['NumCorrect'] - temp['NumIncorrect']) * temp['Value'] * temp['Round'] * 200 
    temp.loc[temp['Ignore']==1, 'Calc'] = 0
    return sum(temp['Calc'])

def get_batting_average_by_round(df):
    temp = df.copy()
    date = list(set(list(temp['Date'].values)))[0]
    temp = temp[temp['Round'] < 3]
    grp = temp.groupby('Round')
    avgs = [get_batting_average(item) for key, item in grp]
    return avgs
