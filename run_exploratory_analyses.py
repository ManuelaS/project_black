import os

import matplotlib.pyplot
import numpy
import pandas
import seaborn

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


def plot_var_by_SKU_and_result_type(data, cols):
    data = data.copy()
    data.set_index(['SKU', 'Result_Type'], inplace=True)
    data = data[cols].stack().to_frame('value')
    data.index.names = ['SKU', 'Result_Type', 'vars']

    seaborn.catplot(x='SKU', y='value',
                    kind='violin',
                    hue='Result_Type',
                    row='vars',
                    dodge=True,
                    palette='Set1',
                    data=data.reset_index())


def plot_var_by_date_and_SKU(data, cols):
    data = data.copy()
    data.set_index(['Date', 'SKU', 'Result_Type'], inplace=True)
    data = data[cols].stack().to_frame('value')
    data.index.names = ['Date', 'SKU', 'Result_Type', 'vars']

    g = seaborn.relplot(x='Date', y='value',
                        err_style="bars",
                        row='SKU',
                        col='vars',
                        hue='SKU',
                        kind='line',
                        palette='Set1',
                        data=data.reset_index())
    g.set_xticklabels(rotation=90)
    matplotlib.pyplot.tight_layout()


def plot_correlation_among_features(data, cols):
    data = data.copy()
    data = data[cols]
    # Correlation among different features
    corr = data.corr()
    mask = numpy.zeros_like(corr)
    mask[numpy.triu_indices_from(mask)] = True
    #f = matplotlib.pyplot.figure()
    seaborn.heatmap(corr,
                    mask=mask,
                    cmap='RdBu',
                    vmin=-1,
                    vmax=1,
                    linewidths=1,
                    linecolor='w',
                    square=True,
                    xticklabels=True,
                    yticklabels=True)
    matplotlib.pyplot.tight_layout()


if __name__ == '__main__':
    data = read_data()
    print('Dataset with {} rows and {} columns'.format(data.shape[0], data.shape[1]))

    # Drop entries with missing data
    # TODO: Revisit after coming up with a strategy to deal with missing data
    data = data.dropna()
    print('After removing missing data, dataset with {} rows and {} columns'.format(data.shape[0], data.shape[1]))

    # Exploratory plots
    matplotlib.pyplot.close('all')

    # Influence of temperature on defects
    plot_correlation_among_features(data, ['Zone1_Temp_Min', 'Zone2_Temp_Min', 'Zone3_Temp_Min',
                                           'Zone1_Temp_Max', 'Zone2_Temp_Max', 'Zone3_Temp_Max',
                                           'Zone1_Temp_Range', 'Zone2_Temp_Range', 'Zone3_Temp_Range',
                                           'Zone1_Temp_Avg', 'Zone2_Temp_Avg', 'Zone3_Temp_Avg'])


    plot_var_by_SKU_and_result_type(data, ['Zone1_Temp_Min', 'Zone2_Temp_Min', 'Zone3_Temp_Min'])
    plot_var_by_SKU_and_result_type(data, ['Zone1_Temp_Max', 'Zone2_Temp_Max', 'Zone3_Temp_Max'])
    plot_var_by_SKU_and_result_type(data, ['Zone1_Temp_Avg', 'Zone2_Temp_Avg', 'Zone3_Temp_Avg'])
    plot_var_by_SKU_and_result_type(data, ['Zone1_Temp_Range', 'Zone2_Temp_Range', 'Zone3_Temp_Range'])



    # Influence of humidity on defects
    plot_correlation_among_features(data, ['Zone1_Humidity_Min', 'Zone2_Humidity_Min', 'Zone3_Humidity_Min',
                                           'Zone1_Humidity_Max', 'Zone2_Humidity_Max', 'Zone3_Humidity_Max',
                                           'Zone1_Humidity_Range', 'Zone2_Humidity_Range', 'Zone3_Humidity_Range',
                                           'Zone1_Humidity_Avg', 'Zone2_Humidity_Avg', 'Zone3_Humidity_Avg'])
    plot_var_by_SKU_and_result_type(data, ['Zone1_Humidity_Min', 'Zone2_Humidity_Min', 'Zone3_Humidity_Min'])
    plot_var_by_SKU_and_result_type(data, ['Zone1_Humidity_Max', 'Zone2_Humidity_Max', 'Zone3_Humidity_Max'])
    plot_var_by_SKU_and_result_type(data, ['Zone1_Humidity_Avg', 'Zone2_Humidity_Avg', 'Zone3_Humidity_Avg'])
    plot_var_by_SKU_and_result_type(data, ['Zone1_Humidity_Range', 'Zone2_Humidity_Range', 'Zone3_Humidity_Range'])


    # Influence of date on defects broken down by SKU
    plot_var_by_date_and_SKU(data, ['Passed_QC_Count'])
    plot_var_by_date_and_SKU(data, ['Passed_QC_Count', 'Defect_1_Count', 'Defect_2_Count', 'Defect_3_Count',
                                    'Defect_4_Count'])

