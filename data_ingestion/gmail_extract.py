import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# process pdf plumber
import base64
import io
import pdfplumber
from PyPDF2 import PdfReader, PdfWriter
import re
import filter_retriever

import logging
logging.getLogger("PyPDF2").setLevel(logging.ERROR)

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

def get_creds():
  """Shows basic usage of the Gmail API.
  Lists the user's Gmail labels.
  """
  creds = None
  # The file token.json stores the user's access and refresh tokens, and is
  # created automatically when the authorization flow completes for the first
  # time.
  if os.path.exists("token.json"):
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
  # If there are no (valid) credentials available, let the user log in.
  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
    else:
      flow = InstalledAppFlow.from_client_secrets_file(
          "credentials.json", SCOPES
      )
      creds = flow.run_local_server(port=55647)
    # Save the credentials for the next run
    with open("token.json", "w") as token:
      token.write(creds.to_json())
      
  return creds



def clean_cid_patterns(text):
    # Remove (cid:number) or (cid:word) patterns
    cleaned_text = re.sub(r'\(cid:[^)]*\)', '', text)
    return cleaned_text

def process_pdf_data(base64_data, password):
    try:
        # Decode base64url to bytes
        pdf_bytes = base64.urlsafe_b64decode(base64_data.encode('utf-8'))
        pdf_stream = io.BytesIO(pdf_bytes)
        
        # Load PDF with PyPDF2
        reader = PdfReader(pdf_stream)
        if reader.is_encrypted:
            if not password:
                raise ValueError("PDF is encrypted but no password provided")
            if reader.decrypt(password) == 0:
                raise ValueError("Failed to decrypt PDF with the provided password")
        
        # Write decrypted PDF to bytes buffer for pdfplumber
        writer = PdfWriter()
        for page in reader.pages:
            writer.add_page(page)
        decrypted_pdf_stream = io.BytesIO()
        writer.write(decrypted_pdf_stream)
        decrypted_pdf_stream.seek(0)
        
        # Use pdfplumber to extract text
        text = ""
        with pdfplumber.open(decrypted_pdf_stream) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text() or ""
                text += page_text
        
        clean_text = clean_cid_patterns(text)
        return clean_text
    
    except Exception as e:
        print(f"Error processing PDF with pdfplumber: {e}")
        return None
         
def get_attachments(service, message_ids, docpass):
    attachments = []
    print(f'Number of PDFs found: {len(message_ids)}, starting to process them.')
    for idx, msg_id in enumerate(message_ids, start=1):
        getdata = service.users().messages().get(userId='me', id=msg_id).execute()
        subject = next((data['value'] for data in getdata['payload']['headers'] if data['name'] == 'Subject'), None)
        months, years = filter_retriever.find_months_and_years(subject)
        parts = getdata['payload'].get('parts', [])
        
        for part in parts:
            filename = part.get('filename')
            body = part.get('body', {})
            attach_id = body.get('attachmentId')
            mime_type = part.get('mimeType')
            
            if filename and attach_id:
                attachment = service.users().messages().attachments().get(
                    userId='me', messageId=msg_id, id=attach_id).execute()
                
                text = process_pdf_data(attachment['data'], docpass)
        
                attachments.append({
                    'filename': filename,
                    'mime_type': mime_type,
                    'data': text,
                    'months' : months,
                    'years' : years
                })
                
        print(f'{idx} pdfs are processed', end='\r', flush=True)
            
    print(f'{idx} pdfs are processed')
    return attachments

def trim_pdf(content):
    for details in content:
        trim_words = 'MOST IMPORTANT TERMS AND CONDITIONS (MITC)'
        if trim_words in details['data']:
            find_position = details['data'].find(trim_words)
            details['data'] = details['data'][:find_position + len(trim_words)]
        else:
            pass
    return content
        
         

def main(docpass,subjectname):
    creds = get_creds()
    service = build("gmail", "v1", credentials=creds)
    fetch_credit_emails = service.users().messages().list(userId='me', q=f'Subject: "{subjectname}"').execute()
    message_ids = [list['id'] for list in fetch_credit_emails['messages']]
    get_all_details = get_attachments(service, message_ids,docpass)
    get_trim_pdf = trim_pdf(get_all_details)
    return get_trim_pdf