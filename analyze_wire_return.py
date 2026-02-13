#!/usr/bin/env python3
"""
Column Payment Operations Database Analysis
Question 1: Wire Return Investigation
"""

import sqlite3
import json
from datetime import datetime

DB_PATH = './payment_ops_db'  

def connect_to_database():
    """Connect to the SQLite database"""
    try:
        conn = sqlite3.connect(DB_PATH)
        print(f"Successfully connected to database: {DB_PATH}\n")
        return conn
    except Exception as e:
        print(f"Error connecting to database: {e}")
        print(f"Make sure the file exists at: {DB_PATH}")
        return None

def explore_database(conn):
    """Show basic database information"""
    cursor = conn.cursor()
    
    # List all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    print("=== DATABASE TABLES ===")
    for table in tables:
        print(f"  • {table[0]}")
    
    # Show wire_transfers schema
    cursor.execute("SELECT sql FROM sqlite_master WHERE name='wire_transfers'")
    schema = cursor.fetchone()
    print("\n=== WIRE_TRANSFERS TABLE SCHEMA ===")
    print(schema[0])
    print()

def query_returned_wire(conn, wire_id):
    """Query the returned wire transfer"""
    cursor = conn.cursor()
    
    query = """
    SELECT * 
    FROM wire_transfers 
    WHERE wire_transfer_id = ?
    """
    
    print(f"=== QUERY 1: RETURNED WIRE ===")
    print(f"SQL: {query}")
    print(f"Parameter: {wire_id}\n")
    
    cursor.execute(query, (wire_id,))
    columns = [description[0] for description in cursor.description]
    result = cursor.fetchone()
    
    if result:
        returned_wire = dict(zip(columns, result))
        print("Found returned wire:")
        print(json.dumps(returned_wire, indent=2))
        return returned_wire
    else:
        print("No wire found with that ID")
        return None

def query_original_wire(conn, amount):
    """Find the original outgoing wire"""
    cursor = conn.cursor()
    
    query = """
    SELECT * 
    FROM wire_transfers 
    WHERE amount = ?
      AND is_incoming = '0'
    """
    
    print(f"\n=== QUERY 2: ORIGINAL OUTGOING WIRE ===")
    print(f"SQL: {query}")
    print(f"Parameter: amount = {amount}\n")
    
    cursor.execute(query, (amount,))
    columns = [description[0] for description in cursor.description]
    result = cursor.fetchone()
    
    if result:
        original_wire = dict(zip(columns, result))
        print("Found original wire:")
        print(json.dumps(original_wire, indent=2))
        return original_wire
    else:
        print("No matching outgoing wire found")
        return None

def parse_return_reason(bank_message):
    """Parse the bank-to-bank message to extract return reason"""
    try:
        msg = json.loads(bank_message)
        return_info = msg.get('fiToFI', {})
        return {
            'code': return_info.get('lineFour', 'N/A'),
            'reason': return_info.get('lineThree', 'N/A'),
            'full_message': return_info
        }
    except:
        return {'code': 'N/A', 'reason': 'Unable to parse', 'full_message': {}}

def format_amount(amount_str):
    """Format amount as currency"""
    try:
        return f"${float(amount_str)/100:,.2f}"
    except:
        return amount_str

def format_timestamp(timestamp_str):
    """Format timestamp for readability"""
    try:
        dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        return dt.strftime('%Y-%m-%d %H:%M:%S UTC')
    except:
        return timestamp_str

def generate_summary(original, returned):
    """Generate a summary report"""
    print("\n" + "="*70)
    print("SUMMARY REPORT")
    print("="*70)
    
    # Parse return reason
    return_details = parse_return_reason(returned['bank_to_bank_message'])
    
    print(f"\nORIGINAL OUTGOING WIRE")
    print(f"   Wire Transfer ID: {original['wire_transfer_id']}")
    print(f"   Sent at:          {format_timestamp(original['completed_at'])}")
    print(f"   Amount:           {format_amount(original['amount'])}")
    print(f"   Direction:        Outgoing")
    
    print(f"\nRETURNED WIRE")
    print(f"   Wire Transfer ID: {returned['wire_transfer_id']}")
    print(f"   Returned at:      {format_timestamp(returned['completed_at'])}")
    print(f"   Amount:           {format_amount(returned['amount'])}")
    print(f"   Direction:        Incoming (Return)")
    
    print(f"\nRETURN REASON")
    print(f"   Return Code:      {return_details['code']}")
    print(f"   Reason:           {return_details['reason']}")
    print(f"   Full Message:     {json.dumps(return_details['full_message'], indent=21)}")
    
    # Calculate time difference
    try:
        orig_time = datetime.fromisoformat(original['completed_at'].replace('Z', '+00:00'))
        ret_time = datetime.fromisoformat(returned['completed_at'].replace('Z', '+00:00'))
        time_diff = ret_time - orig_time
        hours = time_diff.total_seconds() / 3600
        print(f"\nTIME TO RETURN:    {hours:.2f} hours ({time_diff})")
    except:
        pass
    
    print("\n" + "="*70)

def main():
    """Main execution function"""
    print("="*70)
    print("COLUMN PAYMENT OPERATIONS - WIRE RETURN ANALYSIS")
    print("="*70)
    print()
    
    # Customer's wire ID
    RETURNED_WIRE_ID = 'wire_2QIZQwWo3bXp4aP5NUKFDJAXw4k'
    
    # Connect to database
    conn = connect_to_database()
    if not conn:
        return
    
    try:
        # Explore database structure
        explore_database(conn)
        
        # Query the returned wire
        returned_wire = query_returned_wire(conn, RETURNED_WIRE_ID)
        if not returned_wire:
            return
        
        # Find the original wire
        original_wire = query_original_wire(conn, returned_wire['amount'])
        if not original_wire:
            return
        
        # Generate summary
        generate_summary(original_wire, returned_wire)
        
    finally:
        conn.close()
        print("\nDatabase connection closed")

if __name__ == "__main__":
    main()