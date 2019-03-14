import os

import pandas

pandas.set_option('display.max_columns', 10)
pandas.set_option('display.width', 300)


def read_data():
    """Read in dataset and return a dataframe with:
       - index: row_id
       - columns: original and derived features. Derived features include:
         - Result_Type_Bin: binary feature (PASS or DEFECT)
         - Week_Day: categorical (day of the week)
         - Is_Weekend: "binary (1 for weekend and 0 for weekday)."""

    data = pandas.read_csv(os.path.join('data', 'WIDS_Project_Generated_Data_10K.csv'), index_col=0)
    # data = pandas.read_csv(os.path.join('data', 'WIDS_Dataset_Full_Aug18_Jan19_Adjusted.csv'), index_col=0)
    data.index.name = 'row_id'

    # Add binary Result_Type_Bin variable
    data['Result_Type_Bin'] = data.Result_Type.map({
        'PASS': 'PASS',
        'Defect_1': 'DEFECT',
        'Defect_2': 'DEFECT',
        'Defect_3': 'DEFECT',
        'Defect_4': 'DEFECT'})

    # Add annotation by day of the week/weekend to explore whether there is an associations with defects appearance
    data['Week_Day'] = pandas.Categorical(
        pandas.to_datetime(data.Date).dt.day_name(),
        ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'])
    data['Is_Weekend'] = (pandas.to_datetime(data.Date).dt.dayofweek // 5 == 1).astype(float)

    return data


def impute_data_zone1(data):
    # Columns related to position in zone1
    zone1_pos = ['Zone1Position', 'Zone1_Row_Num', 'Zone1_Col_Num', 'Zone1_Left_Block_Bin', 'Zone1_Right_Block_Bin', 'Zone1_Area']

    # Investigate patterns of available data:
    # print(data[zone1_pos].notna().groupby(zone1_pos).size())

    print('{:.2f}% fraction of samples have positional information for Zone1'.format(
        100 * data.Zone1Position.notna().mean()))

    # Set Row based on Zone1_Area where we can.
    data.loc[data.Zone1_Area.isin(['Top Right', 'Top Left']), 'Zone1_Row_Num'] = 1
    data.loc[data.Zone1_Area.isin(['Bottom Right', 'Bottom Left']), 'Zone1_Row_Num'] = 2

    # Input values in 'Zone1Position' based on row and col position
    data.loc[(data.Zone1_Row_Num == 1) & (data.Zone1_Col_Num == 1), 'Zone1Position'] = 1
    data.loc[(data.Zone1_Row_Num == 1) & (data.Zone1_Col_Num == 2), 'Zone1Position'] = 2
    data.loc[(data.Zone1_Row_Num == 1) & (data.Zone1_Col_Num == 3), 'Zone1Position'] = 3
    data.loc[(data.Zone1_Row_Num == 1) & (data.Zone1_Col_Num == 4), 'Zone1Position'] = 4
    data.loc[(data.Zone1_Row_Num == 2) & (data.Zone1_Col_Num == 1), 'Zone1Position'] = 5
    data.loc[(data.Zone1_Row_Num == 2) & (data.Zone1_Col_Num == 2), 'Zone1Position'] = 6
    data.loc[(data.Zone1_Row_Num == 2) & (data.Zone1_Col_Num == 3), 'Zone1Position'] = 7
    data.loc[(data.Zone1_Row_Num == 2) & (data.Zone1_Col_Num == 4), 'Zone1Position'] = 8

    data.drop(columns=set(zone1_pos).difference(['Zone1Position']), inplace=True)

    # Investigate remaining patterns of missing data:
    print('{:.2f}% fraction of samples have positional information for Zone1 after imputation.'.format(
        100 * data.Zone1Position.notna().mean()))


def impute_data_zone2(data):
    # Columns related to position in zone2
    zone2_pos = ['Zone2Position', 'Zone2_Row_Num', 'Zone2_Col_num']

    # Investigate patterns of available data:
    # print(data[zone2_pos].notna().groupby(zone2_pos).size())

    print('{:.2f}% fraction of samples have positional information for Zone2'.format(
        100 * data.Zone2Position.notna().mean()))

    # Input values in 'Zone2Position' based on row and col position
    data.loc[(data.Zone2_Row_Num == 1) & (data.Zone2_Col_num == 1), 'Zone2Position'] = 1
    data.loc[(data.Zone2_Row_Num == 1) & (data.Zone2_Col_num == 2), 'Zone2Position'] = 2
    data.loc[(data.Zone2_Row_Num == 2) & (data.Zone2_Col_num == 1), 'Zone2Position'] = 3
    data.loc[(data.Zone2_Row_Num == 2) & (data.Zone2_Col_num == 2), 'Zone2Position'] = 4

    data.drop(columns=set(zone2_pos).difference(['Zone2Position']), inplace=True)

    print('{:.2f}% fraction of samples have positional information for Zone2 after imputation.'.format(
        100 * data.Zone2Position.notna().mean()))


def impute_data_zone3(data):
    # Columns related to position in zone3
    zone3_pos = ['Zone3Position', 'Zone3_Row_Num', 'Zone3_Col_Num', 'Zone3_Area']

    # Investigate patterns of available data:
    # print(data[zone3_pos].notna().groupby(zone3_pos).size())

    print('{:.2f}% fraction of samples have positional information for Zone3'.format(
        100 * data.Zone3Position.notna().mean()))

    # Set Position based on Zone3_Area and Row/Column where we can.
    data.loc[(data.Zone3_Area == 'Top Left') & (data.Zone3_Col_Num == 2), 'Zone3Position'] = 2
    data.loc[(data.Zone3_Area == 'Top Left') & (data.Zone3_Row_Num == 2), 'Zone3Position'] = 4
    data.loc[(data.Zone3_Area == 'Bottom Right') & (data.Zone3_Row_Num == 1), 'Zone3Position'] = 3
    data.loc[(data.Zone3_Area == 'Bottom Right') & (data.Zone3_Col_Num == 2), 'Zone3Position'] = 5

    # Input values in 'Zone2Position' based on row and col position
    data.loc[(data.Zone3_Row_Num == 1) & (data.Zone3_Col_Num == 1), 'Zone3Position'] = 1
    data.loc[(data.Zone3_Row_Num == 1) & (data.Zone3_Col_Num == 2), 'Zone3Position'] = 2
    data.loc[(data.Zone3_Row_Num == 1) & (data.Zone3_Col_Num == 3), 'Zone3Position'] = 3
    data.loc[(data.Zone3_Row_Num == 2) & (data.Zone3_Col_Num == 1), 'Zone3Position'] = 4
    data.loc[(data.Zone3_Row_Num == 2) & (data.Zone3_Col_Num == 2), 'Zone3Position'] = 5
    data.loc[(data.Zone3_Row_Num == 2) & (data.Zone3_Col_Num == 3), 'Zone3Position'] = 6

    data.drop(columns=set(zone3_pos).difference(['Zone3Position']), inplace=True)

    print('{:.2f}% fraction of samples have positional information for Zone3 after imputation.'.format(
        100 * data.Zone3Position.notna().mean()))


def get_prepared_data():
    data = read_data()

    # Impute missing data from redundant information
    impute_data_zone1(data)
    impute_data_zone2(data)
    impute_data_zone3(data)

    # # Drop entries with missing data
    # # TODO: Revisit after coming up with a strategy to deal with missing data
    # data = data.dropna()

    # Drop un-informative columns
    data.drop(columns=['Block_Orientation'], inplace=True)  # Same value in column

    return data


if __name__ == '__main__':
    data = get_prepared_data()
