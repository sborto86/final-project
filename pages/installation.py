import streamlit as st

st.title("How to install and deploy this applictaion")

st.markdown('''
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
            ''')