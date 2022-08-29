# 10. MLOps in Azure

MLOps is a set of practices to manage the full ML Lifecycle. The ML Lifecycle consists of different stages that a ML project must go through in order to fulfill the project‘s goal

![image](https://user-images.githubusercontent.com/54147355/187204015-1c740955-54d3-4536-9f06-081fc6506cf7.png)

Productionizing other software development projects is done within the DevOps framework. However productionizing ML models, faces new challenges:

- Experimental nature of ML models: we run several algorithms, with different hyperparameters and different feature engineering methods --> keep track of different experiments and runs

- Reproducibility: it could often happen that when we re-run a ML model, we get different results! This could happen because of changes in code, data, env --> need a robust implementation

- Retraining: ML model training on our local Machine is a one-time activity. However, in production, we would like to add the new data by the end-user to retrain our model, several times to improve its performance continuously.  

- Automation: we would like all these goals to be achieved in an automated fashion --> multi-step pipelines to automatically retrain and deploy a model

In this session of the training, we explore different aspects of MLOps including

- Introduction
- ML life cycle
- DevOps
- MLOps
- MLOps in Azure

