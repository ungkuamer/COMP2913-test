# COMP2913-Flask-Test

## Installation
### 1. Clone the repository
`git clone git@github.com:ungkuamer/comp2913-test.git`

`cd comp2913-test`
### 2. Create virtual environment and install dependencies

__Create new virtual environment__

`python3 -m venv .venv`

__Activate the environment__

Windows : `.venv\Scripts\activate`

MacOS/Linux : `source .venv/bin/activate`

__Install dependencies__

`pip install -r requirements.txt`

### 3. Run the server

`flask server.py`

Open browser and go to:

`http:://127.0.0.1:5000`

## Web Stack and Tech

### Web Framework
- Flask

### Frontend and Design
- Jinja
- Tailwind CSS (served from cdn)

### Database, Storage and User Authentication
- Supabase
- PostgressSQL (hosted on Supabase) 

### Payment
- Stripe API
  