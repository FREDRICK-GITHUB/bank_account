# bank_account

## Instructions for running project locally
### Ensure you have the following in your development environment:
Install python3

``` sudo apt install python3 ```

Install Flask 

``` pip install flask ```

Install Flask-Login 

``` pip install flask-login ```

Install Flask Alchemy

``` pip install flask-sqlalchemy ```

### Clone this repository to your development environment.
Navigate to the root folder, create .env file and run main.py

``` cd bank_account ```

Install dotenv package

``` pip3 install python-dotenv ```

Create .env file(in root directory) and add the following:

``` touch .env ```

``` DB_NAME = "bank_account_solution.db" ```

``` SECRET_KEY = 'ADD SECRET KEY HERE' ```

Run main.py

``` python3 main.py ```

You will get a url which will help you access the platform on a browser

``` http://127.0.0.1:5000 ```

# Web View

## Default login credentials

``` username: admin@quickmail.com    password: 1234567 ```

# Login
![login page](image.png)

# Create new user
![alt text](image-1.png)

# Create Bank Account
![alt text](image-2.png)

# View Bank Account and Transact
![alt text](image-3.png)

# Create Transaction - Deposit
![alt text](image-4.png)

# View Transaction
![alt text](image-5.png)

# View User Account Balance
![alt text](image-6.png)

# Create Transaction - Withdrawal( Exeeding amount in account)
![alt text](image-7.png)

![alt text](image-8.png)