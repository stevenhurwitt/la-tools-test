
## Classification

Classification is a large domain in the field of statistics and machine learning. Generally, classification can be broken down into two areas: 

1. **Binary classification**, where we wish to group an outcome into one of two groups.

2. **Multi-class classification**, where we wish to group an outcome into one of multiple (more than two) groups.

In this post, the main focus will be on using a variety of classification algorithms across both of these domains, less emphasis will be placed on the theory behind them.

We can use libraries in Python such as <a rel="nofollow" target="_blank" href="http://scikit-learn.org/stable/">scikit-learn</a> for machine learning models, and <a rel="nofollow" target="_blank" href="https://pandas.pydata.org/">Pandas</a> to import data as data frames. These can be installed and imported into Python as follows:

```sh
python3 -m pip install sklearn
python3 -m pip install pandas
```


```python
import sklearn as sk
import pandas as pd
```

### Binary Classification

For binary classification, we are interested in classifying data into one of two *binary* groups - these are usually represented as 0's and 1's in our data. 

We will look at data regarding coronary heart disease (chd) in South Africa. The goal is to use different variables such as *tobacco usage*, *family history*, *ldl cholestrol levels*, *alcohol usage*, *obesity* and more. A full description is available in the data section of the <a rel="nofollow" target="_blank" href="https://web.stanford.edu/~hastie/ElemStatLearn/">Elements of Statistical Learning</a> website. A sample of the data is shown below.

The code below reads the data into a pandas data frame, and then separates the data frame into a y vector of the response and an X matrix of explanatory variables.


```python
import pandas as pd
import os

os.chdir('/Users/stevenhurwitt/Documents/Blog/Classification')
heart = pd.read_csv('SAHeart.csv', sep=',',header=0)
heart.head()

y = heart.iloc[:,9]
X = heart.iloc[:,:9]
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>sbp</th>
      <th>tobacco</th>
      <th>ldl</th>
      <th>adiposity</th>
      <th>famhist</th>
      <th>typea</th>
      <th>obesity</th>
      <th>alcohol</th>
      <th>age</th>
      <th>chd</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>160</td>
      <td>12.00</td>
      <td>5.73</td>
      <td>23.11</td>
      <td>1</td>
      <td>49</td>
      <td>25.30</td>
      <td>97.20</td>
      <td>52</td>
      <td>1</td>
    </tr>
    <tr>
      <th>1</th>
      <td>144</td>
      <td>0.01</td>
      <td>4.41</td>
      <td>28.61</td>
      <td>0</td>
      <td>55</td>
      <td>28.87</td>
      <td>2.06</td>
      <td>63</td>
      <td>1</td>
    </tr>
    <tr>
      <th>2</th>
      <td>118</td>
      <td>0.08</td>
      <td>3.48</td>
      <td>32.28</td>
      <td>1</td>
      <td>52</td>
      <td>29.14</td>
      <td>3.81</td>
      <td>46</td>
      <td>0</td>
    </tr>
    <tr>
      <th>3</th>
      <td>170</td>
      <td>7.50</td>
      <td>6.41</td>
      <td>38.03</td>
      <td>1</td>
      <td>51</td>
      <td>31.99</td>
      <td>24.26</td>
      <td>58</td>
      <td>1</td>
    </tr>
    <tr>
      <th>4</th>
      <td>134</td>
      <td>13.60</td>
      <td>3.50</td>
      <td>27.78</td>
      <td>1</td>
      <td>60</td>
      <td>25.99</td>
      <td>57.34</td>
      <td>49</td>
      <td>1</td>
    </tr>
  </tbody>
</table>
</div>



#### Logistic Regression

<a rel="nofollow" target="_blank" href="https://en.wikipedia.org/wiki/Logistic_regression">Logistic Regression </a> is a type of Generalized Linear Model (GLM) that uses logistic function to model a binary variable based on any kind of independent variables.

To fit a binary logistic regression with *sklearn*, we use the <a rel="nofollow" target="_blank" href="https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.LogisticRegression.htmlLogisticRegression">LogisticRegression module</a> with multi_class set to *'ovr'* and fit X and y. We can then use the *predict* class to predict probabilities of new data, as well as the *score* class to get the mean prediction accuracy.


```python
import sklearn as sk
from sklearn.linear_model import LogisticRegression
import pandas as pd
import os

os.chdir('/Users/stevenhurwitt/Documents/Blog/Classification')
heart = pd.read_csv('SAHeart.csv', sep=',',header=0)
heart.head()

y = heart.iloc[:,9]
X = heart.iloc[:,:9]

LR =  LogisticRegression(random_state=0, solver='lbfgs', multi_class='ovr').fit(X, y)
LR.predict(X.iloc[460:,:])
round(LR.score(X,y), 4)
```




    array([1, 1])



#### Support Vector Machines

<a rel="nofollow" target="_blank" href="https://scikit-learn.org/stable/modules/svm.html">Support Vector Machines (SVMs) </a> are a type of classification algorithm that are more flexible - they can do linear classification, but can use other nonlinear *basis functions*. The following example uses a linear classifier to fit a hyperplane that separates the data into two classes.


```python
import sklearn as sk
from sklearn import svm
import pandas as pd
import os

os.chdir('/Users/stevenhurwitt/Documents/Blog/Classification')
heart = pd.read_csv('SAHeart.csv', sep=',',header=0)

y = heart.iloc[:,9]
X = heart.iloc[:,:9]

SVM = svm.LinearSVC()
SVM.fit(X, y)
SVM.predict(X.iloc[460:,:])
round(SVM.score(X,y), 4)
```




    array([0, 1])



#### Random Forests

<a rel="nofollow" target="_blank" href="https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.RandomForestClassifier.html">Random Forests </a> are an ensemble learning method that fit multiple <a rel="nofollow" target="_blank" href="https://en.wikipedia.org/wiki/Decision_tree">Decision Trees </a> on subsets of the data and average the results. We can again fit them using *sklearn*, and use them to predict outcomes, as well as get mean prediction accuracy.


```python
import sklearn as sk
from sklearn.ensemble import RandomForestClassifier

RF = RandomForestClassifier(n_estimators=100, max_depth=2, random_state=0)
RF.fit(X,y)
RF.predict(X.iloc[460:,:])
round(RF.score(X,y), 4)
```




    0.7338



#### Neural Networks

<a rel="nofollow" target="_blank" href="https://en.wikipedia.org/wiki/Neural_network">Neural Networks </a> are a machine learning algorithm that involves fitting many *hidden layers* used to represent neurons that are connected with synaptic *activation functions*. These essentially use a very simplified model of the brain to model and predict data.

We use *sklearn* for consistency in this post, however libraries such as <a rel="nofollow" target="_blank" href="https://www.tensorflow.org/ "> Tensorflow </a> and <a rel="nofollow" target="_blank" href="https://keras.io/ "> Keras </a> are more suited to fitting and customizing neural networks, of which there are a few varieties used for different purposes.


```python
import sklearn as sk
from sklearn.neural_network import MLPClassifier

NN = MLPClassifier(solver='lbfgs', alpha=1e-5, hidden_layer_sizes=(5, 2), random_state=1)
NN.fit(X, y)
NN.predict(X.iloc[460:,:])
round(NN.score(X,y), 4)
```




    0.6537



### Multi-class Classification

While binary classification alone is incredibly useful, there are times when we would like to model and predict data that has more than two classes. Many of the same algorithms can be used with slight modifications.

Additionally, it is common to split data into *training* and *test* sets. This means we use a certain portion of the data to fit the model (the training set), and save the remaining portion of it to evaluate to the predictive accuracy of the fitted model (the test set).

To explore both multi-class classification, as well as training/test data, we will look at another dataset from <a rel="nofollow" target="_blank" href="https://web.stanford.edu/~hastie/ElemStatLearn/">Elements of Statistical Learning</a>: data used to determine which one of eleven vowel sounds were spoken.


```python
import pandas as pd

vowel_train = pd.read_csv('vowel.train.csv', sep=',',header=0)
vowel_test = pd.read_csv('vowel.test.csv', sep=',',header=0)

vowel_train.head()

y_tr = vowel_train.iloc[:,0]
X_tr = vowel_train.iloc[:,1:]

y_test = vowel_test.iloc[:,0]
X_test = vowel_test.iloc[:,1:]
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>y</th>
      <th>x.1</th>
      <th>x.2</th>
      <th>x.3</th>
      <th>x.4</th>
      <th>x.5</th>
      <th>x.6</th>
      <th>x.7</th>
      <th>x.8</th>
      <th>x.9</th>
      <th>x.10</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>1</td>
      <td>-3.639</td>
      <td>0.418</td>
      <td>-0.670</td>
      <td>1.779</td>
      <td>-0.168</td>
      <td>1.627</td>
      <td>-0.388</td>
      <td>0.529</td>
      <td>-0.874</td>
      <td>-0.814</td>
    </tr>
    <tr>
      <th>1</th>
      <td>2</td>
      <td>-3.327</td>
      <td>0.496</td>
      <td>-0.694</td>
      <td>1.365</td>
      <td>-0.265</td>
      <td>1.933</td>
      <td>-0.363</td>
      <td>0.510</td>
      <td>-0.621</td>
      <td>-0.488</td>
    </tr>
    <tr>
      <th>2</th>
      <td>3</td>
      <td>-2.120</td>
      <td>0.894</td>
      <td>-1.576</td>
      <td>0.147</td>
      <td>-0.707</td>
      <td>1.559</td>
      <td>-0.579</td>
      <td>0.676</td>
      <td>-0.809</td>
      <td>-0.049</td>
    </tr>
    <tr>
      <th>3</th>
      <td>4</td>
      <td>-2.287</td>
      <td>1.809</td>
      <td>-1.498</td>
      <td>1.012</td>
      <td>-1.053</td>
      <td>1.060</td>
      <td>-0.567</td>
      <td>0.235</td>
      <td>-0.091</td>
      <td>-0.795</td>
    </tr>
    <tr>
      <th>4</th>
      <td>5</td>
      <td>-2.598</td>
      <td>1.938</td>
      <td>-0.846</td>
      <td>1.062</td>
      <td>-1.633</td>
      <td>0.764</td>
      <td>0.394</td>
      <td>-0.150</td>
      <td>0.277</td>
      <td>-0.396</td>
    </tr>
  </tbody>
</table>
</div>



We will now fit models and test them as is normally done in statistics/machine learning: by training them on the training set and evaluating them on the test set.

Additionally, since this is multi-class classification, some arguments will have to be changed within each algorithm.


```python
import pandas as pd
import sklearn as sk
from sklearn.linear_model import LogisticRegression
from sklearn import svm
from sklearn.ensemble import RandomForestClassifier
from sklearn.neural_network import MLPClassifier

vowel_train = pd.read_csv('vowel.train.csv', sep=',',header=0)
vowel_test = pd.read_csv('vowel.test.csv', sep=',',header=0)

y_tr = vowel_train.iloc[:,0]
X_tr = vowel_train.iloc[:,1:]

y_test = vowel_test.iloc[:,0]
X_test = vowel_test.iloc[:,1:]

LR =  LogisticRegression(random_state=0, solver='lbfgs', multi_class='multinomial').fit(X_tr, y_tr)
LR.predict(X_test)
round(LR.score(X_test,y_test), 4)

SVM = svm.SVC(decision_function_shape="ovo").fit(X_tr, y_tr)
SVM.predict(X_test)
round(SVM.score(X_test, y_test), 4)

RF = RandomForestClassifier(n_estimators=1000, max_depth=10, random_state=0).fit(X_tr, y_tr)
RF.predict(X_test)
round(RF.score(X_test, y_test), 4)

NN = MLPClassifier(solver='lbfgs', alpha=1e-5, hidden_layer_sizes=(150, 10), random_state=1).fit(X_tr, y_tr)
NN.predict(X_test)
round(NN.score(X_test, y_test), 4)
```




    0.5455



Although the implementations of these models were rather naive (in practice there are a variety of parameters that can and should be varied for each model), we can still compare the predictive accuracy across the models. This will tell us which one is the most accurate for this specific training and test dataset.

<!DOCTYPE html>
<html>
<head>
<style>
table {
    font-family: arial, sans-serif;
    border-collapse: collapse;
    width: 100%;
}

td, th {
    border: 1px solid #dddddd;
    text-align: left;
    padding: 8px;
}

tr:nth-child(even) {
    background-color: #dddddd;
}
</style>
</head>
<body>


<table>
  <tr>
    <th>Model</th>
    <th>Predictive Accuracy</th>
  </tr>
  <tr>
    <td>Logistic Regression</td>
    <td>46.1%</td>
  </tr>
  <tr>
    <td>Support Vector Machine</td>
    <td>64.07%</td>
  </tr>
  <tr>
    <td>Random Forest</td>
    <td>57.58%</td>
  </tr>
  <tr>
    <td>Neural Network</td>
    <td>54.55%</td>
  </tr>
</table>

</body>
</html>

This shows us that for the vowel data, an SVM using the default radial basis function was the most accurate.

### Conclusion

To summarize this post, we began by exploring the simplest form of classification: binary. This helped us to model data where our response could take one of two states. We then moved further into multi-class classification, when the response variable can take any number of states. 

We also saw how to fit and evaluate models with training and test sets. Furthermore, we could explore additional ways to refine model fitting among various algorithms.
