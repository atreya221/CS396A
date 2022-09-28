# CS396A

## Instructions for setting up virtual environment

1. Activate an existing conda environment (eg. base) using the command 
    ```
    conda activate base
    ```

2. Navigate to the project home directory and create a new python virtual environment `cs396env` using the command 
    ```
    python -m venv cs396env
    ```

3. Deactivate the conda environment using the command
    ```
    conda deactivate
    ```

4. Activate the virtual environment `cs396env` using the command
    ```
    source ./cs396env/bin/activate
    ```

5. Run the following commands to setup the environment and install required packages
    ```
    pip install --upgrade pip setuptools wheel
    pip install -r requirements.txt
    ```