-- Column Payment Operations Database Queries
-- Question 1: Wire Return Investigation
-- Wire ID: wire_2QIZQwWo3bXp4aP5NUKFDJAXw4k

-- ===================================================================
-- EXPLORATION QUERIES
-- ===================================================================

-- List all tables in the database
SELECT name FROM sqlite_master WHERE type='table';

-- Get schema for wire_transfers table
SELECT sql FROM sqlite_master WHERE name='wire_transfers';

-- Count total wire transfers
SELECT COUNT(*) as total_wires FROM wire_transfers;

-- Count incoming vs outgoing wires
SELECT 
    CASE 
        WHEN is_incoming = '1' THEN 'Incoming'
        WHEN is_incoming = '0' THEN 'Outgoing'
    END as direction,
    COUNT(*) as count
FROM wire_transfers
GROUP BY is_incoming;

-- ===================================================================
-- QUERY 1: Get the Returned Wire Details
-- ===================================================================

SELECT * 
FROM wire_transfers 
WHERE wire_transfer_id = 'wire_2QIZQwWo3bXp4aP5NUKFDJAXw4k';

-- Expected Result:
-- wire_transfer_id: wire_2QIZQwWo3bXp4aP5NUKFDJAXw4k
-- completed_at: 2023-05-25T19:30:44.000Z
-- amount: 183639
-- is_incoming: 1 (this is a return - incoming)
-- bank_to_bank_message: Contains return code 41 and "INVALID ACCT"

-- ===================================================================
-- QUERY 2: Find the Original Outgoing Wire
-- ===================================================================

-- Method 1: Search by amount (most reliable)
SELECT * 
FROM wire_transfers 
WHERE amount = '183639'
  AND is_incoming = '0';

-- Method 2: Search by date and amount (more specific)
SELECT * 
FROM wire_transfers 
WHERE amount = '183639'
  AND is_incoming = '0'
  AND date(completed_at) = '2023-05-25';

-- Expected Result:
-- wire_transfer_id: wire_2QIP3WQNoEe583ciCS98XFBVq1d
-- completed_at: 2023-05-25T18:05:26.000Z
-- amount: 183639
-- is_incoming: 0 (this is the original outgoing wire)

-- ===================================================================
-- ANALYSIS QUERIES
-- ===================================================================

-- View both wires side by side
SELECT 
    wire_transfer_id,
    completed_at,
    amount,
    CASE 
        WHEN is_incoming = '1' THEN 'Incoming (Return)'
        WHEN is_incoming = '0' THEN 'Outgoing'
    END as direction,
    bank_to_bank_message
FROM wire_transfers 
WHERE wire_transfer_id IN (
    'wire_2QIZQwWo3bXp4aP5NUKFDJAXw4k',  -- Returned wire
    'wire_2QIP3WQNoEe583ciCS98XFBVq1d'   -- Original wire
)
ORDER BY completed_at;

-- Find all wires on the same day
SELECT 
    wire_transfer_id,
    completed_at,
    amount,
    CASE 
        WHEN is_incoming = '1' THEN 'Incoming'
        WHEN is_incoming = '0' THEN 'Outgoing'
    END as direction
FROM wire_transfers 
WHERE date(completed_at) = '2023-05-25'
  AND amount = '183639'
ORDER BY completed_at;

-- Summary statistics
SELECT 
    COUNT(*) as total_wires,
    SUM(CASE WHEN is_incoming = '0' THEN 1 ELSE 0 END) as outgoing_count,
    SUM(CASE WHEN is_incoming = '1' THEN 1 ELSE 0 END) as incoming_count,
    SUM(CAST(amount AS REAL))/100 as total_amount_dollars
FROM wire_transfers
WHERE date(completed_at) = '2023-05-25';