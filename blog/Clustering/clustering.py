from sklearn.cluster import DBSCAN
from sklearn.cluster import KMeans
from sklearn.mixture import GaussianMixture
import matplotlib.pyplot as plt
from matplotlib import cm
import sklearn as sk
import pandas as pd
import numpy as np
import os

os.chdir('/Users/stevenhurwitt/Documents/Blog/Clustering')

##### K means #####

#read in iris data, make data matrix
iris = pd.read_csv('iris.csv', sep = ",", header = 0)
iris.head()
X = iris.loc[:,['Sepal.Length', 'Sepal.Width', 'Petal.Length', 'Petal.Width']]

#k means clustering
kmeans = KMeans(n_clusters=3, init = 'random', n_init = 25,
                precompute_distances = True, max_iter = 500, tol = .00001).fit(X)

#save clusters, turn species into numbers
clusters = pd.DataFrame(kmeans.labels_)
species = pd.DataFrame(iris.loc[:,['Species']])
replace_map = {'Species': {'setosa':0, 'versicolor':1, 'virginica':2}}
species.replace(replace_map, inplace = True)

#plot petal length vs width based on cluster
fig = plt.figure()
fig.suptitle("Petal Length vs. Width (K means)",fontsize=14)
ax = fig.add_subplot(111)
ax.set_xlabel("Petal Length",fontsize=10)
ax.set_ylabel("Petal Width",fontsize=12)

pl = iris.loc[:,['Petal.Length']]
pw = iris.loc[:,['Petal.Width']]

ax.scatter(pl,pw,s=100,c=clusters, marker = '.', cmap = cm.jet);

plt.show()

#plot petal length vs width based on species
fig = plt.figure()
fig.suptitle("Petal Length vs. Width (Species)",fontsize=14)
ax = fig.add_subplot(111)
ax.set_xlabel("Petal Length",fontsize=10)
ax.set_ylabel("Petal Width",fontsize=12)

pl = iris.loc[:,['Petal.Length']]
pw = iris.loc[:,['Petal.Width']]

ax.scatter(pl,pw,s=100,c=species, marker = '.', cmap = cm.jet);

plt.show()

### GMM ####

#split data into training and test set
train_ind = np.random.choice(150, 120, replace = False)
X_tr = np.array(X)[train_ind]
X_test = np.array(X)[[i for i in range(150) if i not in train_ind]]

gmm = GaussianMixture(n_components=3).fit(X_tr)
gmm.predict(X_test)

groups = pd.DataFrame(gmm.predict(X))

fig = plt.figure()
fig.suptitle("Petal Length vs. Width (GMM)",fontsize=14)
ax = fig.add_subplot(111)
ax.set_xlabel("Petal Length",fontsize=10)
ax.set_ylabel("Petal Width",fontsize=12)

pl = iris.loc[:,['Petal.Length']]
pw = iris.loc[:,['Petal.Width']]

ax.scatter(pl,pw,s=100,c=groups, marker = '.', cmap = cm.jet);

plt.show()

#### DBSCAN ####
db_clusters = DBSCAN(eps = .4, min_samples=5).fit(X)
dbc = pd.DataFrame(db_clusters.labels_+1)

fig = plt.figure()
fig.suptitle("Petal Length vs. Width (DBSCAN)",fontsize=14)
ax = fig.add_subplot(111)
ax.set_xlabel("Petal Length",fontsize=10)
ax.set_ylabel("Petal Width",fontsize=12)

pl = iris.loc[:,['Petal.Length']]
pw = iris.loc[:,['Petal.Width']]

ax.scatter(pl,pw,s=100,c=dbc, marker = '.', cmap = cm.jet);

plt.show()
