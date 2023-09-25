# Library-service-Mate

Library service API for managing with DRF.
You can manage  with users, books, borrowings, payments.

# Installing
You can use this commands to install project on you own localhost.

* Python 3 should be installed. Docker should be installed.
```shell
git clone https://github.com/Bloodviel/library-service.git
cd library_service
python -m venv venv
venv\Scripts\activate (on Windows)
source venv/bin/activate (on macOS)
pip install -r requirements.txt
python manage.py migrate
```
* Create .env file in base directory
* Fill .env file with data
```shell
BOT_TOKEN=BOT_TOEN
CHAT_ID=TELEGRAM_CHAT_ID
STRIPE_SECRET_KEY=STRIPE_SECRET_KEY
```
* Make migrations
* Use "python manage.py runserver" to start

# To use authenticate system

* /api/users - to create user
* /api/users/token - to get token

# Features
1. JSON Web Token authenticated  
2. Documentation /api/doc/swagger/
3. Creating users, books, borrowings, payments
4. Implemented borrowing system
5. Implemented filtering for the Borrowings List endpoint
6. Implemented return borrowing functionality
7. Implemented notification service when you borrow book and make successful payment
