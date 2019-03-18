import os

import matplotlib.pyplot
import numpy
import pandas
import seaborn
import sklearn.model_selection

import prepare_data

data = prepare_data.get_prepared_data()

data2 = prepare_data.balance_dataset(data.dropna(), 'Result_Type')

x = pandas.get_dummies(data2.drop(columns=['Result_Type', 'Result_Type_Bin', 'Date']))
y = data2.Result_Type#.astype('category')
rf = sklearn.ensemble.RandomForestClassifier(n_estimators=1000, oob_score=True, random_state=0)
rf.fit(x, y)

oob_prediction = pandas.Series(rf.classes_[numpy.argmax(rf.oob_decision_function_,axis=1)], index=x.index)
print(sklearn.metrics.classification_report(y, oob_prediction))
print(sklearn.metrics.balanced_accuracy_score(y, oob_prediction))

# Make plots
os.makedirs('figures', exist_ok=True)

matplotlib.pyplot.figure()
pandas.Series(rf.feature_importances_, index=x.columns).sort_values(ascending=False).head(10).plot(kind='bar')
matplotlib.pyplot.xlabel('Features')
matplotlib.pyplot.ylabel('Importance')
matplotlib.pyplot.tight_layout()
matplotlib.pyplot.savefig(os.path.join('figures', 'rf_variable_importance.png'))

matplotlib.pyplot.figure()
seaborn.heatmap(pandas.DataFrame(sklearn.metrics.confusion_matrix(y, oob_prediction),
                                 index=rf.classes_,
                                 columns=rf.classes_),
                cmap='Blues',
                cbar_kws={'label': 'Number of products'})
matplotlib.pyplot.xlabel('Golden truth')
matplotlib.pyplot.ylabel('Out-of-bag predictions')
matplotlib.pyplot.tight_layout()
matplotlib.pyplot.savefig(os.path.join('figures', 'rf_confusion_matrix.png'))

