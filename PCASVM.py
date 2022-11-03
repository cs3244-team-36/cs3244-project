import numpy as np
import scipy
import matplotlib.pyplot as plt
import pandas as pd
import random

import sklearn
from sklearn.decomposition import PCA
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay
from sklearn.svm import SVC
from sklearn import metrics
from sklearn.utils import shuffle
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import KFold
from sklearn.model_selection import GridSearchCV
from sklearn.neighbors import KNeighborsClassifier

#Loading of data, split into X(features) and Y(labels)
train = pd.read_csv('/Users/kohlongyang/Desktop/fashion-mnist_train.csv')
test = pd.read_csv('/Users/kohlongyang/Desktop/fashion-mnist_test.csv')

random.seed(3244)
valid = train.sample(frac=0.20)
train = train.drop(valid.index)
#print(train.shape)
#print(valid.head(3))

Ytrain = train.iloc[:, 0]
Yvalid = valid.iloc[:, 0]
Ytest = test.iloc[:, 0]

Xtrain = train.loc[:,train.columns!='label']
Xvalid = valid.loc[:, valid.columns!='label']
Xtest = test.loc[:, test.columns!='label']

Xtrain = np.divide(Xtrain, 255)
Xvalid = np.divide(Xvalid, 255)
Xtest = np.divide(Xtest, 255)

#first scree plot shows that the number of optimum comps is within the range of 1 to 30
covar_matrix = PCA(n_components=784)
covar_matrix.fit(Xtrain)
covar_matrix_values = np.arange(covar_matrix.n_components_)+1
plt.style.context('seaborn-whitegrid')
plt.plot(covar_matrix_values,covar_matrix.explained_variance_ratio_,'o-',linewidth=2,color='blue')
plt.title('Scree Plot')
plt.xlabel('PC')
plt.ylabel('Variance Explained')

#reduce the dimensions further and double confirm
covar_matrix = PCA(n_components=30)
covar_matrix.fit(Xtrain)
covar_matrix_values = np.arange(covar_matrix.n_components_)+1
plt.style.context('seaborn-whitegrid')
plt.plot(covar_matrix_values,covar_matrix.explained_variance_ratio_,'o-',linewidth=2,color='blue')
plt.title('Scree Plot')
plt.xlabel('PC')
plt.ylabel('Variance Explained')
#variance explained gets stagnant after 15

#a for loop to see where the accuracy starts to get stagnant/insignificant increase in accuracy
n_components = np.arange(1,31) 
for n in n_components: 
    pca = PCA(n_components=n, random_state=42)
    Xtrainpca = pca.fit_transform(Xtrain)
    Xvalidpca = pca.transform(Xvalid)
    Xtestpca = pca.transform(Xtest)

#Using GSCV to find best k
    knn = KNeighborsClassifier()

#create a dictionary of all values we want to test for n_neighbors
    param_range = np.arange(1, 10)
    param_grid = {'n_neighbors': param_range}

#use gridsearch to test all values for n_neighbors
    knn_gscv = GridSearchCV(knn, param_grid)

#fit model to data
    gs = knn_gscv.fit(Xtrainpca, Ytrain)

#get best performing models
    print("best accuracy= ", gs.best_score_)
    print("best k= ", gs.best_params_)
# best accuracy=  0.8363125, at n_components = 16
# best k=  {'n_neighbors': 6}

#finding out best C for k=6
penalties = np.logspace(-2,3, num=10)
#using k=6
mcv_scores = []
for C in penalties:
    curr_svm = SVC(kernel='rbf', C=C)
    fold = KFold(n_splits=6, random_state=1, shuffle=True)
    # Cross validation 6-Fold scores        
    mean_crossval = np.mean(cross_val_score(curr_svm, Xtrainpca, Ytrain, cv=fold))
    mcv_scores.append(mean_crossval)
    print("On C=", C, "\tMCV=", mean_crossval)
# highest MCV of 88.67% when C = 21.54 and k = 6


SVM = SVC(kernel = "rbf", C = 21.54, gamma="auto")
# #https://www.geeksforgeeks.org/radial-basis-function-kernel-machine-learning/
# #use radial basis function to help "draw" the decision boundary
SVM.fit(Xtrainpca, Ytrain)
Y_predict = SVM.predict(Xtrainpca)
train_acc = metrics.accuracy_score(Ytrain,Y_predict)
#0.9575625
Y_validpredict = SVM.predict(Xvalidpca)
valid_acc = metrics.accuracy_score(Yvalid,Y_validpredict)
#0.88508

