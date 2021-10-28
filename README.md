# StockWatch
A web service which provides the ability to send emails to the user when stock prices change according to configuration signaling a "buy" or "sell" opportunity.

# Environment variables
If in development, the environment variable READ_ENV_FILE must be set to True to correctly set the project's environment variables.
In production, those variables should be set individually in the host server. Consult the '.template.env' file to know which variables must be set.


# Execution Instructions

## In Development:

- The server is executed with the command:
'''python3 manage.py runserver'''

- The task scheduler must be executed in another process/terminal:
'''python3 manage.py qcluster'''

- The email backend is set to send to this python debugging server, that must be executed in another terminal:
'''python -m smtpd -n -c DebuggingServer localhost:1025'''