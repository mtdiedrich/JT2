def get_episode_measure(df):
    return get_cryt(df), get_batting_average(df)

def get_batting_average(df):
    temp = df.copy()
    temp = temp[temp['Round'] < 3]
    corr = len(temp[temp['NumCorrect'] > 0])
    return corr/len(temp)

def get_cryt(df):
    temp = df.copy()
    temp['Ignore'] = (temp['DailyDouble'].astype(bool)) & (temp['NumIncorrect'] > 0)
    temp['Calc'] = (1 - temp['Ignore']) * (temp['NumCorrect'] - temp['NumIncorrect']) 
    cryt = sum(temp['Calc'] * temp['Value'] * 200)
    return cryt
