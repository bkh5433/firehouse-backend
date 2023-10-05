import os

from flask import Flask, jsonify
from modules import email_processing
from modules import email_processingv2 as email_parser
import traceback

app = Flask(__name__)


def check_emails():
    try:
        import imaplib
        import email

        # Fetching credentials from environment variables (placeholders for now)
        # EMAIL = os.environ.get('FIREHOUSE_EMAIL', 'your_email_here')
        # PASSWORD = os.environ.get('FIREHOUSE_PASSWORD', 'your_password_here')

        # Variable to keep track of the last email ID processed
        last_processed_id = 0

        ################ IMAP SSL Connection ##############################
        with imaplib.IMAP4_SSL(host="imap.gmail.com", port=imaplib.IMAP4_SSL_PORT) as imap_ssl:
            print("Connection Object : {}".format(imap_ssl))

            ############### Login to Mailbox ######################
            print("Logging into mailbox...")
            resp_code, response = imap_ssl.login("firehouse.test.bkh@gmail.com", "jmze mchl vhvi elcb")

            print("Response Code : {}".format(resp_code))
            print("Response      : {}\n".format(response[0].decode()))

            ############### Set Mailbox #############
            resp_code, mail_count = imap_ssl.select(mailbox="INBOX", readonly=True)

            ############### Retrieve Mail IDs for given Directory #############
            resp_code, mail_ids = imap_ssl.search(None, "ALL")

            print("Mail IDs : {}\n".format(mail_ids[0].decode().split()))

            ############### Display Few Messages for given Directory #############
            for mail_id in mail_ids[0].decode().split()[-2:]:
                print("================== Start of Mail [{}] ====================".format(mail_id))

                try:
                    resp_code, mail_data = imap_ssl.fetch(mail_id, '(RFC822)')  ## Fetch mail data.
                except ValueError:
                    print(f"Unexpected response format when fetching mail ID {mail_id}. Skipping...")
                    continue
                if not mail_data or len(mail_data) < 2:
                    print(f"Unexpected mail data format for mail ID {mail_id}: {mail_data}")
                    continue  # Skip this mail and continue with the next one
                message = email.message_from_bytes(mail_data[0][1])  ## Construct Message from mail data
                email_subject = message.get("Subject")
                print("From       : {}".format(message.get("From")))
                print("To         : {}".format(message.get("To")))
                print("Bcc        : {}".format(message.get("Bcc")))
                print("Date       : {}".format(message.get("Date")))
                print("Subject    : {}".format(message.get("Subject")))

                print("Body : ")
                for part in message.walk():
                    if part.get_content_type() == "text/plain":
                        if part.get("Content-Transfer-Encoding") == "base64":
                            body_content = part.get_payload(decode=True).decode("utf-8")
                        else:
                            body_content = part.get_payload()
                        body_lines = body_content.split("\n")
                        print("\n".join(body_lines))  ### Print lines of message

                print("================== End of Mail [{}] ====================\n".format(mail_id))
                if email_subject != "MCDPS CAD MESSAGE":
                    print(f"Skipping email {mail_id} due to unmatched subject.")
                    continue

                if email_subject == "MCDPS CAD MESSAGE":
                    parsed_data = email_parser.parser(body_content)
                    print(parsed_data)

                    return parsed_data

            ############# Close Selected Mailbox #######################
            imap_ssl.close()

        # Updating the last processed mail ID
        if mail_ids:
            last_processed_id = int(mail_ids[0].decode().split()[-1])
            print(f"Last processed mail ID: {last_processed_id}")
            # return last_processed_id
    except Exception as e:
        print(traceback.print_stack())
        return str(e)





@app.route('/check-emails', methods=['GET'])
def trigger_check_emails():
    result = check_emails()
    return jsonify(result)


if __name__ == '__main__':
    app.run()
