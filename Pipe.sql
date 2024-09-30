To select columns from 1 to 28 from a pipe-separated string in BigQuery, you can use the `SPLIT()` function and `SAFE_OFFSET` for each column. Here’s the SQL code:

```sql
SELECT
  SPLIT(column_with_pipes, '|')[SAFE_OFFSET(0)] AS column_1,
  SPLIT(column_with_pipes, '|')[SAFE_OFFSET(1)] AS column_2,
  SPLIT(column_with_pipes, '|')[SAFE_OFFSET(2)] AS column_3,
  SPLIT(column_with_pipes, '|')[SAFE_OFFSET(3)] AS column_4,
  SPLIT(column_with_pipes, '|')[SAFE_OFFSET(4)] AS column_5,
  SPLIT(column_with_pipes, '|')[SAFE_OFFSET(5)] AS column_6,
  SPLIT(column_with_pipes, '|')[SAFE_OFFSET(6)] AS column_7,
  SPLIT(column_with_pipes, '|')[SAFE_OFFSET(7)] AS column_8,
  SPLIT(column_with_pipes, '|')[SAFE_OFFSET(8)] AS column_9,
  SPLIT(column_with_pipes, '|')[SAFE_OFFSET(9)] AS column_10,
  SPLIT(column_with_pipes, '|')[SAFE_OFFSET(10)] AS column_11,
  SPLIT(column_with_pipes, '|')[SAFE_OFFSET(11)] AS column_12,
  SPLIT(column_with_pipes, '|')[SAFE_OFFSET(12)] AS column_13,
  SPLIT(column_with_pipes, '|')[SAFE_OFFSET(13)] AS column_14,
  SPLIT(column_with_pipes, '|')[SAFE_OFFSET(14)] AS column_15,
  SPLIT(column_with_pipes, '|')[SAFE_OFFSET(15)] AS column_16,
  SPLIT(column_with_pipes, '|')[SAFE_OFFSET(16)] AS column_17,
  SPLIT(column_with_pipes, '|')[SAFE_OFFSET(17)] AS column_18,
  SPLIT(column_with_pipes, '|')[SAFE_OFFSET(18)] AS column_19,
  SPLIT(column_with_pipes, '|')[SAFE_OFFSET(19)] AS column_20,
  SPLIT(column_with_pipes, '|')[SAFE_OFFSET(20)] AS column_21,
  SPLIT(column_with_pipes, '|')[SAFE_OFFSET(21)] AS column_22,
  SPLIT(column_with_pipes, '|')[SAFE_OFFSET(22)] AS column_23,
  SPLIT(column_with_pipes, '|')[SAFE_OFFSET(23)] AS column_24,
  SPLIT(column_with_pipes, '|')[SAFE_OFFSET(24)] AS column_25,
  SPLIT(column_with_pipes, '|')[SAFE_OFFSET(25)] AS column_26,
  SPLIT(column_with_pipes, '|')[SAFE_OFFSET(26)] AS column_27,
  SPLIT(column_with_pipes, '|')[SAFE_OFFSET(27)] AS column_28
FROM
  your_table;
```

### Explanation:
- The `SPLIT(column_with_pipes, '|')` function splits the string by `|`.
- The `SAFE_OFFSET(n)` extracts the `n+1`th element from the array (since BigQuery arrays are zero-indexed).
- This query extracts columns 1 to 28 safely, where each column is represented by its respective index.

Replace `your_table` with your actual table name and `column_with_pipes` with the relevant column containing pipe-separated values.
