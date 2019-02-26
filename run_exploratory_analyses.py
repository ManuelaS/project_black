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


if __name__ == '__main__':
    data = read_data()
    print('Dataset with {} rows and {} columns'.format(data.shape[0], data.shape[1]))

    # Drop entries with missing data
    # TODO: Revisit after coming up with a strategy to deal with missing data
    data = data.dropna()
    print('After removing missing data, dataset with {} rows and {} columns'.format(data.shape[0], data.shape[1]))
