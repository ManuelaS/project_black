import os

import matplotlib.pyplot
import statsmodels.graphics.mosaicplot
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
    # Investigate patterns of missing data:
    print(data[zone1_pos].isna().groupby(zone1_pos).size())

    print('{:.2f}% fraction of samples have missing positional information for Zone1'.format(
        100 * data[zone1_pos].isna().any(axis=1).mean()))
    print(
        'but complete positional information can be made out from Zone1Position except when missing. Zone1Position is '
        'missing for {:.2f}% of the samples)'.format(100 * data.Zone1Position.isna().mean()))

    print('If Zone1Position information is available, all other position columns can be inferred.')
    print('Zone1Position can be inferred from Row+Col, when both are present')
    print(
        'If Col is missing, we will be unable to determine exact Zone1Position, as this is not available anywhere else')
    print('If Row is missing it can be inferred from Zone1_Area')

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
    print('After imputation {:.2f}% fraction of samples have missing positional information for Zone1'.format(
        100 * data['Zone1Position'].isna().mean()))


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
    f = matplotlib.pyplot.figure()
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


def plot_paired_grid(data, grouping_var, cols):
    data = data.copy()
    data.set_index(grouping_var, inplace=True)
    data = data[cols]

    g = seaborn.PairGrid(data.reset_index(),
                         hue=grouping_var,
                         palette='Set1')
    g = g.map_diag(matplotlib.pyplot.hist)
    g = g.map_lower(matplotlib.pyplot.scatter, edgecolor="w", s=20)
    g = g.map_upper(seaborn.kdeplot, cmap='Blues')
    g = g.add_legend()


def plot_cat_data_association(data, cols):
    statsmodels.graphics.mosaicplot.mosaic(data, cols)


if __name__ == '__main__':
    data = read_data()
    print('Dataset with {} rows and {} columns'.format(data.shape[0], data.shape[1]))

    # Drop un-informative columns
    data.drop(columns=['Block_Orientation'], inplace=True) # Same value in column

    # Impute missing data from redundant information
    impute_data_zone1(data)

    # Drop entries with missing data
    # TODO: Revisit after coming up with a strategy to deal with missing data
    data = data.dropna()
    print('After removing missing data, dataset with {} rows and {} columns'.format(data.shape[0], data.shape[1]))

    # Exploratory plots
    matplotlib.pyplot.close('all')

    # Association between SKU and categorical variables
    plot_cat_data_association(data, ['SKU', 'Result_Type_Bin'])
    plot_cat_data_association(data, ['SKU', 'Result_Type'])
    plot_cat_data_association(data, ['SKU', 'Week_Day'])
    plot_cat_data_association(data, ['SKU', 'Is_Weekend'])
    plot_cat_data_association(data, ['SKU', 'Block_Num'])
    plot_cat_data_association(data, ['SKU', 'Block_Position'])


    # Correlation among numerical variables
    plot_correlation_among_features(data, data.columns)


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
    plot_var_by_date_and_SKU(data, ['Defect_1_Count', 'Defect_2_Count', 'Defect_3_Count',
                                    'Defect_4_Count'])


    # Influence of time taken to manufacture the product. Do products made quickly have more defects?
    seaborn.violinplot(x='SKU', y='Total_Dur', data=data)
    plot_paired_grid(data, 'Result_Type_Bin', ['Zone1_Dur', 'Zone2_Dur', 'Zone3_Dur'])
    plot_paired_grid(data, 'Result_Type', ['Zone1_Dur', 'Zone2_Dur', 'Zone3_Dur'])
    plot_correlation_among_features(data, ['Result_Type_Bin', 'Zone1_Dur', 'Zone2_Dur', 'Zone3_Dur', 'Zone1_Out_Zone2_In_Dur',
                                           'Zone1_Out_Zone3_In_Dur', 'Zone2_Out_Zone3_In_Dur',
                                           'Zone1_In_Zone3_Out_Dur', 'Zone1_In_Zone2_Out_Dur', 'Zone2_In_Zone3_Out_Dur', 'Total_Dur',
                                           'Total_Zone123_Dur', 'AVG_Zone123_Dur'])
