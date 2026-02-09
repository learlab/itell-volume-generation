#!/usr/bin/env python3
"""
Analyze Prompt Tournament Results

This script automatically fetches data from Google Sheets and analyzes:
1. Which strategy performed best (with descriptive statistics)
2. Annotator comments (recurring themes and concerns)

The script maps selections back to actual strategies using tournament_mapping.json.
"""

import json
import os
import pickle
import csv
from collections import Counter, defaultdict
from typing import Dict, List, Tuple
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import re


def get_google_sheets_credentials():
    """
    Get Google Sheets API credentials.
    """
    from google_auth_oauthlib.flow import InstalledAppFlow
    
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
    creds = None
    token_path = os.path.join(os.path.dirname(__file__), 'token.pickle')
    credentials_path = os.path.join(os.path.dirname(__file__), 'client_secret_292793864190-84u88cqm6319v0aa1ufnj9l416f98pi8.apps.googleusercontent.com.json')
    
    # Token file stores the user's access and refresh tokens
    if os.path.exists(token_path):
        with open(token_path, 'rb') as token:
            creds = pickle.load(token)
    
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
                # Save the refreshed credentials
                with open(token_path, 'wb') as token:
                    pickle.dump(creds, token)
            except Exception as e:
                print(f"Error refreshing credentials: {e}")
                print("Attempting to re-authenticate...")
                creds = None
        
        if not creds:
            # Re-authenticate
            if not os.path.exists(credentials_path):
                raise FileNotFoundError(
                    f"Credentials file not found: {credentials_path}\n"
                    "Please ensure you have the Google API credentials file."
                )
            
            flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
            creds = flow.run_local_server(port=0)
            
            # Save the credentials for the next run
            with open(token_path, 'wb') as token:
                pickle.dump(creds, token)
    
    return creds


def load_tournament_mapping(mapping_file: str = None) -> Dict:
    """
    Load the tournament mapping file that shows which strategy is in which column.
    
    Args:
        mapping_file: Path to the tournament mapping JSON file
    
    Returns:
        Dictionary with spreadsheet_url and list of textbooks with mappings
    """
    if mapping_file is None:
        mapping_file = os.path.join(os.path.dirname(__file__), 'tournament_mapping.json')
    
    if not os.path.exists(mapping_file):
        raise FileNotFoundError(
            f"Mapping file not found: {mapping_file}\n"
            "Please ensure tournament_mapping.json exists in the src/ directory."
        )
    
    with open(mapping_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def get_all_sheet_names(spreadsheet_id: str) -> List[str]:
    """
    Get all sheet tab names from a Google Spreadsheet.
    
    Args:
        spreadsheet_id: The Google Sheets ID
    
    Returns:
        List of sheet names
    """
    try:
        creds = get_google_sheets_credentials()
        service = build('sheets', 'v4', credentials=creds)
        
        # Get spreadsheet metadata
        spreadsheet = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
        sheets = spreadsheet.get('sheets', [])
        
        sheet_names = [sheet['properties']['title'] for sheet in sheets]
        return sheet_names
    
    except HttpError as error:
        print(f"An error occurred: {error}")
        return []


def fetch_sheet_data(spreadsheet_id: str, sheet_name: str = "Sheet1") -> List[List[str]]:
    """
    Fetch data from Google Sheets.
    
    Args:
        spreadsheet_id: The Google Sheets ID
        sheet_name: Name of the sheet tab (default: "Sheet1")
    
    Returns:
        List of rows from the sheet
    """
    try:
        creds = get_google_sheets_credentials()
        service = build('sheets', 'v4', credentials=creds)
        
        # Fetch all data from the sheet
        range_name = f"'{sheet_name}'!A:H"  # Columns A through H (Textbook to Comments)
        result = service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range=range_name
        ).execute()
        
        values = result.get('values', [])
        return values
    
    except HttpError as error:
        print(f"An error occurred: {error}")
        return []


def fetch_all_sheets_data(spreadsheet_id: str) -> Dict[str, List[List[str]]]:
    """
    Fetch data from all sheets in the spreadsheet.
    
    Args:
        spreadsheet_id: The Google Sheets ID
    
    Returns:
        Dictionary mapping sheet name to sheet data
    """
    # Get all sheet names
    sheet_names = get_all_sheet_names(spreadsheet_id)
    
    if not sheet_names:
        return {}
    
    print(f"Found {len(sheet_names)} sheets: {', '.join(sheet_names[:5])}" + 
          (f" and {len(sheet_names) - 5} more..." if len(sheet_names) > 5 else ""))
    print()
    
    # Fetch data from each sheet
    all_data = {}
    for sheet_name in sheet_names:
        # Skip sheets that are clearly mapping/reference sheets
        if 'mapping' in sheet_name.lower() or 'reference' in sheet_name.lower():
            print(f"  Skipping: {sheet_name} (appears to be a reference sheet)")
            continue
        
        print(f"  Fetching: {sheet_name}...")
        data = fetch_sheet_data(spreadsheet_id, sheet_name)
        
        if data:
            all_data[sheet_name] = data
    
    print()
    return all_data


def load_csv_data(csv_file: str) -> List[List[str]]:
    """
    Load data from a CSV file.
    
    Args:
        csv_file: Path to the CSV file
    
    Returns:
        List of rows from the CSV
    """
    if not os.path.exists(csv_file):
        raise FileNotFoundError(f"CSV file not found: {csv_file}")
    
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        return list(reader)


def parse_sheet_data(sheet_data: List[List[str]], evaluator_name: str = "Unknown") -> Tuple[Dict[str, str], Dict[str, List[str]]]:
    """
    Parse the sheet data to extract selections and comments from a single evaluator.
    
    Args:
        sheet_data: Raw sheet data
        evaluator_name: Name of the evaluator (tab name)
    
    Returns:
        Tuple of (selections dict, comments dict by textbook)
    """
    if not sheet_data or len(sheet_data) < 2:
        return {}, {}
    
    # Find header row and evaluator columns
    header_row = sheet_data[0]
    
    # Expected columns: Textbook, Strategy 1, Strategy 2, Strategy 3, PDF, Selection/Preferred columns...
    textbook_col = 0
    
    # Find all "Selection" or "Preferred" columns
    selection_cols = []
    comment_cols = []
    
    for i, col_name in enumerate(header_row):
        col_lower = col_name.lower()
        if 'selection' in col_lower or 'preferred' in col_lower or 'choice' in col_lower:
            selection_cols.append(i)
        elif 'comment' in col_lower or 'note' in col_lower or 'feedback' in col_lower:
            comment_cols.append(i)
    
    selections = {}
    all_comments = defaultdict(list)
    
    # Parse data rows (skip header and any empty rows)
    for row_idx, row in enumerate(sheet_data[1:], start=2):
        if not row or len(row) <= textbook_col:
            continue
        
        textbook_name = row[textbook_col].strip()
        if not textbook_name or textbook_name.startswith("MAPPING"):
            continue
        
        # Get selection (use first non-empty selection column)
        for sel_col in selection_cols:
            if sel_col < len(row) and row[sel_col].strip():
                selection = row[sel_col].strip()
                selections[textbook_name] = selection
                break  # Take first selection found
        
        # Get comments from all comment columns
        for comment_col in comment_cols:
            if comment_col < len(row) and row[comment_col].strip():
                comment = row[comment_col].strip()
                all_comments[textbook_name].append(f"[{evaluator_name}] {comment}")
    
    return selections, dict(all_comments)


def aggregate_all_evaluators(all_sheets_data: Dict[str, List[List[str]]]) -> Tuple[Dict[str, List[str]], Dict[str, List[str]]]:
    """
    Aggregate selections and comments from all evaluators (all sheets).
    
    Args:
        all_sheets_data: Dictionary mapping sheet name to sheet data
    
    Returns:
        Tuple of (all_selections dict with list of selections per textbook, all_comments dict)
    """
    # Store all selections per textbook (can have multiple votes)
    all_selections = defaultdict(list)
    all_comments = defaultdict(list)
    
    for sheet_name, sheet_data in all_sheets_data.items():
        selections, comments = parse_sheet_data(sheet_data, evaluator_name=sheet_name)
        
        # Add selections
        for textbook, selection in selections.items():
            all_selections[textbook].append(selection)
        
        # Add comments
        for textbook, comment_list in comments.items():
            all_comments[textbook].extend(comment_list)
    
    return dict(all_selections), dict(all_comments)


def categorize_comment(comment: str) -> str:
    """
    Categorize a comment as problem, strength, or observation.
    
    Args:
        comment: The comment text
    
    Returns:
        Category: 'problem', 'strength', or 'observation'
    """
    comment_lower = comment.lower()
    
    # Problem indicators
    problem_keywords = [
        'missing', 'incorrect', 'wrong', 'error', 'mistake', 'failed', 'not',
        'doesn\'t', 'don\'t', 'issue', 'problem', 'bad', 'poor', 'lacks',
        'too short', 'too long', 'confusing', 'unclear'
    ]
    
    # Strength indicators
    strength_keywords = [
        'good', 'better', 'best', 'great', 'excellent', 'correct', 'accurate',
        'proper', 'well', 'perfect', 'optimal', 'happy medium'
    ]
    
    # Check for problems first (more specific)
    for keyword in problem_keywords:
        if keyword in comment_lower:
            return 'problem'
    
    # Then check for strengths
    for keyword in strength_keywords:
        if keyword in comment_lower:
            return 'strength'
    
    return 'observation'


def analyze_comments(comments_by_textbook: Dict[str, List[str]]) -> Dict:
    """
    Analyze comments to extract recurring themes and concerns.
    
    Args:
        comments_by_textbook: Dictionary of textbook names to list of comments
    
    Returns:
        Dictionary with comment analysis
    """
    all_comments = []
    for textbook, comments in comments_by_textbook.items():
        all_comments.extend(comments)
    
    if not all_comments:
        return {
            'total_comments': 0,
            'themes': [],
            'problems': [],
            'strengths': [],
            'observations': [],
            'all_comments': []
        }
    
    # Categorize comments
    problems = []
    strengths = []
    observations = []
    
    for comment in all_comments:
        category = categorize_comment(comment)
        if category == 'problem':
            problems.append(comment)
        elif category == 'strength':
            strengths.append(comment)
        else:
            observations.append(comment)
    
    # Keywords to look for in comments
    theme_keywords = {
        'missing_components': ['missing', 'lacks', 'doesn\'t include', 'absent', 'no keyphrase', 'no question', 'missing cri'],
        'chunk_length': ['too short', 'too long', 'chunk', 'length', 'short chunks', 'long chunks'],
        'formatting': ['format', 'formatting', 'layout', 'structure', 'organized'],
        'questions_cri': ['question', 'questions', 'constructed response', 'cri', 'keyphrase', 'assessment'],
        'chunking_strategy': ['chunking', 'chunks', 'divided', 'paragraphs', 'segmentation'],
        'accuracy': ['accurate', 'correct', 'wrong', 'error', 'mistake', 'incorrect', 'follows'],
        'content_issues': ['text', 'content', 'includes', 'excludes', 'page numbers', 'boxed numbers'],
        'reference_summary': ['reference', 'summary', 'references', 'invented'],
        'clarity': ['clear', 'clarity', 'readable', 'understandable', 'confusing', 'unclear', 'reading'],
        'completeness': ['complete', 'incomplete', 'all', 'necessary', 'components'],
    }
    
    theme_counts = Counter()
    theme_examples = defaultdict(list)
    
    # Count theme mentions
    for comment in all_comments:
        comment_lower = comment.lower()
        for theme, keywords in theme_keywords.items():
            for keyword in keywords:
                if keyword in comment_lower:
                    theme_counts[theme] += 1
                    if len(theme_examples[theme]) < 3:
                        theme_examples[theme].append(comment[:300])
                    break
    
    # Sort themes by frequency
    top_themes = theme_counts.most_common(10)
    
    return {
        'total_comments': len(all_comments),
        'textbooks_with_comments': len(comments_by_textbook),
        'problems': problems,
        'strengths': strengths,
        'observations': observations,
        'themes': [
            {
                'theme': theme.replace('_', ' ').title(),
                'count': count,
                'percentage': (count / len(all_comments) * 100) if all_comments else 0,
                'examples': theme_examples[theme][:2]
            }
            for theme, count in top_themes
        ],
        'all_comments': all_comments
    }


def map_selection_to_strategy(textbook_name: str, column_selected: str, 
                              mapping_data: Dict) -> str:
    """
    Map the selected column (e.g., "Strategy 1") back to the actual strategy.
    
    Args:
        textbook_name: Name of the textbook
        column_selected: Which column was selected (e.g., "Strategy 1", "Strategy 2", "Strategy 3")
        mapping_data: The tournament mapping data
    
    Returns:
        The actual strategy name (e.g., "strategy1", "strategy2", "strategy3")
    """
    # Find the textbook in mapping data
    textbook_mapping = None
    for item in mapping_data['textbooks']:
        if item['textbook'] == textbook_name:
            textbook_mapping = item
            break
    
    if not textbook_mapping:
        raise ValueError(f"Textbook '{textbook_name}' not found in mapping data")
    
    # Map column to index
    column_index = {
        'Strategy 1': 0,
        'Strategy 2': 1,
        'Strategy 3': 2
    }.get(column_selected)
    
    if column_index is None:
        raise ValueError(f"Invalid column selected: {column_selected}")
    
    # Get the actual strategy from mapping
    actual_strategy = textbook_mapping['mapping'][column_index]
    
    return actual_strategy


def analyze_results(all_selections: Dict[str, List[str]], mapping_data: Dict) -> Dict:
    """
    Analyze the tournament results to determine which strategy performed best.
    
    Args:
        all_selections: Dictionary mapping textbook name to list of selected columns (from all evaluators)
        mapping_data: The tournament mapping data
    
    Returns:
        Dictionary with analysis results
    """
    strategy_votes = Counter()
    detailed_results = []
    votes_by_textbook = {}
    
    for textbook_name, column_selections in all_selections.items():
        textbook_votes = Counter()
        
        for column_selected in column_selections:
            try:
                actual_strategy = map_selection_to_strategy(
                    textbook_name, column_selected, mapping_data
                )
                strategy_votes[actual_strategy] += 1
                textbook_votes[actual_strategy] += 1
            except ValueError as e:
                print(f"Warning: {e}")
        
        # Determine winner for this textbook (most votes)
        if textbook_votes:
            winning_strategy = textbook_votes.most_common(1)[0][0]
            votes_by_textbook[textbook_name] = {
                'votes': dict(textbook_votes),
                'winner': winning_strategy,
                'total_votes': sum(textbook_votes.values())
            }
            
            detailed_results.append({
                'textbook': textbook_name,
                'votes': dict(textbook_votes),
                'winner': winning_strategy,
                'total_evaluators': len(column_selections)
            })
    
    # Calculate percentages
    total_votes = sum(strategy_votes.values())
    strategy_percentages = {
        strategy: (count / total_votes * 100) if total_votes > 0 else 0
        for strategy, count in strategy_votes.items()
    }
    
    # Count textbook wins (which strategy won the most textbooks)
    textbook_wins = Counter()
    for result in detailed_results:
        textbook_wins[result['winner']] += 1
    
    return {
        'total_votes': dict(strategy_votes),
        'vote_percentages': strategy_percentages,
        'textbook_wins': dict(textbook_wins),
        'detailed_results': detailed_results,
        'total_evaluators': len(all_selections[next(iter(all_selections))]) if all_selections else 0,
        'total_textbooks': len(all_selections),
        'total_votes_cast': total_votes
    }


def print_results(analysis: Dict, comment_analysis: Dict = None):
    """
    Pretty print the analysis results.
    
    Args:
        analysis: Analysis results dictionary
        comment_analysis: Comment analysis dictionary (optional)
    """
    print("=" * 80)
    print("PROMPT TOURNAMENT RESULTS - SUMMARY")
    print("=" * 80)
    print()
    
    print(f"Total Evaluators: {analysis['total_evaluators']}")
    print(f"Total Textbooks: {analysis['total_textbooks']}")
    print(f"Total Votes Cast: {analysis['total_votes_cast']}")
    print()
    
    # Strategy preference results
    print("=" * 80)
    print("1. STRATEGY PREFERENCE (DESCRIPTIVE STATISTICS)")
    print("=" * 80)
    print()
    
    strategy_names = {
        'strategy1': 'Strategy 1 (Chain of Thought)',
        'strategy2': 'Strategy 2 (Few-shot)',
        'strategy3': 'Strategy 3 (Validation)'
    }
    
    # Sort by total votes
    sorted_by_votes = sorted(
        analysis['total_votes'].items(),
        key=lambda x: x[1],
        reverse=True
    )
    
    print("Overall Rankings (by total votes received):")
    print("-" * 80)
    
    for rank, (strategy, votes) in enumerate(sorted_by_votes, 1):
        percentage = analysis['vote_percentages'][strategy]
        full_name = strategy_names.get(strategy, strategy)
        textbook_wins = analysis['textbook_wins'].get(strategy, 0)
        
        medal = "🥇" if rank == 1 else "🥈" if rank == 2 else "🥉"
        print(f"{medal} Rank {rank}: {full_name}")
        print(f"   Total Votes: {votes} out of {analysis['total_votes_cast']} ({percentage:.1f}%)")
        print(f"   Textbooks Won (most votes): {textbook_wins} out of {analysis['total_textbooks']}")
        
        # Calculate margin if not last place
        if rank < len(sorted_by_votes):
            next_strategy, next_votes = sorted_by_votes[rank]
            margin = votes - next_votes
            print(f"   Margin over Rank {rank+1}: +{margin} votes")
        print()
    
    # Detailed results by textbook
    print("=" * 80)
    print("DETAILED RESULTS BY TEXTBOOK:")
    print("=" * 80)
    print()
    
    for result in analysis['detailed_results']:
        textbook = result['textbook']
        winner = result['winner']
        votes = result['votes']
        total = result['total_evaluators']
        
        full_name = strategy_names.get(winner, winner)
        
        print(f"  • {textbook}")
        print(f"    Winner: {full_name}")
        print(f"    Votes breakdown:")
        for strat, vote_count in sorted(votes.items(), key=lambda x: x[1], reverse=True):
            strat_name = strategy_names.get(strat, strat)
            print(f"      - {strat_name}: {vote_count}/{total}")
    
    print()
    
    # Comment analysis
    if comment_analysis and comment_analysis['total_comments'] > 0:
        print("=" * 80)
        print("2. ANNOTATOR COMMENTS ANALYSIS")
        print("=" * 80)
        print()
        
        print(f"Total Comments: {comment_analysis['total_comments']}")
        print(f"Textbooks with Comments: {comment_analysis['textbooks_with_comments']} out of {analysis['total_textbooks']}")
        print()
        
        # Show categorized comments
        print(f"📊 Comment Breakdown:")
        print(f"   🚨 Problems/Issues: {len(comment_analysis['problems'])} ({len(comment_analysis['problems'])/comment_analysis['total_comments']*100:.1f}%)")
        print(f"   ✅ Strengths: {len(comment_analysis['strengths'])} ({len(comment_analysis['strengths'])/comment_analysis['total_comments']*100:.1f}%)")
        print(f"   📝 Observations: {len(comment_analysis['observations'])} ({len(comment_analysis['observations'])/comment_analysis['total_comments']*100:.1f}%)")
        print()
        
        # Show problems first (most important)
        if comment_analysis['problems']:
            print("🚨 PROBLEMS AND ISSUES (Top 10):")
            print("-" * 80)
            for i, problem in enumerate(comment_analysis['problems'][:10], 1):
                print(f"{i}. {problem}")
            if len(comment_analysis['problems']) > 10:
                print(f"... and {len(comment_analysis['problems']) - 10} more problems")
            print()
        
        if comment_analysis['themes']:
            print("📊 Recurring Themes:")
            print("-" * 80)
            
            for i, theme_data in enumerate(comment_analysis['themes'][:8], 1):
                theme = theme_data['theme']
                count = theme_data['count']
                percentage = theme_data['percentage']
                examples = theme_data['examples']
                
                print(f"{i}. {theme}")
                print(f"   Mentioned in: {count} comments ({percentage:.1f}%)")
                
                if examples and len(examples) > 0:
                    print(f"   Example: \"{examples[0]}\"")
                print()
    else:
        print("=" * 80)
        print("2. ANNOTATOR COMMENTS ANALYSIS")
        print("=" * 80)
        print()
        print("No comments found in the spreadsheet.")
        print()


def generate_markdown_report(analysis: Dict, comment_analysis: Dict, all_comments: Dict, output_file: str):
    """
    Generate a comprehensive markdown report of the tournament results.
    """
    strategy_names = {
        'strategy1': 'Strategy 1 (Chain of Thought)',
        'strategy2': 'Strategy 2 (Few-shot)',
        'strategy3': 'Strategy 3 (Validation)'
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# Prompt Tournament Results\n\n")
        f.write(f"**Date**: {os.popen('date').read().strip()}\n\n")
        
        # Executive Summary
        f.write("## Executive Summary\n\n")
        f.write(f"- **Total Evaluators**: {analysis['total_evaluators']}\n")
        f.write(f"- **Total Textbooks**: {analysis['total_textbooks']}\n")
        f.write(f"- **Total Votes Cast**: {analysis['total_votes_cast']}\n")
        f.write(f"- **Total Comments**: {comment_analysis['total_comments']}\n\n")
        
        # Winner
        sorted_by_votes = sorted(analysis['total_votes'].items(), key=lambda x: x[1], reverse=True)
        winner_strategy, winner_votes = sorted_by_votes[0]
        winner_percentage = analysis['vote_percentages'][winner_strategy]
        
        f.write(f"### 🏆 Winner: {strategy_names[winner_strategy]}\n\n")
        f.write(f"- **{winner_votes}** votes out of {analysis['total_votes_cast']} ({winner_percentage:.1f}%)\n")
        f.write(f"- Won **{analysis['textbook_wins'].get(winner_strategy, 0)}** out of {analysis['total_textbooks']} textbooks\n\n")
        
        # Strategy Rankings
        f.write("## Strategy Rankings\n\n")
        f.write("### By Total Votes\n\n")
        
        for rank, (strategy, votes) in enumerate(sorted_by_votes, 1):
            percentage = analysis['vote_percentages'][strategy]
            full_name = strategy_names.get(strategy, strategy)
            textbook_wins = analysis['textbook_wins'].get(strategy, 0)
            
            medal = "🥇" if rank == 1 else "🥈" if rank == 2 else "🥉"
            f.write(f"#### {medal} Rank {rank}: {full_name}\n\n")
            f.write(f"- **Total Votes**: {votes} out of {analysis['total_votes_cast']} ({percentage:.1f}%)\n")
            f.write(f"- **Textbooks Won**: {textbook_wins} out of {analysis['total_textbooks']}\n")
            
            if rank < len(sorted_by_votes):
                next_strategy, next_votes = sorted_by_votes[rank]
                margin = votes - next_votes
                f.write(f"- **Margin over Rank {rank+1}**: +{margin} votes\n")
            f.write("\n")
        
        # Detailed Results by Textbook
        f.write("## Detailed Results by Textbook\n\n")
        
        for result in analysis['detailed_results']:
            textbook = result['textbook']
            winner = result['winner']
            votes = result['votes']
            total = result['total_evaluators']
            
            full_name = strategy_names.get(winner, winner)
            
            f.write(f"### {textbook}\n\n")
            f.write(f"**Winner**: {full_name}\n\n")
            f.write("**Vote Breakdown**:\n\n")
            
            for strat, vote_count in sorted(votes.items(), key=lambda x: x[1], reverse=True):
                strat_name = strategy_names.get(strat, strat)
                percentage = (vote_count / total * 100) if total > 0 else 0
                f.write(f"- {strat_name}: **{vote_count}/{total}** ({percentage:.1f}%)\n")
            f.write("\n")
        
        # Comment Analysis
        f.write("## Annotator Comments Analysis\n\n")
        f.write(f"**Total Comments**: {comment_analysis['total_comments']}\n\n")
        
        if comment_analysis['total_comments'] > 0:
            # Comment breakdown
            f.write("### Comment Breakdown\n\n")
            f.write(f"- 🚨 **Problems/Issues**: {len(comment_analysis['problems'])} ({len(comment_analysis['problems'])/comment_analysis['total_comments']*100:.1f}%)\n")
            f.write(f"- ✅ **Strengths**: {len(comment_analysis['strengths'])} ({len(comment_analysis['strengths'])/comment_analysis['total_comments']*100:.1f}%)\n")
            f.write(f"- 📝 **Observations**: {len(comment_analysis['observations'])} ({len(comment_analysis['observations'])/comment_analysis['total_comments']*100:.1f}%)\n\n")
            
            # Problems
            if comment_analysis['problems']:
                f.write("### 🚨 Problems and Issues\n\n")
                for i, problem in enumerate(comment_analysis['problems'], 1):
                    f.write(f"{i}. {problem}\n")
                f.write("\n")
            
            # Recurring Themes
            if comment_analysis['themes']:
                f.write("### 📊 Recurring Themes\n\n")
                for i, theme_data in enumerate(comment_analysis['themes'], 1):
                    theme = theme_data['theme']
                    count = theme_data['count']
                    percentage = theme_data['percentage']
                    examples = theme_data['examples']
                    
                    f.write(f"#### {i}. {theme}\n\n")
                    f.write(f"Mentioned in **{count}** comments ({percentage:.1f}%)\n\n")
                    
                    if examples:
                        f.write("**Examples**:\n\n")
                        for ex in examples:
                            f.write(f"- {ex}\n")
                        f.write("\n")
            
            # Strengths
            if comment_analysis['strengths']:
                f.write("### ✅ Strengths Noted\n\n")
                for i, strength in enumerate(comment_analysis['strengths'][:15], 1):
                    f.write(f"{i}. {strength}\n")
                f.write("\n")
            
            # All comments by textbook
            f.write("### All Comments by Textbook\n\n")
            for textbook, comments in sorted(all_comments.items()):
                f.write(f"#### {textbook}\n\n")
                for comment in comments:
                    f.write(f"- {comment}\n")
                f.write("\n")
    
    print(f"✅ Markdown report generated: {output_file}")


def organize_comments_by_actual_strategy(comments_by_textbook: Dict[str, List[str]], 
                                         mapping_data: Dict) -> Dict[str, List[str]]:
    """
    Organize comments by actual strategy (unshuffled).
    Parse comments to identify which shuffled strategy they mention,
    then map to the actual strategy.
    
    Args:
        comments_by_textbook: Comments organized by textbook
        mapping_data: Tournament mapping data
    
    Returns:
        Dictionary mapping actual strategy to list of comments about it
    """
    import re
    
    comments_by_actual_strategy = {
        'strategy1': [],
        'strategy2': [],
        'strategy3': []
    }
    
    strategy_mention_pattern = re.compile(r'\b[Ss]trategy\s*([123])\b')
    
    for textbook, comments in comments_by_textbook.items():
        # Get the mapping for this textbook
        textbook_mapping = None
        for item in mapping_data['textbooks']:
            if item['textbook'] == textbook:
                textbook_mapping = item['mapping']
                break
        
        if not textbook_mapping:
            continue
        
        for comment in comments:
            # Find all strategy mentions in the comment
            matches = strategy_mention_pattern.findall(comment)
            
            if matches:
                # Get unique strategies mentioned
                strategies_mentioned = set(matches)
                
                for shuffled_num in strategies_mentioned:
                    # Map shuffled column to actual strategy
                    column_index = int(shuffled_num) - 1
                    if 0 <= column_index < len(textbook_mapping):
                        actual_strategy = textbook_mapping[column_index]
                        
                        # Add comment with context
                        context = f"[{textbook}] {comment}"
                        if context not in comments_by_actual_strategy[actual_strategy]:
                            comments_by_actual_strategy[actual_strategy].append(context)
            else:
                # Comment doesn't mention a specific strategy, add to all
                for strategy in ['strategy1', 'strategy2', 'strategy3']:
                    context = f"[{textbook}] {comment}"
                    if context not in comments_by_actual_strategy[strategy]:
                        comments_by_actual_strategy[strategy].append(context)
    
    return comments_by_actual_strategy


def export_comments_for_llm(comment_analysis: Dict, output_file: str):
    """
    Export all comments in a format optimized for LLM analysis.
    """
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# Prompt Tournament - Annotator Comments\n")
        f.write("# Format: Each comment is on a separate line\n")
        f.write("# Use this file for further LLM analysis\n\n")
        f.write("=" * 80 + "\n")
        f.write("PROBLEMS AND ISSUES\n")
        f.write("=" * 80 + "\n\n")
        
        for problem in comment_analysis.get('problems', []):
            f.write(f"{problem}\n\n")
        
        f.write("=" * 80 + "\n")
        f.write("STRENGTHS\n")
        f.write("=" * 80 + "\n\n")
        
        for strength in comment_analysis.get('strengths', []):
            f.write(f"{strength}\n\n")
        
        f.write("=" * 80 + "\n")
        f.write("OBSERVATIONS\n")
        f.write("=" * 80 + "\n\n")
        
        for obs in comment_analysis.get('observations', []):
            f.write(f"{obs}\n\n")
        
        f.write("=" * 80 + "\n")
        f.write("ALL COMMENTS (UNSORTED)\n")
        f.write("=" * 80 + "\n\n")
        
        for comment in comment_analysis.get('all_comments', []):
            f.write(f"{comment}\n\n")
    
    print(f"✅ Comments exported for LLM: {output_file}")


def export_comments_by_strategy(comments_by_strategy: Dict[str, List[str]], output_file: str):
    """
    Export comments organized by actual (unshuffled) strategy.
    """
    strategy_names = {
        'strategy1': 'Strategy 1 (Chain of Thought)',
        'strategy2': 'Strategy 2 (Few-shot)',
        'strategy3': 'Strategy 3 (Validation)'
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# Comments Organized by Actual Strategy (Unshuffled)\n\n")
        f.write("This file organizes all comments by the ACTUAL strategy they refer to,\n")
        f.write("not the shuffled column names shown to evaluators.\n\n")
        f.write("When evaluators said 'Strategy 1', 'Strategy 2', or 'Strategy 3' in their\n")
        f.write("comments, those referred to shuffled columns. This file maps those back to\n")
        f.write("the actual strategies.\n\n")
        
        for strategy in ['strategy1', 'strategy2', 'strategy3']:
            full_name = strategy_names[strategy]
            comments = comments_by_strategy[strategy]
            
            f.write("=" * 80 + "\n")
            f.write(f"{full_name.upper()}\n")
            f.write("=" * 80 + "\n\n")
            f.write(f"Total comments mentioning this strategy: {len(comments)}\n\n")
            
            if comments:
                for i, comment in enumerate(comments, 1):
                    f.write(f"{i}. {comment}\n\n")
            else:
                f.write("No comments found mentioning this strategy.\n\n")
            
            f.write("\n")
    
    print(f"✅ Comments by strategy exported: {output_file}")


def automated_mode(single_sheet: str = None):
    """
    Automated mode - fetches data directly from Google Sheets (ALL tabs).
    
    Args:
        single_sheet: If provided, only read this sheet. Otherwise read all sheets.
    """
    print("=" * 80)
    print("PROMPT TOURNAMENT - AUTOMATED RESULTS ANALYZER")
    print("=" * 80)
    print()
    
    # Load mapping
    try:
        mapping_data = load_tournament_mapping()
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return
    
    print(f"Loaded mapping for {len(mapping_data['textbooks'])} textbooks")
    print(f"Spreadsheet URL: {mapping_data['spreadsheet_url']}")
    print(f"Spreadsheet ID: {mapping_data['spreadsheet_id']}")
    print()
    
    # Fetch data from Google Sheets
    try:
        if single_sheet:
            print(f"Fetching data from single sheet: {single_sheet}")
            sheet_data = fetch_sheet_data(mapping_data['spreadsheet_id'], single_sheet)
            if not sheet_data:
                print("Error: Could not fetch data from the specified sheet.")
                return
            all_sheets_data = {single_sheet: sheet_data}
        else:
            print("Fetching data from ALL sheets (all evaluators)...")
            all_sheets_data = fetch_all_sheets_data(mapping_data['spreadsheet_id'])
        
        if not all_sheets_data:
            print("Error: Could not fetch any data from Google Sheets.")
            return
            
    except Exception as e:
        print(f"Error fetching data from Google Sheets: {e}")
        print()
        print("=" * 80)
        print("ALTERNATIVE: CSV IMPORT MODE")
        print("=" * 80)
        print()
        print("You can export each evaluator's sheet as CSV and combine them:")
        print("See QUICK_START.md for detailed instructions on CSV export.")
        print()
        return
    
    print(f"Successfully fetched data from {len(all_sheets_data)} evaluator sheet(s)")
    print()
    
    # Aggregate selections and comments from all evaluators
    all_selections, all_comments = aggregate_all_evaluators(all_sheets_data)
    
    if not all_selections:
        print("Warning: No selections found in any sheet.")
        print("Please check that sheets have 'Selection' or 'Preferred' columns with data.")
        return
    
    total_votes = sum(len(votes) for votes in all_selections.values())
    print(f"Aggregated {total_votes} votes across {len(all_selections)} textbooks from {len(all_sheets_data)} evaluators")
    print(f"Found {sum(len(c) for c in all_comments.values())} comments")
    print()
    
    # Analyze results
    analysis = analyze_results(all_selections, mapping_data)
    comment_analysis = analyze_comments(all_comments)
    
    # Print results
    print_results(analysis, comment_analysis)
    
    # Save results
    results_file = os.path.join(os.path.dirname(__file__), 'tournament_results.json')
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump({
            'all_selections': all_selections,
            'analysis': analysis,
            'comment_analysis': comment_analysis,
            'comments_by_textbook': all_comments
        }, f, indent=2)
    
    # Generate markdown report
    markdown_file = os.path.join(os.path.dirname(__file__), 'tournament_results.md')
    generate_markdown_report(analysis, comment_analysis, all_comments, markdown_file)
    
    # Generate separate comments file for LLM analysis
    comments_file = os.path.join(os.path.dirname(__file__), 'tournament_comments.txt')
    export_comments_for_llm(comment_analysis, comments_file)
    
    # Organize comments by actual strategy (unshuffled)
    comments_by_strategy = organize_comments_by_actual_strategy(all_comments, mapping_data)
    strategy_comments_file = os.path.join(os.path.dirname(__file__), 'comments_by_strategy.txt')
    export_comments_by_strategy(comments_by_strategy, strategy_comments_file)
    
    print("=" * 80)
    print(f"📄 Results saved to:")
    print(f"   - JSON: {results_file}")
    print(f"   - Markdown Report: {markdown_file}")
    print(f"   - Comments for LLM: {comments_file}")
    print(f"   - Comments by Strategy: {strategy_comments_file}")
    print("=" * 80)
    print()


def interactive_mode():
    """
    Interactive mode to manually input selections from Google Sheets.
    """
    print("=" * 80)
    print("PROMPT TOURNAMENT - RESULTS ANALYZER (Interactive Mode)")
    print("=" * 80)
    print()
    
    # Load mapping
    try:
        mapping_data = load_tournament_mapping()
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return
    
    print(f"Loaded mapping for {len(mapping_data['textbooks'])} textbooks")
    print(f"Spreadsheet URL: {mapping_data['spreadsheet_url']}")
    print()
    
    # Get selections from user
    selections = {}
    
    print("For each textbook, enter which column was selected (1, 2, or 3)")
    print("Or type 'skip' to skip a textbook, or 'done' when finished")
    print()
    
    for item in mapping_data['textbooks']:
        textbook_name = item['textbook']
        
        while True:
            response = input(f"{textbook_name} - Selected column (1/2/3/skip): ").strip().lower()
            
            if response == 'skip':
                break
            elif response == 'done':
                break
            elif response in ['1', '2', '3']:
                column_name = f"Strategy {response}"
                selections[textbook_name] = column_name
                break
            else:
                print("  Invalid input. Please enter 1, 2, 3, 'skip', or 'done'")
        
        if response == 'done':
            break
    
    if not selections:
        print("No selections entered. Exiting.")
        return
    
    print()
    
    # Analyze results
    analysis = analyze_results(selections, mapping_data)
    
    # Print results
    print_results(analysis)
    
    # Save results
    results_file = os.path.join(os.path.dirname(__file__), 'tournament_results.json')
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump({
            'selections': selections,
            'analysis': analysis
        }, f, indent=2)
    
    print(f"Results saved to: {results_file}")
    print()


def csv_mode(csv_files: List[str]):
    """
    CSV mode - loads data from CSV file(s).
    
    Args:
        csv_files: List of CSV file paths (one per evaluator)
    """
    print("=" * 80)
    print("PROMPT TOURNAMENT - CSV IMPORT MODE")
    print("=" * 80)
    print()
    
    # Load mapping
    try:
        mapping_data = load_tournament_mapping()
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return
    
    print(f"Loaded mapping for {len(mapping_data['textbooks'])} textbooks")
    print()
    
    # Load all CSV files
    all_sheets_data = {}
    
    for csv_file in csv_files:
        print(f"Loading data from CSV: {csv_file}")
        try:
            sheet_data = load_csv_data(csv_file)
            evaluator_name = os.path.basename(csv_file).replace('.csv', '')
            all_sheets_data[evaluator_name] = sheet_data
            print(f"  ✓ Loaded {len(sheet_data)} rows")
        except FileNotFoundError as e:
            print(f"  ✗ Error: {e}")
            continue
        except Exception as e:
            print(f"  ✗ Error reading CSV: {e}")
            continue
    
    if not all_sheets_data:
        print("Error: Could not load any CSV files.")
        return
    
    print()
    print(f"Successfully loaded data from {len(all_sheets_data)} CSV file(s)")
    print()
    
    # Aggregate selections and comments from all evaluators
    all_selections, all_comments = aggregate_all_evaluators(all_sheets_data)
    
    if not all_selections:
        print("Warning: No selections found in any CSV.")
        print("Please check that CSVs have 'Selection' or 'Preferred' columns with data.")
        return
    
    total_votes = sum(len(votes) for votes in all_selections.values())
    print(f"Aggregated {total_votes} votes across {len(all_selections)} textbooks from {len(all_sheets_data)} evaluators")
    print(f"Found {sum(len(c) for c in all_comments.values())} comments")
    print()
    
    # Analyze results
    analysis = analyze_results(all_selections, mapping_data)
    comment_analysis = analyze_comments(all_comments)
    
    # Print results
    print_results(analysis, comment_analysis)
    
    # Save results
    results_file = os.path.join(os.path.dirname(__file__), 'tournament_results.json')
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump({
            'all_selections': all_selections,
            'analysis': analysis,
            'comment_analysis': comment_analysis,
            'comments_by_textbook': all_comments
        }, f, indent=2)
    
    # Generate markdown report
    markdown_file = os.path.join(os.path.dirname(__file__), 'tournament_results.md')
    generate_markdown_report(analysis, comment_analysis, all_comments, markdown_file)
    
    # Generate separate comments file for LLM analysis
    comments_file = os.path.join(os.path.dirname(__file__), 'tournament_comments.txt')
    export_comments_for_llm(comment_analysis, comments_file)
    
    # Organize comments by actual strategy (unshuffled)
    comments_by_strategy = organize_comments_by_actual_strategy(all_comments, mapping_data)
    strategy_comments_file = os.path.join(os.path.dirname(__file__), 'comments_by_strategy.txt')
    export_comments_by_strategy(comments_by_strategy, strategy_comments_file)
    
    print("=" * 80)
    print(f"📄 Results saved to:")
    print(f"   - JSON: {results_file}")
    print(f"   - Markdown Report: {markdown_file}")
    print(f"   - Comments for LLM: {comments_file}")
    print(f"   - Comments by Strategy: {strategy_comments_file}")
    print("=" * 80)
    print()


def main():
    """
    Main function - runs automated mode by default (reads ALL sheets).
    
    Usage:
        python analyze_tournament_results.py                    # Read all sheets/tabs (all evaluators)
        python analyze_tournament_results.py --sheet "Name"     # Read only one specific sheet
        python analyze_tournament_results.py --csv file1.csv file2.csv ...  # Load from CSV files
        python analyze_tournament_results.py --interactive      # Manual input mode
    """
    import sys
    
    # Check for command line arguments
    if '--interactive' in sys.argv:
        interactive_mode()
    elif '--csv' in sys.argv:
        # CSV mode - collect all CSV files
        try:
            csv_idx = sys.argv.index('--csv')
            # Collect all arguments after --csv that don't start with --
            csv_files = []
            for i in range(csv_idx + 1, len(sys.argv)):
                if sys.argv[i].startswith('--'):
                    break
                csv_files.append(sys.argv[i])
            
            if not csv_files:
                print("Error: --csv requires at least one file path")
                print("Usage: python analyze_tournament_results.py --csv file1.csv [file2.csv ...]")
            else:
                csv_mode(csv_files)
        except (ValueError, IndexError):
            print("Error: --csv requires at least one file path")
            print("Usage: python analyze_tournament_results.py --csv file1.csv [file2.csv ...]")
    else:
        # Default to automated mode (ALL sheets)
        single_sheet = None
        
        # Check if user wants only a specific sheet
        if '--sheet' in sys.argv:
            try:
                sheet_idx = sys.argv.index('--sheet')
                if sheet_idx + 1 < len(sys.argv):
                    single_sheet = sys.argv[sheet_idx + 1]
            except (ValueError, IndexError):
                pass
        
        automated_mode(single_sheet)


if __name__ == '__main__':
    main()
