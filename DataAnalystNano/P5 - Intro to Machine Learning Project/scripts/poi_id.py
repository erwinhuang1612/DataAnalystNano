#!/usr/bin/python

###Preparation

import pickle
import sys
import numpy
import numpy as np
import pandas
import sklearn
from time import time
from copy import copy
from pprint import pprint
import matplotlib
import matplotlib.pyplot as plt
##%matplotlib inline

import warnings
warnings.filterwarnings('ignore')

sys.path.append("../tools/")

import seaborn
import seaborn as sns

from tester import test_classifier, dump_classifier_and_data
from feature_format import featureFormat, targetFeatureSplit

import enron 
import evaluate

numpy.random.seed(43)


## Create features list
features_list = ['poi', 'to_messages', 'salary',  'total_payments', 'total_stock_value',
                 'deferral_payments', 'bonus', 'loan_advances', 'expenses', 'shared_receipt_with_poi',
                 'restricted_stock_deferred', 'deferred_income', 'exercised_stock_options',
                 'from_this_person_to_poi', 'from_poi_to_this_person', 'restricted_stock',   
                 'other', 'long_term_incentive', 'from_messages', 'director_fees'] 

## Get POI file
fpoi = open("poi_names.txt", "r")

### Get the dataset
enron_data = pickle.load(open("final_project_dataset.pkl", "r") )

# Test print information of one recpr`d
print enron_data["SKILLING JEFFREY K"]

#Number of Individuals in the dataset
individuals = len(enron_data)
print "Number of individuals in the dataset: " + str(individuals) + " individuals"

#Features in the dataset
features = len(enron_data['SKILLING JEFFREY K'])
print "There are " + str(features) + " features in the dataset."

#poi's in the dataset
def count_poi(file):
    count = 0 
    for person in file:
        if file[person]['poi'] == True:
            count += 1
    print "There are " + str(count) + " poi's in the dataset."

count_poi(enron_data)

#Number of POI's
poi_file = open("poi_names.txt", "r")
rfile =poi_file.readlines()
poi_length = len(rfile[2:])
print "Number of POI's: " + str(poi_length) + " POI's"

##Detecting and Removing Outliers
features = ["bonus", "salary"]
data = featureFormat(enron_data, features)

for point in data:
    bonus = point[0]
    salary = point[1]
    matplotlib.pyplot.scatter( bonus, salary )

matplotlib.pyplot.xlabel("bonus")
matplotlib.pyplot.ylabel("salary")
matplotlib.pyplot.show()


## check outlier
features = ["bonus", "salary"]
data = featureFormat(enron_data, features)

for point in data:
    bonus = point[0]
    salary = point[1]
    matplotlib.pyplot.scatter( bonus, salary )

matplotlib.pyplot.xlabel("bonus")
matplotlib.pyplot.ylabel("salary")
matplotlib.pyplot.show()

###We can see that the biggest outlier for "Bonus" feature is the total aggregation that often appears in a spreadsheet.

outliers_in_salary = []
for key in enron_data:
    val = enron_data[key]['salary']
    if val == 'NaN':
        continue
    outliers_in_salary.append((key,int(val)))

pprint(sorted(outliers_in_salary,key=lambda x:x[1],reverse=True)[:10])

##One tricky record that is not an Enron employee
print "One tricky record that is not an Enron employee:"
for key in enron_data:
    if "TRAVEL AGENCY" in key:
        print key

###As shown above, the major outlier is TOTAL. This is the total aggregation of all the records and thus, should be removed from the dataset.
###The other record THE TRAVEL AGENCY IN THE PARK is also an outlier as it is not an Enron employee. This record should be removed as well.
		
features = ["salary", "bonus"]

##Remove the outliers mentioned above
enron_data.pop('TOTAL',0)
enron_data.pop('THE TRAVEL AGENCY IN THE PARK',0)

my_dataset = copy(enron_data)
my_feature_list = copy(features_list)

data = featureFormat(enron_data, features)

##Plot the cleaned data
for point in data:
    salary = point[0]
    bonus = point[1]
    matplotlib.pyplot.scatter( salary, bonus )

matplotlib.pyplot.xlabel("salary")
matplotlib.pyplot.ylabel("bonus")
matplotlib.pyplot.show()

###We also need to check two more important features for outliers. These two features are "from_poi_to_this_person" and "from_this_person_to_poi".
features = ["from_this_person_to_poi", "from_poi_to_this_person"]
data = featureFormat(enron_data, features)


### plot the two features
for point in data:
    from_this_person_to_poi = point[0]
    from_poi_to_this_person = point[1]
    matplotlib.pyplot.scatter( from_this_person_to_poi, from_poi_to_this_person )

matplotlib.pyplot.xlabel("from_this_person_to_poi")
matplotlib.pyplot.ylabel("from_poi_to_this_person")
matplotlib.pyplot.show()

###Based on the chart above, there are a few outliers that should be further investigated.
to_poi_outliers = []
for key in enron_data:
    val = enron_data[key]['from_this_person_to_poi']
    if val == 'NaN':
        continue
    to_poi_outliers.append((key,int(val)))

pprint(sorted(to_poi_outliers,key=lambda x:x[1],reverse=True)[:10])

from_poi_outliers = []
for key in enron_data:
    val = enron_data[key]['from_poi_to_this_person']
    if val == 'NaN':
        continue
    from_poi_outliers.append((key,int(val)))

pprint(sorted(from_poi_outliers,key=lambda x:x[1],reverse=True)[:10])

###The records with the biggest values seem to be enron_employee. As such, those records need to be kept.

#Further Data Cleaning and Exploration. Loading Dataset into dataframe.
df = pandas.DataFrame.from_records(list(enron_data.values()))
persons = pandas.Series(list(enron_data.keys()))

#View of Data
print df.head()

# check data types
df.dtypes

#Check and take care of "NaN"
# Convert to numpy nan
df.replace(to_replace='NaN', value=numpy.nan, inplace=True)

# Count number of NaN's for columns
print df.isnull().sum()

# DataFrame dimeansion
print df.shape
# print df.head()

### Convert "NaN" string to Numpy NaN
df.replace(to_replace='NaN', value=numpy.nan, inplace=True)

### Count total occurence of NaN values.
print "Number of records with NaN values:"
print df.isnull().sum()

### Dataset Shape
print "\nDataset shape: "
print df.shape
### print df.head()

###Handling NaN Values
df_replace_nan = df.replace(to_replace=numpy.nan, value=0)
df_replace_nan = df.fillna(0).copy(deep=True)
df_replace_nan.columns = list(df.columns.values)

print "Number of records with NaN values:"
print df_replace_nan.isnull().sum()

print "\nOverview of df: "
print df_replace_nan.head()

df_replace_nan.describe()


##Feature Selection:
###Using Correlation Table to Explore Features
pearson = df.corr(method='pearson')

#create a list of correlation between available and the target feature (i.e. poi)
corr_with_target_feature = pearson['poi']

#drop 'poi' feature in the row because it is not the independent variable
corr_with_target_feature = corr_with_target_feature.drop(['poi'])

#sort correlation list by absolute value
corr_with_target_feature_sorted = abs(corr_with_target_feature).sort_values(ascending = False)

print "Sorted features based on their absolute correlation value with the target feature ('poi'): "

print corr_with_target_feature[corr_with_target_feature_sorted.index]


# Compute the correlation matrix
corr = df.corr()

# Generate a mask for the upper triangle
mask = np.zeros_like(corr, dtype=np.bool)
mask[np.triu_indices_from(mask)] = True

# Set up the matplotlib figure
f, ax = plt.subplots(figsize=(20, 15))

# Generate a custom diverging colormap
cmap = sns.diverging_palette(220, 10, as_cmap=True)

# Draw the heatmap with the mask and correct aspect ratio
sns.heatmap(corr, mask=mask, cmap=cmap, vmax=.3,
            square=True, xticklabels=2, yticklabels=2,
            linewidths=.5, cbar_kws={"shrink": .5}, ax=ax)

###Based on correlation value with the target feature ('poi'), the list above shows the sorted list of features, which can be our potential useful features.

###Using SKLearn SelectKBest feature selection:
def get_k_best(enron_data, features_list, k):
    """ runs scikit-learn's SelectKBest feature selection
        returns dict where keys=features, values=scores
    """
    data = featureFormat(enron_data, features_list)
    labels, features = targetFeatureSplit(data)
    
    k_best = SelectKBest(k=k)
    k_best.fit(features, labels)
    scores = k_best.scores_
    unsorted_pairs = zip(features_list[1:], scores)
    sorted_pairs = list(reversed(sorted(unsorted_pairs, key=lambda x: x[1])))
    k_best_features = dict(sorted_pairs[:k])
    print k_best_features
#     print "{0} best features: {1}\n".format(k, k_best_features.keys())
    return k_best_features

# get K-best features
target_label = 'poi'
from sklearn.feature_selection import SelectKBest
# print enron_data
num_features = 10 # N best features
best_features = get_k_best(enron_data, features_list, num_features)
# print best_features
my_feature_list = [target_label] + best_features.keys()

print "{0} selected features: {1}\n".format(len(my_feature_list) - 1, my_feature_list[1:])



#Feature Engineering
import warnings
warnings.filterwarnings('ignore')

#Here I engineered three new features:

#poi_ratio = number of messages sent to + received from poi / total sent + received messages
eng_feat1='poi_ratio'

#fraction_to_poi = number of messages sent to poi / total sent messages
eng_feat2='fraction_to_poi'

#fraction_from_poi = number of messages received from poi / total received messages
eng_feat3='fraction_from_poi'

#add the newly engineered features to my_feature_list
enron.add_poi_ratio(enron_data, my_feature_list)
enron.add_fraction_to_poi(enron_data, my_feature_list)
enron.add_fraction_from_poi(enron_data, my_feature_list)

eng_feature_list=my_feature_list 
print my_feature_list
print eng_feature_list

#Feature Scaling
#Here we rescale the feature values before the features can be used into a machine learning model
#subset the features in the eng_feature_list
data = featureFormat(enron_data, eng_feature_list)

#split the target feature from the other features
labels, features = targetFeatureSplit(data)

from sklearn import preprocessing

#scale the features with MinMaxScaler
scaler = preprocessing.MinMaxScaler()
features = scaler.fit_transform(features)

#split the data: 30% of the data as test data and 70% as training data.
features_train,features_test,labels_train,labels_test = sklearn.cross_validation.train_test_split(features,labels, test_size=0.3, random_state=52)

print labels
print features

#Iterating through various models
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import ExtraTreesClassifier
from sklearn.ensemble import AdaBoostClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.naive_bayes import GaussianNB

names = ["Nearest Neighbors", "Linear SVM", "RBF SVM", "Decision Tree",
         "Random Forest", "AdaBoost", "Naive Bayes", "Extra Trees"]

classifiers = [
    KNeighborsClassifier(3),
    SVC(kernel="linear", C=0.025),
    SVC(gamma=2, C=1),
    DecisionTreeClassifier(max_depth=5),
    RandomForestClassifier(max_depth=5, n_estimators=10, max_features=1),
    AdaBoostClassifier(),
    GaussianNB(),
    ExtraTreesClassifier()]


#iteration over various classifiers
for name, clf in zip(names, classifiers):
        clf.fit(features_train,labels_train)
        scores = clf.score(features_test,labels_test)
        print " "
        print "Classifier:"
        evaluate.evaluate_clf(clf, features, labels, num_iters=1000, test_size=0.3)
        print("Accuracy: %0.2f (+/- %0.2f)" % (scores.mean(), scores.std() * 2))
        print "====================================================================="


#Model tuning with grid_search.GridSearchCV
##Define Scoring and Cross Validation
from sklearn import grid_search
from sklearn.tree import DecisionTreeClassifier

cv = sklearn.cross_validation.StratifiedShuffleSplit(labels, n_iter=10)
def scoring(estimator, features_test, labels_test):
     labels_pred = estimator.predict(features_test)
     p = sklearn.metrics.precision_score(labels_test, labels_pred, average='micro')
     r = sklearn.metrics.recall_score(labels_test, labels_pred, average='micro')
     if p >= 0.1 and r >= 0.3:
            return sklearn.metrics.f1_score(labels_test, labels_pred, average='macro')
     return 0


#Tuning DecisionTreeClassifier
t0 = time()
parameters = {'max_depth': [1,2,3,4,5,6,8,9,10],'min_samples_split':[2,3,4,5],'min_samples_leaf':[1,2,3,4,5,6,7,8], 'criterion':('gini', 'entropy')}

dtc_clf = sklearn.tree.DecisionTreeClassifier() 
dtcclf = grid_search.GridSearchCV(dtc_clf, parameters, scoring = scoring, cv = cv)

dtcclf.fit(features, labels)
print 'best estimator:', dtcclf.best_estimator_
print 'best score:', dtcclf.best_score_
print 'Processing time:',round(time()-t0,3) ,'s'

#Validation of ClassifierClassifier validation
##DecisionTreeClassifier Validation No. 1 (StratifiedShuffleSplit, folds = 1000)
t0 = time()
dtc_best_clf = dtcclf.best_estimator_
   
test_classifier(dtc_best_clf, enron_data, eng_feature_list)

print 'Processing time:',round(time()-t0,3) ,'s'

##DecisionTreeClassifier Validation No. 2 (Randomized, partitioned trials, n=1,000)
t0 = time()
dtc_best_clf = dtcclf.best_estimator_
   
evaluate.evaluate_clf(dtc_best_clf, features, labels, num_iters=1000, test_size=0.3)
print("Accuracy: %0.2f (+/- %0.2f)" % (scores.mean(), scores.std() * 2))
print 'Processing time:',round(time()-t0,3) ,'s'

#Dump classifier
dump_classifier_and_data(dtc_best_clf, enron_data, eng_feature_list)

