
**Installation for Windows:**
- install PostgreSQL and run it on localhost
- create db 'hotel', add chemas and data:
- run `createdb -U postgres hotel`
- run `psql -U postgres hotel < setup.sql`
- run `psql -U postgres hotel < data.sql`
- install python 3.* and pip
- go to the root of this project
- run `pip install virtualenv`
- run `virtualenv venv`
- run `venv\Scripts\activate.bat`
- run `pip install -r requirements`
    
**To launch the web-server:**
- run `python run.py`
- open `http://localhost/`
