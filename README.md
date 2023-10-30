Author - Ihor Prokopenko:
 - Email: i.prokopenko.dev@gmail.com
 - LinkedIn: https://www.linkedin.com/in/i-prokopenko/

# The Staking app

This application is designed to conveniently manage various operations related to staking, wallets, positions and user management.

## Installing:

1. Clone project from GitHub repository
    - `git clone URL`

2. Make sure You have installed Python3:
    - Open the terminal and run:
         - `python --version` - Windows
         - `python3 --version` - Unix
    - If version were not displayed, you can find the python installer [here](https://www.python.org/downloads/)
   
   ##### NOTE: that the project will not run on Python version 3.12, you must use a version lower than 3.12, preferably 3.11

3. Use the virtual environment:
    - Follow to the project dir
    - Create the venv:
         - `python -m venv myenv` - Windows
         - `python3 -m venv myenv` - Unix
    - Activate venv:
         - `myenv\Scripts\activate` - Windows
         - `source myenv/bin/activate` - Unix
4. Install the dependencies:
    - Make sure Your venv activated
    - Follow to the `project_dir` and run next commands:
         - `pip install poetry`
         - `poetry install`

## How to run the app:
- Make sure Your venv activated
- Follow to the `project_dir/src`
- Apply migrations:
     - `python manage.py migrate` - Windows
     - `python3 manage.py migrate` - Unix
- (Optional)Create an Example StakingPools:
     - `python manage.py create_example_pools` - Windows
     - `python3 manage.py create_example_pools` - Unix
- Create superuser:
     - `python manage.py createsuperuser` - Windows
     - `python3 manage.py createsuperuser` - Unix
- Run the server:
     - `python manage.py runserver` - Windows
     - `python3 manage.py runserver` - Unix
- Now you can try the app:
     - http://127.0.0.1:8000/swagger - API swagger documentation
     - http://127.0.0.1:8000/admin - Admin panel (login here via superuser credentials)

## Functionality
#### Wallet Management:
 - User creating provides a wallet creation and relate wallet to the user.
 - Users can replenish and withdraw funds from their wallets.

#### Position Management:
 - Users can create and manage positions. 
 - They can increase or decrease their positions.

#### Conditions:
 - Admins can create, delete and manage conditions.

#### Staking Pools:
 - Admins can create, delete and manage staking pools. 
 - They can also edit existing staking pools.

#### User Management:
 - Listing users
 - Viewing user details
 - Registering new users
 - Deleting users
 - Editing user profiles
 - Changing user passwords.

#### Authentication:
 - Users can log in to the system to access the application's features.
      - SessionAuthentication
      - JWTAuthentication

#### API Documentation:

 - The application provides API documentation through Swagger, which allows developers to explore and interact with the available APIs.
