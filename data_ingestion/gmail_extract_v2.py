import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from PyPDF2 import PdfReader, PdfWriter
import pdfplumber
import base64
import io
import re
from tqdm import tqdm
from pathlib import Path
base_dir = Path(__file__).resolve().parents[1]

import filter_retriever
import concurrent.futures
from itertools import repeat
import time

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

def get_creds():
  """Shows basic usage of the Gmail API.
  Lists the user's Gmail labels.
  """
  creds = None
  # The file token.json stores the user's access and refresh tokens, and is
  # created automatically when the authorization flow completes for the first
  # time.
  if os.path.exists(base_dir/"credentials"/"token.json"):
    creds = Credentials.from_authorized_user_file(base_dir/"credentials"/"token.json", SCOPES)
  # If there are no (valid) credentials available, let the user log in.
  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
    else:
      flow = InstalledAppFlow.from_client_secrets_file(
          base_dir/"credentials"/"gmail.json", SCOPES
      )
      creds = flow.run_local_server(port=55647, prompt="consent")
    # Save the credentials for the next run
    with open(base_dir/"credentials"/"token.json", "w") as token:
      token.write(creds.to_json())
      
  return creds

def lookup_messageID(service, subject):  #Network bound
    messageId = service.users().messages().list(userId="me", q=f"Subject: {subject}").execute()['messages']
    return messageId

def lookup_attachment_id(creds, messageId): #network bound
    
    service = build("gmail", "v1", credentials=creds)
    
    attachmentContent = service.users().messages().get(userId="me", id=messageId).execute()
    parts = attachmentContent['payload'].get('parts', [])
    subject = next((data['value'] for data in attachmentContent['payload']['headers'] if data['name'] == 'Subject'), None)
    for part in parts:
        filename = part.get('filename')
        body = part.get('body', {})
        attach_id = body.get('attachmentId')
        
        if filename and attach_id:
            attachmentData = service.users().messages().attachments().get(
                userId='me', messageId=messageId, id=attach_id).execute()

    return {
        "attachment": attachmentData['data'],
        "subject": subject,
        "filename": filename
    }

def get_pdf_data(attachmentData, password): #cpu bound
    try:
        # Decode base64url to bytes
        pdf_bytes = base64.urlsafe_b64decode(attachmentData.encode('utf-8'))
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
        
        return text
    
    except Exception as e:
        print(f"Error processing PDF with pdfplumber: {e}")
        return None
    
def clean_cid_patterns(text):
    # Remove (cid:number) or (cid:word) patterns
    cleaned_text = re.sub(r'\(cid:[^)]*\)', '', text)
    return cleaned_text        

def main(docpass, subject):
    creds = get_creds()
    service = build("gmail", "v1", credentials=creds)
    messageId_init = lookup_messageID(service, subject) #list of dictionaries
    messageId = [message['id'] for message in messageId_init]
    
    final_content = []
    
    start = time.perf_counter()
    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = list(
            tqdm(
                executor.map(lookup_attachment_id, repeat(creds), messageId)
            )
        )
        
    attachment_content = []
    for item in results:
        months , years = filter_retriever.find_months_and_years(item['subject'])
        attachment_content.append({
            "filename" : item['filename'],
            "raw_data" : item['attachment'],
            "months" : months,
            "years" : years
        })
        
    raw_data = [item["raw_data"] for item in attachment_content]
        
    with concurrent.futures.ProcessPoolExecutor() as executor:
        results_data = list(
            tqdm(
                executor.map(get_pdf_data, raw_data, repeat(docpass))
            )
        )
        
    final_content = []
    for meta, pdf_data in zip(attachment_content, results_data):
        clean_text = clean_cid_patterns(pdf_data)
        final_content.append({
            "filename" : meta['filename'],
            "data" : clean_text,
            "months" : meta['months'],
            "years" : meta['years']
        })
        
    end=time.perf_counter()
    
    print(f"Time taken: {round(end-start,2)} seconds")

    return final_content
