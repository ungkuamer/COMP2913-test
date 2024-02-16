
## Features
[] implement stripe payment
    - create session
    - add to payment table
    - add to subscription table
      - userid, startdate, enddate
    - update user isSubscribe
    

## Design
[] change user/file table to pages if too long
    - limit database query to 'x' and change to the next 'x'
      if button is clicked

## Code
[] add docstring - IN PROGRESS
[] refactor code

## Payment
[ ] check for user subscription on login
[ ] if user is subscribe disable payment function - pull status from stripe api