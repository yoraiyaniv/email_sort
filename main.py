import time
import logging
import os

from google_cloud_api import get_gmail_service, get_user_labels, label_email, get_messages_in_time_window, get_email_content, mark_email_as_read
from  google_gemini_api import classify_email

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

FIVE_MINUTES = 5 * 60    

def main():
    service = get_gmail_service()

    labels_ids: dict = get_user_labels(service)
    labels = labels_ids.keys()

    # Polls the gmail API for new emails in the last 5 minutes
    messages_ids = get_messages_in_time_window(service, str(int(time.time()) - FIVE_MINUTES), str(int(time.time()))) 

    logging.info(f"Found {len(messages_ids)} new emails in the last 5 minutes.")

    # Process each email
    emails = {}
    for email_id in messages_ids:
        email_content = get_email_content(service, email_id)
        emails[email_id] = email_content
        
    for email_id, email_content in emails.items():
        # Classify the email content using Gemini API
        classification = classify_email(email_content, labels)
        if classification:
            label_email(service, email_id, labels_ids.get(classification))
            mark_email_as_read(service, email_id)
            logging.info(f"Email ID: {email_id} classified as '{classification}' and labeled.")
        else:
            logging.warning(f"Email ID: {email_id} could not be classified.")

if __name__ == "__main__":
    if os.path.exists("token.json"):
        os.remove("token.json")
    logging.info("Starting email classification service...")
    while True:
        main()
        logging.info(f"Sleeping for 5 minutes...")
        time.sleep(FIVE_MINUTES)