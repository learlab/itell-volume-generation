#!/usr/bin/env python3
"""
Prompt Tournament Script
Shuffles strategy outputs for blind evaluation and exports to Google Sheets.
"""

import json
import random
import os
from pathlib import Path
from typing import Dict, List, Tuple
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import pickle

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# Directory containing the revised outputs
REVISED_OUTPUTS_DIR = "/Users/tobasum/Downloads/revised-outputs"

# Strategy file mappings
STRATEGY_FILES = {
    'strategy1': 'itell_input_strategy1_cot.json',
    'strategy2': 'itell_input_strategy2_fewshot.json',
    'strategy3': 'itell_input_strategy3_validation.json'
}


def authenticate_google_sheets():
    """
    Authenticate with Google Sheets API using OAuth2 (personal account).
    """
    creds = None
    
    # The file token.pickle stores the user's access and refresh tokens
    token_path = os.path.join(os.path.dirname(__file__), 'token.pickle')
    
    if os.path.exists(token_path):
        with open(token_path, 'rb') as token:
            creds = pickle.load(token)
    
    # If there are no (valid) credentials available, let the user log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # Need to create credentials.json from Google Cloud Console
            creds_json = os.path.join(os.path.dirname(__file__), 'credentials.json')
            if not os.path.exists(creds_json):
                raise FileNotFoundError(
                    f"credentials.json not found at {creds_json}.\n"
                    "Please download OAuth2 credentials from Google Cloud Console:\n"
                    "1. Go to https://console.cloud.google.com/\n"
                    "2. Create or select a project\n"
                    "3. Enable Google Sheets API\n"
                    "4. Create OAuth2 credentials (Desktop app)\n"
                    "5. Download as credentials.json and place in src/ directory"
                )
            
            flow = InstalledAppFlow.from_client_secrets_file(creds_json, SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save the credentials for the next run
        with open(token_path, 'wb') as token:
            pickle.dump(creds, token)
    
    return build('sheets', 'v4', credentials=creds)


def load_strategy_outputs(textbook_folder: str) -> Dict[str, dict]:
    """
    Load all three strategy outputs for a given textbook folder.
    
    Args:
        textbook_folder: Path to the textbook folder
    
    Returns:
        Dictionary mapping strategy name to parsed JSON data
    """
    outputs = {}
    
    for strategy_name, filename in STRATEGY_FILES.items():
        filepath = os.path.join(textbook_folder, filename)
        
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                outputs[strategy_name] = json.load(f)
        else:
            print(f"Warning: {filepath} not found")
            outputs[strategy_name] = None
    
    return outputs


def shuffle_strategies(strategies: Dict[str, dict]) -> Tuple[List[str], List[dict]]:
    """
    Shuffle the order of strategies for blind evaluation.
    
    Args:
        strategies: Dictionary mapping strategy name to data
    
    Returns:
        Tuple of (original_order, shuffled_data)
        - original_order: List of strategy names showing which strategy is in which position
        - shuffled_data: List of strategy data in shuffled order
    """
    strategy_items = list(strategies.items())
    random.shuffle(strategy_items)
    
    original_order = [name for name, _ in strategy_items]
    shuffled_data = [data for _, data in strategy_items]
    
    return original_order, shuffled_data


def format_json_for_display(data: dict, max_chars: int = 49000) -> str:
    """
    Convert JSON data to a human-readable markdown format for the sheet.
    
    Args:
        data: Parsed JSON data from strategy output
        max_chars: Maximum characters (truncate if exceeded)
    
    Returns:
        Formatted markdown string
    """
    if not data:
        return "N/A"
    
    output = []
    
    # Volume level
    output.append("# Volume")
    output.append(f"Title: {data.get('Title', 'N/A')}")
    output.append(f"Description: {data.get('Description', 'N/A')}")
    output.append(f"VolumeSummary: {data.get('VolumeSummary', 'N/A')}")
    output.append("")
    
    # Pages
    pages = data.get('Pages', [])
    for page in pages:
        output.append("# Page")
        output.append(f"Title: {page.get('Title', 'N/A')}")
        output.append(f"Order: {page.get('Order', 'N/A')}")
        output.append(f"ReferenceSummary: {page.get('ReferenceSummary', 'N/A')}")
        output.append("")
        
        # Content chunks
        content = page.get('Content', [])
        for chunk in content:
            component = chunk.get('__component', '')
            
            if 'plain-chunk' in component:
                output.append("## Plain Chunk")
            else:
                output.append("## Normal Chunk")
            
            # Add ALL chunk fields (except __component which we already used)
            for key, value in chunk.items():
                if key != '__component':  # Skip internal component field
                    output.append(f"{key}: {value}")
            
            output.append("")
    
    result = "\n".join(output)
    
    # Truncate if too long
    if len(result) > max_chars:
        result = result[:max_chars] + "\n\n... [TRUNCATED - Content exceeds character limit]"
    
    return result


def validate_cell_sizes(values: List[List[str]]) -> bool:
    """
    Validate that no cell exceeds 50,000 characters.
    
    Args:
        values: 2D array of cell values
    
    Returns:
        True if all cells are valid, False otherwise
    """
    for row_idx, row in enumerate(values):
        for col_idx, cell in enumerate(row):
            if isinstance(cell, str) and len(cell) > 50000:
                print(f"ERROR: Cell at row {row_idx}, col {col_idx} exceeds 50,000 characters ({len(cell)} chars)")
                return False
    return True


def create_combined_spreadsheet(service, all_textbook_data: List[Dict]) -> str:
    """
    Create a single Google Spreadsheet with all textbooks.
    
    Args:
        service: Google Sheets API service
        all_textbook_data: List of dicts containing textbook name, order, and shuffled data
    
    Returns:
        URL of the created spreadsheet
    """
    spreadsheet_title = "Prompt Tournament - All Textbooks"
    
    spreadsheet = {
        'properties': {
            'title': spreadsheet_title
        },
        'sheets': [{
            'properties': {
                'title': 'Evaluation',
                'gridProperties': {
                    'frozenRowCount': 1,
                    'frozenColumnCount': 1
                }
            }
        }]
    }
    
    try:
        spreadsheet = service.spreadsheets().create(
            body=spreadsheet,
            fields='spreadsheetId,spreadsheetUrl'
        ).execute()
        
        spreadsheet_id = spreadsheet.get('spreadsheetId')
        spreadsheet_url = spreadsheet.get('spreadsheetUrl')
        
        print(f"Created spreadsheet: {spreadsheet_url}")
        
        # Prepare data for the sheet
        headers = ['Textbook', 'Strategy 1', 'Strategy 2', 'Strategy 3', 'PDF', 'Selection', 'Comments']
        
        # Build rows for each textbook
        values = [headers]
        
        for item in all_textbook_data:
            textbook_name = item['textbook']
            original_order = item['mapping']
            shuffled_data = item['data']
            
            # Convert JSON data to formatted markdown strings
            formatted_strings = [format_json_for_display(data) for data in shuffled_data]
            
            # Create row: textbook name + 3 formatted strings + empty PDF/Selection/Comments
            data_row = [textbook_name] + formatted_strings + ['', '', '']
            values.append(data_row)
        
        # Add a mapping note at the bottom
        values.append([])  # Empty row
        values.append(['MAPPING (delete before evaluation):'])
        
        for item in all_textbook_data:
            textbook_name = item['textbook']
            original_order = item['mapping']
            mapping_text = (f"{textbook_name}: Strategy 1 = {original_order[0]}, "
                          f"Strategy 2 = {original_order[1]}, Strategy 3 = {original_order[2]}")
            values.append([mapping_text])
        
        # Validate that no cell exceeds 50,000 characters
        if not validate_cell_sizes(values):
            print("ERROR: Some cells exceed the 50,000 character limit!")
            print("This should not happen with the 49,000 char split limit.")
            return None
        
        body = {
            'values': values
        }
        
        # Update the sheet with data
        service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range='Evaluation!A1',
            valueInputOption='USER_ENTERED',
            body=body
        ).execute()
        
        # Format the sheet
        num_textbooks = len(all_textbook_data)
        
        requests = [
            # Format header row
            {
                'repeatCell': {
                    'range': {
                        'sheetId': 0,
                        'startRowIndex': 0,
                        'endRowIndex': 1
                    },
                    'cell': {
                        'userEnteredFormat': {
                            'backgroundColor': {
                                'red': 0.2,
                                'green': 0.6,
                                'blue': 0.9
                            },
                            'textFormat': {
                                'bold': True,
                                'foregroundColor': {
                                    'red': 1,
                                    'green': 1,
                                    'blue': 1
                                }
                            }
                        }
                    },
                    'fields': 'userEnteredFormat(backgroundColor,textFormat)'
                }
            },
            # Set textbook column width
            {
                'updateDimensionProperties': {
                    'range': {
                        'sheetId': 0,
                        'dimension': 'COLUMNS',
                        'startIndex': 0,
                        'endIndex': 1
                    },
                    'properties': {
                        'pixelSize': 200
                    },
                    'fields': 'pixelSize'
                }
            },
            # Set strategy column widths
            {
                'updateDimensionProperties': {
                    'range': {
                        'sheetId': 0,
                        'dimension': 'COLUMNS',
                        'startIndex': 1,
                        'endIndex': 4
                    },
                    'properties': {
                        'pixelSize': 300
                    },
                    'fields': 'pixelSize'
                }
            },
            # Set PDF/Selection/Comments column widths
            {
                'updateDimensionProperties': {
                    'range': {
                        'sheetId': 0,
                        'dimension': 'COLUMNS',
                        'startIndex': 4,
                        'endIndex': 7
                    },
                    'properties': {
                        'pixelSize': 150
                    },
                    'fields': 'pixelSize'
                }
            },
            # Enable text wrapping for all columns
            {
                'repeatCell': {
                    'range': {
                        'sheetId': 0,
                        'startRowIndex': 0,
                        'endRowIndex': num_textbooks + 1
                    },
                    'cell': {
                        'userEnteredFormat': {
                            'wrapStrategy': 'WRAP',
                            'verticalAlignment': 'TOP'
                        }
                    },
                    'fields': 'userEnteredFormat(wrapStrategy,verticalAlignment)'
                }
            }
        ]
        
        service.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body={'requests': requests}
        ).execute()
        
        return spreadsheet_url
    
    except HttpError as error:
        print(f"An error occurred: {error}")
        return None


def main():
    """
    Main function to process all textbooks and create Google Sheets.
    """
    print("=" * 80)
    print("Prompt Tournament - Strategy Shuffler & Google Sheets Export")
    print("=" * 80)
    print()
    
    # Authenticate with Google Sheets
    print("Authenticating with Google Sheets API...")
    try:
        service = authenticate_google_sheets()
        print("✓ Authentication successful!")
        print()
    except Exception as e:
        print(f"✗ Authentication failed: {e}")
        return
    
    # Get all textbook folders
    textbook_folders = [
        d for d in os.listdir(REVISED_OUTPUTS_DIR)
        if os.path.isdir(os.path.join(REVISED_OUTPUTS_DIR, d)) and not d.startswith('.')
    ]
    
    textbook_folders.sort()
    
    print(f"Found {len(textbook_folders)} textbook folders:")
    for folder in textbook_folders:
        print(f"  - {folder}")
    print()
    
    # Process each textbook and collect data
    all_textbook_data = []
    
    for textbook_name in textbook_folders:
        print(f"Processing: {textbook_name}")
        print("-" * 80)
        
        textbook_path = os.path.join(REVISED_OUTPUTS_DIR, textbook_name)
        
        # Load strategy outputs
        strategies = load_strategy_outputs(textbook_path)
        
        # Check if all strategies are loaded
        if None in strategies.values():
            print(f"⚠ Warning: Some strategies missing for {textbook_name}")
        
        # Shuffle strategies
        original_order, shuffled_data = shuffle_strategies(strategies)
        
        print(f"  Shuffled order: {' | '.join(original_order)}")
        
        # Store data
        all_textbook_data.append({
            'textbook': textbook_name,
            'mapping': original_order,
            'data': shuffled_data
        })
        
        print(f"✓ Data prepared")
        print()
    
    # Create single combined spreadsheet
    print("=" * 80)
    print("Creating combined Google Sheet...")
    print("=" * 80)
    print()
    
    spreadsheet_url = create_combined_spreadsheet(service, all_textbook_data)
    
    if spreadsheet_url:
        print(f"✓ Combined spreadsheet created: {spreadsheet_url}")
        print()
        
        # Print summary
        print("=" * 80)
        print("SUMMARY")
        print("=" * 80)
        print()
        print(f"Spreadsheet URL: {spreadsheet_url}")
        print()
        print(f"Included {len(all_textbook_data)} textbooks:")
        print()
        
        for item in all_textbook_data:
            print(f"{item['textbook']}:")
            print(f"  Mapping: {' | '.join(item['mapping'])}")
            print()
        
        # Save mapping to file for reference
        mapping_file = os.path.join(os.path.dirname(__file__), 'tournament_mapping.json')
        results = {
            'spreadsheet_url': spreadsheet_url,
            'textbooks': [{
                'textbook': item['textbook'],
                'mapping': item['mapping']
            } for item in all_textbook_data]
        }
        
        with open(mapping_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2)
        
        print(f"Mapping saved to: {mapping_file}")
        print()
        print("NOTE: The spreadsheet has mapping notes at the bottom.")
        print("Delete those rows before sharing with evaluators!")
    else:
        print("✗ Failed to create spreadsheet")
        return


if __name__ == '__main__':
    main()
