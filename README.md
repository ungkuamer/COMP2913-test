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

<br>

## Requirements and Backlog
[Backlog File](./backlog.md)

### High Priority

#### Functional

- [x] User accounts and login
- [x] User upload and storage of GPS route data (GPX)
    - [x] Link uploaded file with the user
- [x] Display GPS route on map
    - [x] Add interactive map to page
    - [x] Get coordinate array and pass to JS function
- [x] Allow owner display user data
    - [x] Display registered user
    - [x] Display uploaded files - on view create user page
- [x] Accept payment - ON HOLD
    - [ ] Add user metadata to payment
    - [ ] Change user 'isSubscribed' status
- [ ] Allow owner display future revenue data - weekly level upto 1 year

- [ ] Allow user to cancel membership

#### Non Functional

- [x] Display pricing info

- [ ] Proper data security

- [ ] Accessible interface

### Low Priority

#### Functional

- [ ] Display multiple user routes on the same map

- [ ] Allow user to download GPS data

- [ ] Allow user to change payment tariffs (ex. monthly plan to year plan)

- [ ] Add friend function

- [ ] Allow friend groups to view shared data on a map

### Non Functional

- [x] Responsive UI

- [ ] Informative landing page for new customers

<br>

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
  