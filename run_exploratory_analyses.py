import matplotlib.pyplot
import numpy
import pandas
import seaborn
import statsmodels.graphics.mosaicplot

import prepare_data

pandas.set_option('display.max_columns', 10)
pandas.set_option('display.width', 300)


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
    data.dropna(inplace=True)

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
    data = prepare_data.get_prepared_data()

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
