from modules import email_processingv2 as email_parser
from firebase_utils import firebase_handler as firebase
from flask import jsonify
import traceback
import imaplib
import email
import email.utils


# def check_emails():
#     try:
#         import imaplib
#         import email
#
#         # Fetching credentials from environment variables (placeholders for now)
#         # EMAIL = os.environ.get('FIREHOUSE_EMAIL', 'your_email_here')
#         # PASSWORD = os.environ.get('FIREHOUSE_PASSWORD', 'your_password_here')
#
#         # Variable to keep track of the last email ID processed
#         last_processed_id = 0
#
#         ################ IMAP SSL Connection ##############################
#         with imaplib.IMAP4_SSL(host="imap.gmail.com", port=imaplib.IMAP4_SSL_PORT) as imap_ssl:
#             print("Connection Object : {}".format(imap_ssl))
#
#             ############### Login to Mailbox ######################
#             print("Logging into mailbox...")
#             resp_code, response = imap_ssl.login("firehouse.test.bkh@gmail.com", "jmze mchl vhvi elcb")
#
#             print("Response Code : {}".format(resp_code))
#             print("Response      : {}\n".format(response[0].decode()))
#
#             ############### Set Mailbox #############
#             resp_code, mail_count = imap_ssl.select(mailbox="INBOX", readonly=True)
#
#             ############### Retrieve Mail IDs for given Directory #############
#             resp_code, mail_ids = imap_ssl.search(None, "ALL")
#
#             print("Mail IDs : {}\n".format(mail_ids[0].decode().split()))
#
#             ############### Display Few Messages for given Directory #############
#             for mail_id in mail_ids[0].decode().split()[-2:]:
#                 print("================== Start of Mail [{}] ====================".format(mail_id))
#
#                 try:
#                     resp_code, mail_data = imap_ssl.fetch(mail_id, '(RFC822)')  ## Fetch mail data.
#                 except ValueError:
#                     print(f"Unexpected response format when fetching mail ID {mail_id}. Skipping...")
#                     continue
#                 if not mail_data or len(mail_data) < 2:
#                     print(f"Unexpected mail data format for mail ID {mail_id}: {mail_data}")
#                     continue  # Skip this mail and continue with the next one
#                 message = email.message_from_bytes(mail_data[0][1])  ## Construct Message from mail data
#                 email_subject = message.get("Subject")
#                 print("From       : {}".format(message.get("From")))
#                 print("To         : {}".format(message.get("To")))
#                 print("Bcc        : {}".format(message.get("Bcc")))
#                 print("Date       : {}".format(message.get("Date")))
#                 print("Subject    : {}".format(message.get("Subject")))
#
#                 print("Body : ")
#                 for part in message.walk():
#                     if part.get_content_type() == "text/plain":
#                         if part.get("Content-Transfer-Encoding") == "base64":
#                             body_content = part.get_payload(decode=True).decode("utf-8")
#                         else:
#                             body_content = part.get_payload()
#                         body_lines = body_content.split("\n")
#                         print("\n".join(body_lines))  ### Print lines of message
#
#                 print("================== End of Mail [{}] ====================\n".format(mail_id))
#                 if email_subject != "MCDPS CAD MESSAGE":
#                     print(f"Skipping email {mail_id} due to unmatched subject.")
#                     continue
#
#                 if email_subject == "MCDPS CAD MESSAGE":
#                     metadata = {
#                         "from": message.get("From"),
#                         "to": message.get("To"),
#                         "bcc": message.get("Bcc"),
#                         "date": message.get("Date"),
#                         "subject": message.get("Subject")
#                     }
#                     parsed_data = email_parser.parser(body_content, metadata)
#                     print(parsed_data)
#
#                     return parsed_data
#
#             ############# Close Selected Mailbox #######################
#             imap_ssl.close()
#
#         # Updating the last processed mail ID
#         # if mail_ids:
#         #     last_processed_id = int(mail_ids[0].decode().split()[-1])
#         #     print(f"Last processed mail ID: {last_processed_id}")
#         #     # return last_processed_id
#     except Exception as e:
#         print(f"Exception occurred: {e}")
#         traceback.print_exc()
#         return {"error": str(e)}


def check_emails():
    # Connect and login to the IMAP server
    imap_ssl = imaplib.IMAP4_SSL('imap.gmail.com')
    print("Connection Object :", imap_ssl)

    # Use your email credentials
    user_email = "firehouse.test.bkh@gmail.com"
    user_password = "jmze mchl vhvi elcb"

    print("Logging into mailbox...")
    response_code, response = imap_ssl.login(user_email, user_password)

    print("Response Code :", response_code)
    print("Response      :", response[0].decode())

    # Select the mailbox (Inbox by default)
    imap_ssl.select('INBOX')

    # Fetch the newest CAD message
    newest_email_id = fetch_newest_cad_message(imap_ssl)

    # If no email found, exit
    if not newest_email_id:
        return {"status": "No new CAD emails to process!"}

    # Fetch the details of the newest email
    status, email_data = imap_ssl.fetch(newest_email_id, '(RFC822)')
    raw_email = email_data[0][1]
    parsed_email = email.message_from_bytes(raw_email)

    # Extract the email details and body
    body_content = ""
    for part in parsed_email.walk():
        if part.get_content_type() == "text/plain":
            body_content = part.get_payload()

    # Parse the email metadata
    metadata = {
        "from": parsed_email.get("From"),
        "to": parsed_email.get("To"),
        "bcc": parsed_email.get("Bcc"),
        "date": parsed_email.get("Date"),
        "subject": parsed_email.get("Subject")
    }
    # Parse the email content
    parsed_data = email_parser.parser(body_content, metadata)

    # Push to Firebase
    firebase.store_data(parsed_data)

    report_id = parsed_data["incident"]["incident_number"]

    # Close the connection to the IMAP server
    imap_ssl.close()

    return {"status": f"Successfully processed incident {report_id} and pushed to Firebase!",
            "firebase_id": report_id,

            }


def fetch_newest_cad_message(imap_ssl):
    # Fetch unseen emails
    status, email_ids = imap_ssl.search(None, 'UNSEEN SUBJECT "MCDPS CAD MESSAGE"')
    if status != 'OK':
        return None

    email_ids_list = email_ids[0].decode('utf-8').split()

    # If no emails found, exit
    if not email_ids_list:
        return None

    # Sort emails by date
    email_dates = []

    for email_id in email_ids_list:
        status, email_data = imap_ssl.fetch(email_id, '(BODY[HEADER])')
        email_header = email.message_from_bytes(email_data[0][1])
        email_date = email.utils.parsedate_to_datetime(email_header['Date'])
        email_dates.append((email_id, email_date))

    # Sort the email_dates list by the datetime
    sorted_emails = sorted(email_dates, key=lambda x: x[1], reverse=True)

    # Get the newest email ID
    newest_email_id = sorted_emails[0][0]

    return newest_email_id
