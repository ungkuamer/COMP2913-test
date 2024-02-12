## Customers
[Stripe API CUstomers Docs](https://stripe.com/docs/api/customers)

- represents a customer
- create recurring charges and track payments


## Sessions
[Stripe API Session Docs](https://stripe.com/docs/api/checkout/sessions)

- session represent customer's session as they pay
- create a new session for every attempt of payment
    - create session and redirect url

### Session object

- id : unique id
- amount_total : change this when different button is clicked
- client_reference_id : user id from user table - allow for linking with user
- customer : (TO BE ADDED)
- customer_email : email from user table
- mode: subscription : use stripe billing for fixed subscriptions
- payment_status : payment status of current session (?) - somehow check if the payment is successful
- line_items.data : dictionary containing id
- status : status of session
- invoice_creation : {'enable'}
- url : redirect to this url for checkout