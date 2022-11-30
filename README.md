# A Simple Keyword Research Tool

![Search Toool](./img/seo.png)

## Table of contents

1. <a href="#section-1">Background</a>
2. <a href="#section-2">About this repository</a>
3. <a href="#section-3">Objectives</a>
4. <a href="#section-4">Installation and requirements</a>

<h2 id="section-1">Background</h2>

To design a good SEO strategy, access to big amounts of data is essential. However, access to quality data is getting harder and harder.

At the present moment, SEO tools available are expensive or offer low-quality data.

<h2 id="section-2">About this repository</h2>

This repository was created as a final project for a Data Analyst Bootcamp at Ironhack.

<h2 id="section-3">Objectives</h2>

**1. Proof of concept**: 

Design a minimum working application for SEO keyword research with a limited time (around a week) and 0 budget.

**2. Easy to deploy application**: 

Design an application that can be deployed online by anyone with only few commands.

**3. Prove that news can be a good predictor of search behavior abnormalities**: 

The search behavior of the users is usually predictable and easy to forecast. However, sometimes there are sudden spikes in searches that affect the quality of the prediction models.

This project pretends to show that we can combine, data extracted from the news and the historical behavior of the users, to improve the quality of the prediction models.

<h2 id="section-4">Installation and requirements</h2>

To deploy this application you should have to meet some minimum requirements.

<h3>Requirements</h3>

1. A server with MySQL (or similar) installed and about 100Mb available.
2. The Guardian API access key. Can be  [easily obtained here](https://open-platform.theguardian.com/access/) for free.
3. The New York Times API Key. Can be  [easily obtained here](https://developer.nytimes.com/apis) for free.

<h3>Installation</h3>

1. Open the terminal and clone the repository

```console
git clone https://github.com/sborto86/final-project
```

2. Create a .streamlit directory and an inside a file called secrets.toml

```console
mkdir .streamlit
touch ./.streamlit/secrets.toml
```

3. Open the secrets.toml file and add the necessary keys for the application to work in the following format

```
THE_GUARDIAN = "<The Guardian API key>"
NYT = "<The New York Times API key>"
SQLHOST = "<SQL server host address>"
SQLUSER = "<SQL database user name>"
SQLPW = "<SQL database pasword>"
SQLPORT = "<SQL port>"
SQLDB = "<name of the SQL database>"
```

4. Create the standards that are going to be used to estimate google search volume (it can take around 15 minutes). This should create also the SQL database automatically. In the console execute the following python script. 
```console
python ./db/standards_db.py
```

5. Create the database and the New York Times archive (it can take around 10 minutes). In the console execute the following python script:

```console
python nyarchive.py
```

6. Now that everything is ready the application can be tested locally.  In the console execute streamlit:

```console
 streamlit run main.py
```

7. Finally to deploy the application online, just follow the [instructions here](https://docs.streamlit.io/streamlit-cloud/get-started/deploy-an-app)



