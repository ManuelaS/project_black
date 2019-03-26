import os

import graphviz
import matplotlib.pyplot
import numpy
import pandas
import seaborn
import sklearn.tree
import statsmodels.graphics.mosaicplot

import prepare_data
import zone_path_sankey

pandas.set_option('display.max_columns', 10)
pandas.set_option('display.width', 150)


def plot_var_by_SKU_and_result_type(data, cols):
    data2 = data.copy()
    data2.SKU = data2.SKU.astype('object')
    data2.set_index(['SKU', 'Result_Type'], inplace=True)
    data2 = data2[cols].stack().to_frame('value')
    data2.index.names = ['SKU', 'Result_Type', 'vars']

    seaborn.catplot(x='SKU', y='value',
                    kind='violin',
                    hue='Result_Type',
                    row='vars',
                    dodge=True,
                    palette='Set1',
                    data=data2.reset_index())


def plot_var_by_date_and_SKU(data, cols):
    data = data.copy()
    data.SKU = data.SKU.astype('object')
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


def plot_cat_data_association(data, cols, name):
    statsmodels.graphics.mosaicplot.mosaic(data.groupby(cols).size())
    matplotlib.pyplot.savefig(os.path.join('figures', name+'.png'))


def plot_cost_defect_association(data, costs):
    statsmodels.graphics.mosaicplot.mosaic(data.join(costs, on='SKU').groupby(['SKU', 'Result_Type']).Value.sum())
    matplotlib.pyplot.savefig(os.path.join('figures', 'SKU_vs_Result_Type_costs.png'))


def plot_zone_position_defect(data):
    fig, ax = matplotlib.pyplot.subplots(1, 3)
    data.groupby(['Zone1Position', 'Result_Type']).size().unstack().plot(kind='bar', stacked=True, ax=ax[0])
    data.groupby(['Zone2Position', 'Result_Type']).size().unstack().plot(kind='bar', stacked=True, ax=ax[1])
    data.groupby(['Zone3Position', 'Result_Type']).size().unstack().plot(kind='bar', stacked=True, ax=ax[2])
    matplotlib.pyplot.savefig(os.path.join('figures', 'defects_by_position.png'))


def plot_opportunities(data, costs):
    data2 = data.join(costs, on='SKU')
    data2 = data2[data2.Result_Type != 'PASS']
    data2.SKU.replace(['B003', 'C005', 'X007', 'Z009'], 'NotA001', inplace=True)
    opportunities = data2.groupby(['SKU', 'Result_Type']).Value.sum().sort_values(ascending=False) / 1e6
    matplotlib.pyplot.figure()
    opportunities.plot(kind='bar', width=0.9)
    matplotlib.pyplot.ylabel('Potential savings [Mill Euro]')
    matplotlib.pyplot.tight_layout()
    matplotlib.pyplot.savefig(os.path.join('figures', 'opportunities.png'))


def analyze_opportunity1(data):
    # Analyze root cause of opportunity 1 defects (Defect_2 in NonA001 SKUs)
    data2 = data[(data.SKU != 'A001') & data.Result_Type.isin(['PASS', 'Defect_2'])].dropna()
    x = pandas.get_dummies(data2.drop(columns=['Result_Type_Bin', 'Result_Type', 'Date', 'SKU']))
    tree = sklearn.tree.DecisionTreeClassifier(min_samples_split=1000, min_samples_leaf=500,
                                               min_impurity_split=0.1).fit(x, data2.Result_Type.astype('object'))
    graph = sklearn.tree.export_graphviz(tree,
                                         impurity=False,
                                         precision=2,
                                         special_characters=True,
                                         max_depth=3,
                                         feature_names=x.columns,
                                         class_names=tree.classes_,
                                         filled=True,
                                         rounded=True,
                                         proportion=True)
    graphviz.Source(graph).render(os.path.join('figures', 'opportunity1_tree'), format='png')
    graphviz.Source(graph).render(os.path.join('figures', 'opportunity1_tree'), format='pdf')



def plot_opportunity1_partial_dependency_plot(data):
    data2 = data[(data.Zone3Position == '6') & (data.SKU != 'A001') & data.Result_Type.isin(['PASS', 'Defect_2'])].copy()

    data2['HasDefect'] = data2.Result_Type != 'PASS'
    groups = data2.groupby([pandas.cut(data2.Zone1_Humidity_Min, range(16, 53), precision=0),
                            pandas.cut(data2.Zone1_Temp_Range, range(0, 23), precision=0)])
    data3 = groups.HasDefect.mean().unstack()
    counts = groups.size().unstack(fill_value=0).values # Count number of samples for each group

    matplotlib.pyplot.figure()
    cmap = matplotlib.colors.LinearSegmentedColormap.from_list('red_blue', ['#e31a1c', '#1f78b4'])
    ax = seaborn.heatmap(data3, cmap=cmap, cbar_kws={'label': 'Defect 2 incidence rate'})
    ax.invert_yaxis()
    matplotlib.pyplot.tight_layout()
    matplotlib.pyplot.savefig(os.path.join('figures', 'opportunity1_partial_dependency.png'))
    matplotlib.pyplot.savefig(os.path.join('figures', 'opportunity1_partial_dependency.pdf'))

    quad_mesh = ax.findobj(matplotlib.collections.QuadMesh)[0]
    colors = quad_mesh.get_facecolors()
    alpha = counts / counts.max().max()
    colors[:, -1] = alpha.reshape(-1)
    quad_mesh.set_facecolors(colors)
    matplotlib.pyplot.savefig(os.path.join('figures', 'opportunity1_partial_dependency_alpha.png'))
    matplotlib.pyplot.savefig(os.path.join('figures', 'opportunity1_partial_dependency_alpha.pdf'))


def analyze_opportunity2(data):
    # Analyze root cause of opportunity 2 defects (Defect_1 in A001 SKUs)
    data2 = data[(data.SKU == 'A001') & data.Result_Type.isin(['PASS', 'Defect_1'])].dropna()
    x = pandas.get_dummies(data2.drop(columns=['Result_Type_Bin', 'Result_Type', 'Date', 'SKU']))
    tree = sklearn.tree.DecisionTreeClassifier(min_samples_split=1000, min_samples_leaf=100,
                                               min_impurity_split=0.1).fit(x, data2.Result_Type.astype('object'))
    graph = sklearn.tree.export_graphviz(tree, feature_names=x.columns, class_names=tree.classes_, filled=True,
                                         rounded=True, proportion=False)
    graphviz.Source(graph).render(os.path.join('figures', 'opportunity2_tree'), format='png')


def plot_opportunity2_partial_dependency_plot(data):
    data2 = data[(data.SKU == 'A001') & data.Result_Type.isin(['PASS', 'Defect_1'])].copy()

    data2['HasDefect'] = data2.Result_Type != 'PASS'
    data2['Zone1_Temp_Range'] = data2.Zone1_Temp_Range.round(0)

    matplotlib.pyplot.figure()
    seaborn.lineplot('Zone1_Temp_Range', 'HasDefect', data=data2)
    matplotlib.pyplot.tight_layout()
    matplotlib.pyplot.savefig(os.path.join('figures', 'opportunity2_partial_dependency.png'))


def analyze_opportunity3(data):
    # Analyze root cause of opportunity 3 defects (Defect_3 in NonA001 SKUs)
    data2 = data[(data
                  .SKU != 'A001') & data.Result_Type.isin(['PASS', 'Defect_3'])].dropna()
    x = pandas.get_dummies(data2.drop(columns=['Result_Type_Bin', 'Result_Type', 'Date', 'SKU']))
    tree = sklearn.tree.DecisionTreeClassifier(min_samples_split=10, min_samples_leaf=10,
                                               min_impurity_split=0.065).fit(x, data2.Result_Type.astype('object'))
    graph = sklearn.tree.export_graphviz(tree, feature_names=x.columns, class_names=tree.classes_, filled=True,
                                         rounded=True, proportion=True)
    graphviz.Source(graph).render(os.path.join('figures', 'opportunity3_tree'), format='png')


def plot_opportunity3_partial_dependency_plot(data):
    data2 = data[(data.Zone2Position == '1') & (data.SKU != 'A001') & data.Result_Type.isin(['PASS', 'Defect_3'])].copy()

    data2['HasDefect'] = data2.Result_Type != 'PASS'
    data2.dropna(subset=['HasDefect', 'Block_Position', 'Zone1_In_Zone3_Out_Dur'], inplace=True)


    matplotlib.pyplot.figure()
    ax=seaborn.lineplot('Zone1_In_Zone3_Out_Dur', 'HasDefect', hue=data2.Block_Position.astype('int64'), data=data2, palette='Set1')
    ax.set_ylabel('Defect rate')
    matplotlib.pyplot.tight_layout()
    matplotlib.pyplot.savefig(os.path.join('figures', 'opportunity3_partial_dependency.png'))

if __name__ == '__main__':
    data = prepare_data.get_prepared_data()
    costs = prepare_data.get_costs()

    # Exploratory plots
    matplotlib.pyplot.close('all')
    os.makedirs('figures', exist_ok=True)

    # Association between SKU and categorical variables
    plot_cat_data_association(data, ['SKU', 'Result_Type_Bin'], 'SKU_vs_Result_Type_Bin')
    plot_cat_data_association(data, ['SKU', 'Result_Type'], 'SKU_vs_Result_Type')
    plot_cat_data_association(data, ['SKU', 'Block_Num'], 'SKU_vs_Block_Num')
    plot_cat_data_association(data, ['SKU', 'Block_Position'], 'SKU_vs_Block_Position')
    plot_cost_defect_association(data, costs)
    plot_opportunities(data, costs)

    analyze_opportunity1(data)
    plot_zone_position_defect(data)
    plot_opportunity1_partial_dependency_plot(data)
    zone_path_sankey.make_sankey(data[data.Result_Type.isin(['PASS', 'Defect_2'])])

    analyze_opportunity3(data)
    plot_opportunity3_partial_dependency_plot(data)


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
                                           'Total_Zone123_Dur'])
