
# Data Cleaning Documentation

## Project
E-Commerce Customer 360 Analytics & Intelligent Retention Strategy

## Dataset
Brazilian E-Commerce Public Dataset by Olist

## Cleaning operations

1. Loaded all nine original CSV datasets.
2. Removed exact duplicate records.
3. Standardized text fields by trimming whitespace.
4. Converted date columns to datetime format.
5. Converted numerical columns to appropriate numeric types.
6. Created business rule validation flags.
7. Checked primary key uniqueness.
8. Checked referential integrity between related tables.
9. Generated data quality reports.
10. Exported cleaned datasets separately.

## Data preservation policy

Original raw datasets remain unchanged.

Invalid and suspicious records are flagged for investigation
rather than automatically deleted.

## Output

Cleaned datasets are stored in data/processed/.

Validation reports are stored in reports/.
