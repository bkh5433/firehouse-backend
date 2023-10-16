# Firehouse Backend

## Overview

The Firehouse Backend is an automated system designed to process incident-related emails, extract relevant information, and store this data in a Firebase database. The system specifically targets emails labeled as "MCDPS CAD MESSAGE," which are expected to follow a specific format for the backend to parse and process them correctly.

## How It Works

### 1. Email Retrieval

The system connects to an email server via IMAP, where it checks for new, unseen emails with the subject "MCDPS CAD MESSAGE." This process is initiated through a Flask endpoint, making it possible to trigger the system remotely or at regular intervals, depending on the deployment setup.

### 2. Email Processing

Once a relevant email is retrieved, the system parses its content. It extracts key information such as:

- Incident number
- Date and time the incident was received
- Call source
- Incident closed status
- First unit on the scene
- Time in service
- Code and description
- Address of the incident
- Units dispatched
- Event comments

The parsing is done by dedicated modules within the system, designed to handle the specific format of "MCDPS CAD MESSAGE" emails.

### 3. Data Storage

After successful extraction, the system structures the parsed data into a predefined format and stores it in a Firebase database. The Firebase connection is handled by a utility within the system, ensuring data consistency and security.

### 4. Error Handling and Logging

The system contains basic error handling for common issues that might occur during the email retrieval and parsing process. Errors and system logs are printed out, providing a straightforward way to monitor the system's status.

## System Flow

Here's a simplified flow of the system:

1. A request is made to the Flask server (usually via the `/check-emails` endpoint).
2. The server initiates the email checking process.
3. New emails with the specified subject are fetched and processed one by one.
4. Relevant information from each email is extracted and structured.
5. The structured data is then stored in the Firebase database.
6. The system logs the outcome of the operation and waits for the next trigger.

## Conclusion

The Firehouse Backend serves as an automated intermediary, efficiently processing critical incident reports without requiring manual intervention. Its design ensures that all relevant incident data is promptly and securely stored, making it readily available for any subsequent processing or analysis needs.

