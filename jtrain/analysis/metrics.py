def get_episode_measure(df):
    return get_cryt(df), get_batting_average(df)


def get_batting_average(df):
    temp = df.copy()
    temp = temp[temp['Round'] < 3]
    corr = sum(temp['NumCorrect'])
    incorr = sum(temp['NumIncorrect'])
    return corr/(len(temp) + incorr)


def get_cryt(df):
    temp = df.copy()
    temp = temp[temp['Round'] < 3]
    temp['DDbool'] = temp['DailyDouble'].astype(bool)
    temp['Ignore'] = (temp['DDbool']) & (temp['NumIncorrect'] > 0)
    temp['CorrNum'] = temp['NumCorrect'] - temp['NumIncorrect']
    temp['TrueValue'] = temp['Value'] * temp['Round']
    temp['Calc'] = temp['CorrNum'] * temp['TrueValue'] * 200
    temp.loc[temp['Ignore'] == 1, 'Calc'] = 0
    return sum(temp['Calc'])


def get_batting_average_by_round(df):
    temp = df.copy()
    temp = temp[temp['Round'] < 3]
    grp = temp.groupby('Round')
    avgs = [get_batting_average(item) for key, item in grp]
    return avgs
