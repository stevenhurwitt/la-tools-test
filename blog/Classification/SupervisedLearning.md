
## Supervised Learning

Supervised learning is an incredibly useful aspect of machine learning. The main idea is to predict the value of a *response variable* from a set of *explanatory variables* . This is accomplished by using a wide range of algorithms on training data, which can then be validated on test data by computing the accuracy of the trained model. 

The types of supervised learning problems can be grouped into three main categories:

1. *Regression*
2. *Classification*
3. *Clustering*

We can use libraries in Python such as <a rel="nofollow" target="_blank" href="http://www.numpy.org/">NumPy</a> for linear algebra and <a rel="nofollow" target="_blank" href="http://scikit-learn.org/stable/">scikit-learn</a> for machine learning models. These can be installed and imported into Python as follows:

```sh
python3 -m pip install numpy
python3 -m pip install sklearn
```


```python
import numpy as np
import sklearn as sk
```

### 1. Regression

Regression is an incredibly important subject in statistics and machine learning. The main idea is that we can predict the value of a continuous response variable from explanatory variables when the data exhibit a *linear* relationship. 

If our response variable is not continuous, i.e. if it's a count, binary variable, group category, time correlated value then we cannot use *linear regression*. Instead we may be able to use a *generalized linear model*, of which linear regression is one specific case.

#### Generalized Linear Models

For generalized linear models (GLM's), we must have a reponse variable $\vec{y}$, and an *n x p* data matrix $X$ with n observations and p variables. GLM's will give us a vector of *p* coefficients $\hat{\beta}$ such that our predicted value of $y$ is: $$\hat{y} = X \hat{\beta}.$$

To find $\hat{\beta}$, we choose $\beta = \hat{\beta}$ such that $$\sum_{i = 1}^n {(\vec{y} - \hat{y})}^2 = \sum_{i = 1}^n {(\vec{y} - X \beta)}^2$$ is minimized. For linear regression, this results in the solution: $$\hat{\beta} = {(X^T X)}^{-1} X^T y$$
$$\Rightarrow \hat{y} = X \hat{\beta} = X {(X^T X)}^{-1} X^T y.$$

For GLM's, we have a link function based on the mean such that: $$g(\mu) = X \hat{\beta}.$$

Link functions and their inverse *mean functions* of common distributions are given below:

| Family        | Link $g(\mu)$                              | Mean  |
| ------------- |:------------------------------------------:|:-----:|
| Normal        |$$X \hat{\beta} = \mu$$           | $$\mu = X \hat{\beta}$$   |
| Poisson       |$$X \hat{\beta} = \ln{\mu}$$      | $$\mu = \textit{e}^{X \hat{\beta}}$$|
| Binomial      |$$X\hat{\beta}=\ln{\frac{\mu}{1-\mu}}$$|$$\text{(same as Bernoulli)}$$|
| Bernoulli |$$\text{(same as Binomial)}$$|$$\mu = \frac{1}{1+\textit{e}^{-X\hat{\beta}}}$$|

A standard linear regression is a special case of GLM's that uses the *Normal* distribution/family.

To run a linear regression, we will use data based on 


```python

```

### Classification

-CART, random forest, basic neural nets, etc


```python

```

### Clustering

-k means, LDA/QDA, DBSCAN, etc


```python

```


```python

```


```python

```
