import pandas as pd


def load_data():
    import pandas as pd

    PL_2324_data = pd.read_csv("PL-season-2324.csv")
    PL_2425_data = pd.read_csv("PL-season-2425.csv")

    PL_2324_data["Date"] = pd.to_datetime(PL_2324_data["Date"], dayfirst=True)
    PL_2425_data["Date"] = pd.to_datetime(PL_2425_data["Date"], dayfirst=True)

    return PL_2324_data, PL_2425_data

def get_daily_standings(df):
    cols_to_exclude = ['HTAG', 'HTR', 'HTHG', 'Referee']

    home_df = df.drop(columns=cols_to_exclude).copy().rename(
        columns={
            'HomeTeam': 'Team', 'FTHG': 'GF', 'FTAG': 'GA',
            'HS': 'Shots For', 'AS': 'Opposition Shots',
            'HST': 'Shots on Target', 'AST': 'Opposition Shots on Target',
            'HF': 'Fouls', 'AF': 'Opposition Fouls',
            'HC': 'Corners', 'AC': 'Corners Against',
            'HY': 'Yellow Cards', 'AY': 'Opposition Yellow Cards',
            'HR': 'Red Cards', 'AR': 'Opposition Red Cards'
        }
    )

    away_df = df.drop(columns=cols_to_exclude).copy().rename(
        columns={
            'AwayTeam': 'Team', 'FTAG': 'GF', 'FTHG': 'GA',
            'AS': 'Shots For', 'HS': 'Opposition Shots',
            'AST': 'Shots on Target', 'HST': 'Opposition Shots on Target',
            'AF': 'Fouls', 'HF': 'Opposition Fouls',
            'AC': 'Corners', 'HC': 'Corners Against',
            'AY': 'Yellow Cards', 'HY': 'Opposition Yellow Cards',
            'AR': 'Red Cards', 'HR': 'Opposition Red Cards'
        }
    )

    home_df['Pts'] = 0
    home_df.loc[home_df['FTR'] == 'H', 'Pts'] = 3
    home_df.loc[home_df['FTR'] == 'D', 'Pts'] = 1

    away_df['Pts'] = 0
    away_df.loc[away_df['FTR'] == 'A', 'Pts'] = 3
    away_df.loc[away_df['FTR'] == 'D', 'Pts'] = 1

    stats = pd.concat([home_df, away_df]).sort_values('Date')
    stats['GD'] = stats['GF'] - stats['GA']

    to_exclude = ['Date', 'Team', 'FTR', 'Div']
    stat_cols = [
        c for c in stats.columns
        if c not in to_exclude and pd.api.types.is_numeric_dtype(stats[c])
    ]

    cum_cols = [f'Cum{c}' for c in stat_cols]
    stats[cum_cols] = stats.groupby('Team')[stat_cols].cumsum()

    all_dates = sorted(stats['Date'].unique())
    all_teams = stats['Team'].unique()

    grid = pd.MultiIndex.from_product(
        [all_dates, all_teams],
        names=['Date', 'Team']
    ).to_frame(index=False)

    daily = pd.merge(
        grid,
        stats[['Date', 'Team'] + stat_cols + cum_cols],
        on=['Date', 'Team'],
        how='left'
    )

    daily[cum_cols] = daily.groupby('Team')[cum_cols].ffill().fillna(0)

    daily = daily.sort_values(
        by=['Date', 'CumPts', 'CumGD', 'CumGF'],
        ascending=[True, False, False, False]
    )

    daily['Rank'] = daily.groupby('Date').cumcount() + 1

    return daily.reset_index(drop=True)

def home_away_stats(df):
    cols_to_exclude = ['HTAG', 'HTR', 'HTHG', 'Referee']

    home_df = df.drop(columns=cols_to_exclude).copy().rename(
        columns={
            'HomeTeam': 'Team', 'FTHG': 'GF', 'FTAG': 'GA',
            'HS': 'Shots For', 'AS': 'Opposition Shots',
            'HST': 'Shots on Target', 'AST': 'Opposition Shots on Target',
            'HF': 'Fouls', 'AF': 'Opposition Fouls',
            'HC': 'Corners', 'AC': 'Corners Against',
            'HY': 'Yellow Cards', 'AY': 'Opposition Yellow Cards',
            'HR': 'Red Cards', 'AR': 'Opposition Red Cards'
        }
    )

    away_df = df.drop(columns=cols_to_exclude).copy().rename(
        columns={
            'AwayTeam': 'Team', 'FTAG': 'GF', 'FTHG': 'GA',
            'AS': 'Shots For', 'HS': 'Opposition Shots',
            'AST': 'Shots on Target', 'HST': 'Opposition Shots on Target',
            'AF': 'Fouls', 'HF': 'Opposition Fouls',
            'AC': 'Corners', 'HC': 'Corners Against',
            'AY': 'Yellow Cards', 'HY': 'Opposition Yellow Cards',
            'AR': 'Red Cards', 'HR': 'Opposition Red Cards'
        }
    )

    home_df['Pts'] = 0
    home_df.loc[home_df['FTR'] == 'H', 'Pts'] = 3
    home_df.loc[home_df['FTR'] == 'D', 'Pts'] = 1

    away_df['Pts'] = 0
    away_df.loc[away_df['FTR'] == 'A', 'Pts'] = 3
    away_df.loc[away_df['FTR'] == 'D', 'Pts'] = 1

    results = []

    for stats in (home_df, away_df):
        stats['GD'] = stats['GF'] - stats['GA']

        to_exclude = ['Date', 'Team', 'FTR', 'Div']
        stat_cols = [
            c for c in stats.columns
            if c not in to_exclude and pd.api.types.is_numeric_dtype(stats[c])
        ]

        cum_cols = [f'Cum{c}' for c in stat_cols]
        stats[cum_cols] = stats.groupby('Team')[stat_cols].cumsum()

        all_dates = sorted(stats['Date'].unique())
        all_teams = stats['Team'].unique()

        grid = pd.MultiIndex.from_product(
            [all_dates, all_teams],
            names=['Date', 'Team']
        ).to_frame(index=False)

        daily = pd.merge(
            grid,
            stats[['Date', 'Team'] + stat_cols + cum_cols],
            on=['Date', 'Team'],
            how='left'
        )

        daily[cum_cols] = daily.groupby('Team')[cum_cols].ffill().fillna(0)

        daily = daily.sort_values(
            by=['Date', 'CumPts', 'CumGD', 'CumGF'],
            ascending=[True, False, False, False]
        )

        daily['Rank'] = daily.groupby('Date').cumcount() + 1
        results.append(daily)

    return results[0], results[1]
