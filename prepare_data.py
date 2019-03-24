import os

import pandas

pandas.set_option('display.max_columns', 10)
pandas.set_option('display.width', 150)


def read_data():
    """Read in dataset and return a dataframe with:
       - index: row_id
       - columns: original and derived features. Derived features include:
         - Result_Type_Bin: categorical feature (PASS or DEFECT)."""

    # data = pandas.read_csv(os.path.join('data', 'WIDS_Project_Generated_Data_10K.csv'), index_col=0)
    data = pandas.read_csv(os.path.join('data', 'WIDS_Dataset_Full_Aug18_Jan19_Adjusted.csv.gz'),
                           index_col=0,
                           dtype={
                               'Zone1Position': 'category',
                               'Zone2Position': 'category',
                               'Zone3Position': 'category',
                               'SKU': 'category',
                               'Block_Num': 'category',
                               'Block_Position': 'category',
                               'Result_Type': 'category',
                               'Passed_QC_Count': 'Int64',
                               'Defect_1_Count': 'Int64',
                               'Defect_2_Count': 'Int64',
                               'Defect_3_Count': 'Int64',
                               'Defect_4_Count': 'Int64',
                           })
    data.index.name = 'row_id'

    # Add binary Result_Type_Bin variable
    data['Result_Type_Bin'] = data.Result_Type.map({
        'PASS': 'PASS',
        'Defect_1': 'DEFECT',
        'Defect_2': 'DEFECT',
        'Defect_3': 'DEFECT',
        'Defect_4': 'DEFECT'}).astype('category')

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
    data.loc[(data.Zone1_Row_Num == 1) & (data.Zone1_Col_Num == 1), 'Zone1Position'] = '1'
    data.loc[(data.Zone1_Row_Num == 1) & (data.Zone1_Col_Num == 2), 'Zone1Position'] = '2'
    data.loc[(data.Zone1_Row_Num == 1) & (data.Zone1_Col_Num == 3), 'Zone1Position'] = '3'
    data.loc[(data.Zone1_Row_Num == 1) & (data.Zone1_Col_Num == 4), 'Zone1Position'] = '4'
    data.loc[(data.Zone1_Row_Num == 2) & (data.Zone1_Col_Num == 1), 'Zone1Position'] = '5'
    data.loc[(data.Zone1_Row_Num == 2) & (data.Zone1_Col_Num == 2), 'Zone1Position'] = '6'
    data.loc[(data.Zone1_Row_Num == 2) & (data.Zone1_Col_Num == 3), 'Zone1Position'] = '7'
    data.loc[(data.Zone1_Row_Num == 2) & (data.Zone1_Col_Num == 4), 'Zone1Position'] = '8'

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
    data.loc[(data.Zone2_Row_Num == 1) & (data.Zone2_Col_num == 1), 'Zone2Position'] = '1'
    data.loc[(data.Zone2_Row_Num == 1) & (data.Zone2_Col_num == 2), 'Zone2Position'] = '2'
    data.loc[(data.Zone2_Row_Num == 2) & (data.Zone2_Col_num == 1), 'Zone2Position'] = '3'
    data.loc[(data.Zone2_Row_Num == 2) & (data.Zone2_Col_num == 2), 'Zone2Position'] = '4'

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
    data.loc[(data.Zone3_Area == 'Top Left') & (data.Zone3_Col_Num == 2), 'Zone3Position'] = '2'
    data.loc[(data.Zone3_Area == 'Top Left') & (data.Zone3_Row_Num == 2), 'Zone3Position'] = '4'
    data.loc[(data.Zone3_Area == 'Bottom Right') & (data.Zone3_Row_Num == 1), 'Zone3Position'] = '3'
    data.loc[(data.Zone3_Area == 'Bottom Right') & (data.Zone3_Col_Num == 2), 'Zone3Position'] = '5'

    # Input values in 'Zone2Position' based on row and col position
    data.loc[(data.Zone3_Row_Num == 1) & (data.Zone3_Col_Num == 1), 'Zone3Position'] = '1'
    data.loc[(data.Zone3_Row_Num == 1) & (data.Zone3_Col_Num == 2), 'Zone3Position'] = '2'
    data.loc[(data.Zone3_Row_Num == 1) & (data.Zone3_Col_Num == 3), 'Zone3Position'] = '3'
    data.loc[(data.Zone3_Row_Num == 2) & (data.Zone3_Col_Num == 1), 'Zone3Position'] = '4'
    data.loc[(data.Zone3_Row_Num == 2) & (data.Zone3_Col_Num == 2), 'Zone3Position'] = '5'
    data.loc[(data.Zone3_Row_Num == 2) & (data.Zone3_Col_Num == 3), 'Zone3Position'] = '6'

    data.drop(columns=set(zone3_pos).difference(['Zone3Position']), inplace=True)

    print('{:.2f}% fraction of samples have positional information for Zone3 after imputation.'.format(
        100 * data.Zone3Position.notna().mean()))

    # Recreate other positional variables based on Zone3Position
    data['Zone3_Area'] = data.Zone3Position.map(
        {'1': 'Top Left', '2': 'Top Left', '3': 'Bottom Right',
         '4': 'Top Left', '5': 'Bottom Right', '6': 'Bottom Right'}).astype('category')


def impute_data_duration(data):
    # Drop AVG_Zone123_Dur as it is redundant with Total_Zone123_Dur and the 2 columns are filled in the same cases
    assert ((data.Total_Zone123_Dur.isna() == data.AVG_Zone123_Dur.isna()).all())
    data.drop(columns=['AVG_Zone123_Dur'], inplace=True)

    # Columns related to duration
    dur_cols = ['Zone1_Dur', 'Zone2_Dur', 'Zone3_Dur',
                'Zone1_Out_Zone2_In_Dur', 'Zone1_Out_Zone3_In_Dur', 'Zone2_Out_Zone3_In_Dur',
                'Zone1_In_Zone3_Out_Dur', 'Zone1_In_Zone2_Out_Dur', 'Zone2_In_Zone3_Out_Dur',
                'Total_Dur', 'Total_Zone123_Dur']

    # Investigate patterns of available data:
    # print(data[dur_cols].notna().groupby(dur_cols).size())


def get_prepared_data():
    data = read_data()

    # Impute missing data from redundant information
    impute_data_zone1(data)
    impute_data_zone2(data)
    impute_data_zone3(data)
    impute_data_duration(data)

    # # Drop entries with missing data
    # # TODO: Revisit after coming up with a strategy to deal with missing data
    # data = data.dropna()

    # Drop un-informative columns
    data.drop(columns=['Block_Orientation'], inplace=True)  # Same value in column

    return data


def balance_dataset(data, varname):
    # Create a balanced dataset, balanced on a categorical variable.
    # Sub-samples data for each category down to the number of occurrences of the least common category.
    per_cat_n = data[varname].value_counts().min()
    return pandas.concat([
        sub_data.sample(per_cat_n) for _, sub_data in data.groupby(varname)
    ])


def get_costs():
    return pandas.read_excel(os.path.join('data', 'Costs.xlsx'), skiprows=1, usecols=['SKU', 'Value'], index_col='SKU')


if __name__ == '__main__':
    data = get_prepared_data()
