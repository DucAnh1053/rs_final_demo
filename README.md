# Project Setup Guide

## Step 1: Clone the Repository
First, you need to clone the repository to your local machine. Open a terminal and run the following command:

```bash
git clone https://github.com/DucAnh1053/rs_final_demo
```

## Step 2: Navigate to the Project Directory
Change your current directory to the project directory:

```bash
cd rs_final_demo
```

## Step 3: Create a Virtual Environment (Optional)
It is recommended to create a virtual environment to manage your dependencies. You can create a virtual environment with the following command:

```bash
python -m venv env
```

Activate the virtual environment:

- On Windows:

    ```bash
    .\env\Scripts\activate
    ```

- On macOS/Linux:

    ```bash
    source env/bin/activate
    ```

## Step 4: Install Dependencies
Install the required libraries specified in the requirements.txt file by running:

```bash
pip install -r requirements.txt
```

## Step 5: Run the Streamlit Application
Finally, to run the Streamlit application, use the following command:

```bash
streamlit run main.py
```