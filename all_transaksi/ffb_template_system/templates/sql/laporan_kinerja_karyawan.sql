-- =====================================================
-- LAPORAN KINERJA KERANI, MANDOR, DAN ASISTEN
-- Template SQL untuk FFB Analysis Multi-Estate
-- =====================================================

-- Parameters:
-- ${START_DATE} - Start date (YYYY-MM-DD)
-- ${END_DATE} - End date (YYYY-MM-DD)
-- ${ESTATE_LIST} - Comma-separated list of estates
-- ${USE_STATUS_704_FILTER} - Boolean for May filter
-- ${MONTH_TABLES} - Dynamic month tables

-- =====================================================
-- MAIN ANALYSIS QUERY
-- =====================================================

-- Get employee mapping
WITH employee_mapping AS (
    SELECT
        ID as EMP_ID,
        NAME as EMP_NAME
    FROM EMP
    WHERE ID IS NOT NULL
),

-- Get all FFB transaction data for the period
all_transactions AS (
    SELECT
        a.ID,
        a.SCANUSERID,
        a.OCID,
        a.WORKERID,
        a.CARRIERID,
        a.FIELDID,
        a.TASKNO,
        a.RIPEBCH,
        a.UNRIPEBCH,
        a.BLACKBCH,
        a.ROTTENBCH,
        a.LONGSTALKBCH,
        a.RATDMGBCH,
        a.LOOSEFRUIT,
        a.TRANSNO,
        a.TRANSDATE,
        a.TRANSTIME,
        a.UPLOADDATETIME,
        a.RECORDTAG,
        a.TRANSSTATUS,
        a.TRANSTYPE,
        a.LASTUSER,
        a.LASTUPDATED,
        a.OVERRIPEBCH,
        a.UNDERRIPEBCH,
        a.ABNORMALBCH,
        a.LOOSEFRUIT2,
        b.DIVID,
        c.DIVNAME,
        '${ESTATE_NAME}' as ESTATE_NAME
    FROM FFBSCANNERDATA${MONTH_TABLE} a
    JOIN OCFIELD b ON a.FIELDID = b.ID
    LEFT JOIN CRDIVISION c ON b.DIVID = c.ID
    WHERE b.DIVID IS NOT NULL
        AND c.DIVNAME IS NOT NULL
        AND a.TRANSDATE BETWEEN '${START_DATE}' AND '${END_DATE}'
        ${STATUS_FILTER}
),

-- Find duplicate transactions (verified transactions)
duplicates_check AS (
    SELECT
        TRANSNO,
        COUNT(*) as DUPLICATE_COUNT,
        LIST(DISTINCT RECORDTAG) as RECORD_TYPES
    FROM all_transactions
    GROUP BY TRANSNO
    HAVING COUNT(*) > 1
),

-- Verified transactions (those with duplicates)
verified_transactions AS (
    SELECT
        t.*,
        dc.DUPLICATE_COUNT,
        dc.RECORD_TYPES
    FROM all_transactions t
    JOIN duplicates_check dc ON t.TRANSNO = dc.TRANSNO
),

-- Employee performance calculation
employee_performance AS (
    SELECT
        e.ESTATE_NAME,
        e.DIVID,
        e.DIVNAME,
        e.SCANUSERID,
        COALESCE(em.EMP_NAME, 'EMP-' || e.SCANUSERID) as EMPLOYEE_NAME,

        -- Kerani metrics (RECORDTAG = 'PM')
        COUNT(CASE WHEN e.RECORDTAG = 'PM' THEN 1 END) as KERANI_TRANSACTIONS,

        -- Verified kerani transactions
        COUNT(CASE WHEN e.RECORDTAG = 'PM' AND e.TRANSNO IN (SELECT TRANSNO FROM duplicates_check) THEN 1 END) as KERANI_VERIFIED,

        -- Kerani differences (input variations)
        COUNT(CASE
            WHEN e.RECORDTAG = 'PM' AND e.TRANSNO IN (SELECT TRANSNO FROM duplicates_check)
            AND EXISTS (
                SELECT 1 FROM all_transactions t2
                WHERE t2.TRANSNO = e.TRANSNO
                AND t2.RECORDTAG != 'PM'
                ${STATUS_704_FILTER}
            )
            THEN 1
        END) as KERANI_DIFFERENCES,

        -- Mandor transactions (RECORDTAG = 'P1')
        COUNT(CASE WHEN e.RECORDTAG = 'P1' THEN 1 END) as MANDOR_TRANSACTIONS,

        -- Asisten transactions (RECORDTAG = 'P5')
        COUNT(CASE WHEN e.RECORDTAG = 'P5' THEN 1 END) as ASISTEN_TRANSACTIONS,

        -- Total verification rate
        CASE
            WHEN COUNT(CASE WHEN e.RECORDTAG = 'PM' THEN 1 END) > 0
            THEN ROUND(
                (COUNT(CASE WHEN e.RECORDTAG = 'PM' AND e.TRANSNO IN (SELECT TRANSNO FROM duplicates_check) THEN 1 END) * 100.0) /
                COUNT(CASE WHEN e.RECORDTAG = 'PM' THEN 1 END), 2
            )
            ELSE 0
        END as VERIFICATION_RATE,

        -- Difference rate
        CASE
            WHEN COUNT(CASE WHEN e.RECORDTAG = 'PM' AND e.TRANSNO IN (SELECT TRANSNO FROM duplicates_check) THEN 1 END) > 0
            THEN ROUND(
                (COUNT(CASE
                    WHEN e.RECORDTAG = 'PM' AND e.TRANSNO IN (SELECT TRANSNO FROM duplicates_check)
                    AND EXISTS (
                        SELECT 1 FROM all_transactions t2
                        WHERE t2.TRANSNO = e.TRANSNO
                        AND t2.RECORDTAG != 'PM'
                        ${STATUS_704_FILTER}
                    )
                    THEN 1
                END) * 100.0) /
                COUNT(CASE WHEN e.RECORDTAG = 'PM' AND e.TRANSNO IN (SELECT TRANSNO FROM duplicates_check) THEN 1 END), 2
            )
            ELSE 0
        END as DIFFERENCE_RATE

    FROM all_transactions e
    LEFT JOIN employee_mapping em ON e.SCANUSERID = em.EMP_ID
    GROUP BY e.ESTATE_NAME, e.DIVID, e.DIVNAME, e.SCANUSERID, em.EMP_NAME
)

-- Final result for reporting
SELECT
    ESTATE_NAME,
    DIVID,
    DIVNAME,
    SCANUSERID as EMPLOYEE_ID,
    EMPLOYEE_NAME,
    KERANI_TRANSACTIONS,
    KERANI_VERIFIED,
    KERANI_DIFFERENCES,
    MANDOR_TRANSACTIONS,
    ASISTEN_TRANSACTIONS,
    VERIFICATION_RATE,
    DIFFERENCE_RATE,
    CASE
        WHEN VERIFICATION_RATE >= 95 THEN 'EXCELLENT'
        WHEN VERIFICATION_RATE >= 85 THEN 'GOOD'
        WHEN VERIFICATION_RATE >= 70 THEN 'AVERAGE'
        ELSE 'NEEDS_IMPROVEMENT'
    END as PERFORMANCE_RATING,
    '${START_DATE}' as REPORT_START_DATE,
    '${END_DATE}' as REPORT_END_DATE,
    CURRENT_TIMESTAMP as GENERATED_AT
FROM employee_performance
WHERE KERANI_TRANSACTIONS > 0 OR ${INCLUDE_ZERO_DATA}
ORDER BY ESTATE_NAME, DIVNAME, VERIFICATION_RATE DESC;

-- =====================================================
-- SUMMARY STATISTICS
-- =====================================================

-- Estate Summary
SELECT
    'ESTATE_SUMMARY' as REPORT_TYPE,
    ESTATE_NAME,
    COUNT(*) as TOTAL_EMPLOYEES,
    SUM(KERANI_TRANSACTIONS) as TOTAL_KERANI_TRANSACTIONS,
    SUM(KERANI_VERIFIED) as TOTAL_VERIFIED,
    SUM(KERANI_DIFFERENCES) as TOTAL_DIFFERENCES,
    ROUND(AVG(VERIFICATION_RATE), 2) as AVERAGE_VERIFICATION_RATE,
    ROUND(AVG(DIFFERENCE_RATE), 2) as AVERAGE_DIFFERENCE_RATE,
    COUNT(CASE WHEN VERIFICATION_RATE >= 95 THEN 1 END) as EXCELLENT_PERFORMERS,
    COUNT(CASE WHEN VERIFICATION_RATE < 70 THEN 1 END) as NEEDS_IMPROVEMENT
FROM employee_performance
GROUP BY ESTATE_NAME;

-- Division Summary
SELECT
    'DIVISION_SUMMARY' as REPORT_TYPE,
    ESTATE_NAME,
    DIVID,
    DIVNAME,
    COUNT(*) as TOTAL_EMPLOYEES,
    SUM(KERANI_TRANSACTIONS) as TOTAL_KERANI_TRANSACTIONS,
    SUM(KERANI_VERIFIED) as TOTAL_VERIFIED,
    SUM(KERANI_DIFFERENCES) as TOTAL_DIFFERENCES,
    ROUND(AVG(VERIFICATION_RATE), 2) as AVERAGE_VERIFICATION_RATE,
    ROUND(AVG(DIFFERENCE_RATE), 2) as AVERAGE_DIFFERENCE_RATE
FROM employee_performance
GROUP BY ESTATE_NAME, DIVID, DIVNAME
ORDER BY AVERAGE_VERIFICATION_RATE DESC;