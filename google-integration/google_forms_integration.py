from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload

import io
import yaml
import os
import subprocess
import argparse
import pandas as pd
import datetime

SCOPES = ["https://www.googleapis.com/auth/drive"]

def download_file(service, file_id):
    request = service.files().export_media(fileId=file_id, mimeType='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()
        print("Download %d%%." % int(status.progress() * 100))
    with open('output.xlsx', 'wb') as f:
        f.write(fh.getvalue())
    print("File downloaded")

def parse_to_csv():
    df = pd.read_excel('output.xlsx')
    df.to_csv('output.csv', index=False)
    print("File converted to CSV")

def create_yaml_structure(dataframe):
    yaml_data = {
        'Version': '1.0', # Tengo que fixear esto
        'Date': datetime.datetime.now().strftime('%d.%m.%Y')
    }

    services = []

    for _, row in dataframe.iterrows():
        service = {
            'Description': {
                'Name': row['Service name'],
                'Type': 'Service',
                'Criticality': row['Criticality']
            },
            'Functionality': row['Functionality'] if pd.notna(row['Functionality']) else '',
            'DataProcessed': {
                'Type': row['Data type'] if pd.notna(row['Data type']) else '',
                'DataCategory': row['Data category'] if pd.notna(row['Data category']) else '',
                'EncryptionAtRest': 'Yes' if row['Encryption at rest'] == 'Si' else 'No'
            },
            'Components': {
                'Internal': {
                    'Exist': 'Yes' if row['Internal Exists'] == 'Si' else 'No',
                    'Source': row['Internal Source'] if pd.notna(row['Internal Source']) else '',
                    'Note': row['Internal Note'] if pd.notna(row['Internal Note']) else ''
                },
                'External': {
                    'Exist': 'Yes' if row['External Exists'] == 'Si' else 'No',
                    'PackageManager': row['External Package Manager'] if pd.notna(row['External Package Manager']) else ''
                }
            },
            'Pipeline': {
                'Type': row['Pipeline Type'] if pd.notna(row['Pipeline Type']) else '',
                'CODEOWNERS': 'Yes' if row['Pipeline CODEOWNERS'] == 'Si' else 'No',
                'BranchProtection': 'Yes' if row['Branch protection'] == 'Si' else 'No',
                'SignCommits': 'Yes' if row['Sign commits'] == 'Si' else 'No',
                'PinActions': 'Yes' if row['Pin actions'] == 'Si' else 'No'
            },
            'Network': {
                'Access': row['Network access'] if pd.notna(row['Network access']) else ''
            },
            'dataFlow': [
                {
                    'name': row['Data flow name'] if pd.notna(row['Data flow name']) else '',
                    'description': row['Data flow description'] if pd.notna(row['Data flow description']) else '',
                    'source': row['Data flow source'] if pd.notna(row['Data flow source']) else '',
                    'EncryptionTransit': 'Yes' if row['Data flow encryption transit'] == 'Si' else 'No',
                    'Authentication': {
                        'Exist': 'Yes' if row['Data flow authentication exists'] == 'Si' else 'No',
                        'Type': row['Data flow auth type'] if pd.notna(row['Data flow auth type']) else ''
                    },
                    'Authorization': row['Data flow authorization'] if pd.notna(row['Data flow authorization']) else '',
                    'Protocol': row['Data flow protocol'] if pd.notna(row['Data flow protocol']) else '',
                    'Communication': {
                        'Type': row['Data flow communication type'] if pd.notna(row['Data flow communication type']) else ''
                    },
                    'interactions': [
                        {
                            'from': row['Interactions from'] if pd.notna(row['Interactions from']) else '',
                            'to': row['Interaction to'] if pd.notna(row['Interaction to']) else '',
                            'method': row['Interaction method'] if pd.notna(row['Interaction method']) else '',
                            'protocol': row['Interaction protocol'] if pd.notna(row['Interaction protocol']) else ''
                        }
                    ],
                    'servicesInvolved': [service.strip() for service in row['Services involved'].split(',')] if pd.notna(row['Services involved']) else []
                }
            ]
        }
        services.append(service)

    yaml_data['Services'] = services

    yaml_content = f"Version: '{yaml_data['Version']}'\nDate: {yaml_data['Date']}\n"

    for service in yaml_data['Services']:
        yaml_content += "\n# Order Processing Service Description\n"
        yaml_content += f"Description:\n  Name: {service['Description']['Name']}\n  Type: {service['Description']['Type']}\n  Criticality: {service['Description']['Criticality']}\n"
        yaml_content += "\n# Service Functionality\n"
        yaml_content += f"Functionality: {service['Functionality']}\n"
        yaml_content += "\n# Data Processing Details\n"
        yaml_content += f"DataProcessed:\n  Type: {service['DataProcessed']['Type']}\n  DataCategory: {service['DataProcessed']['DataCategory']}\n  EncryptionAtRest: {service['DataProcessed']['EncryptionAtRest']}\n"
        yaml_content += "\n# Components Used by the Service\n"
        yaml_content += f"Components:\n  Internal:\n    Exist: {service['Components']['Internal']['Exist']}\n    Source: {service['Components']['Internal']['Source']}\n    Note: {service['Components']['Internal']['Note']}\n"
        yaml_content += f"  External:\n    Exist: {service['Components']['External']['Exist']}\n    PackageManager: {service['Components']['External']['PackageManager']}\n"
        yaml_content += "\n# Pipeline Configuration\n"
        yaml_content += f"Pipeline:\n  Type: {service['Pipeline']['Type']}\n  CODEOWNERS: {service['Pipeline']['CODEOWNERS']}\n  BranchProtection: {service['Pipeline']['BranchProtection']}\n  SignCommits: {service['Pipeline']['SignCommits']}\n  PinActions: {service['Pipeline']['PinActions']}\n"
        yaml_content += "\n# Network Information\n"
        yaml_content += f"Network:\n  Access: {service['Network']['Access']}\n"
        yaml_content += "\n# Order Processing Service Data Flow\n"
        yaml_content += "dataFlow:\n"
        for flow in service['dataFlow']:
            yaml_content += f"  - name: {flow['name']}\n    description: {flow['description']}\n    source: {flow['source']}\n    EncryptionTransit: {flow['EncryptionTransit']}\n"
            yaml_content += f"    Authentication:\n      Exist: {flow['Authentication']['Exist']}\n      Type: {flow['Authentication']['Type']}\n"
            yaml_content += f"    Authorization: {flow['Authorization']}\n    Protocol: {flow['Protocol']}\n    Communication:\n      Type: {flow['Communication']['Type']}\n"
            yaml_content += "    interactions:\n"
            for interaction in flow['interactions']:
                yaml_content += f"      - from: {interaction['from']}\n        to: {interaction['to']}\n        method: {interaction['method']}\n        protocol: {interaction['protocol']}\n"
            yaml_content += f"    servicesInvolved: {flow['servicesInvolved']}\n"

    return yaml_content

def worker(url):
    try:
        file_id = url.split('/')[-2]
        creds = None
        if os.path.exists("token.json"):
            creds = Credentials.from_authorized_user_file("token.json", SCOPES)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            with open('token.json', 'w') as token:
                token.write(creds.to_json())
        service = build('drive', 'v3', credentials=creds)
        download_file(service, file_id)
        parse_to_csv()

        # Load the CSV data
        df = pd.read_csv('output.csv')

        # Convert the 'Marca temporal' column to datetime
        df['Marca temporal'] = pd.to_datetime(df['Marca temporal'], format='%Y-%m-%d %H:%M:%S.%f')

        # Get the latest date
        latest_date = df['Marca temporal'].max()

        # Filter rows by the latest date
        latest_rows = df[df['Marca temporal'] == latest_date]

        # Generate the YAML structure for the latest rows
        yaml_content = create_yaml_structure(latest_rows)

        # Save to a single YAML file
        with open(f"{latest_rows['Name']}.yaml", 'w') as yaml_file:
            yaml_file.write(yaml_content)
            print("YAML file created")
        
    except HttpError as e:
        print("An error occurred:", e)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download file from Google Drive")
    parser.add_argument("-u", "--url", type=str, help="URL of the file to download")
    args = parser.parse_args()
    worker(args.url)
    
    # Send file to TaaC-AI
    print("Starting TaaC-AI...")
    
    # I don't really like this, but it's a quick win
    venv_bin = '<Full path to venv>/bin/python3'
    taac_ai = '<Full path to TaaC-AI.py>'
    args = [venv_bin, taac_ai, 'latest_services.yaml']
    subprocess.run(args)