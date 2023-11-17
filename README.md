# dataprep

# Data prepareation python code usage insturction
Our code are implemented in dp.py.

Before using the function, convert name of source file into cmpl_2022_sales.csv and cmpl_2023_sales.csv and kapl_2022_sales.csv since terminal is bad at handling spaces.


## Profiling
this function takes one parameter

### parameter

| parameter     | Description | example|
| :---        |    :--- | :---|
| file1     | relative path that user specify for the source file to be read     | kapl_2023_sales.csv|


### function description
The parameter is a path that user specify. <br>
This is a preliminary profiling of the provided CSV files. It will explore the data's content, structure, and quality, providing a comprehensive data information to next_step data cleaning and structuring.


### Syntax
``` python
python dp.py profiling kapl_2023_sales.csv

python dp.py profiling cmpl_2022_sales.csv

python dp.py profiling cmpl_2023_sales.csv
```

## Functional Dependencies
this function takes only one parameter

### parameter

| parameter     | Description | example|
| :---        |    :--- | :---|
| file1     | relative path that user specify for the source file to be read     | cmpl_converted_2022.csv|



### function description
This function is trying to find the primary key of tables and the relationship between columns. <br>
Firstly, it will check if there are unique values in columns that can specifically identify a recode. If cannot find, it will combine two or three columns to see if it can find the primary key. <br>
Then, it will perform function dependency checks on each pair of data columns and further use union rules. <br>

### Result description
The result from the this function will be printed as the format of <br>
possible primary key column_name/possible combined primary key column_names <br>
column_name → [column_names]
column_name → [column_names]
...

### Syntax
```python
python dp.py functional_dep cmpl_converted_2022.csv

python dp.py functional_dep cmpl_converted_2023.csv

python dp.py functional_dep kapl_converted_2023.csv
```


## Inclusion Dependencies

this function takes three parameters

### parameter

| parameter     | Description | example|
| :---        |    :--- | :---|
| file1     | relative path that user specify for the source file to be read     | ccmpl_converted_2022.csv|
| file2     | relative path that user specify for the source file to be read     | cmpl_converted_2023.csv|
| file3     | relative path that user specify for the source file to be read     | cmpl_converted_2023.csv|


### function description
each of these parameters is a path that user specify. <br>
Firstly, it will perform inclusion dependency analysis within each table.<br>
Then, it will perform unary inclusion dependency test on each pair of data file. With the results, the N-ary test is performed with the selected candidate. <br>

### Result description
The result from the IND test will be printed as the format of <br>
'data_file_1: Column_1 --> data_file_2: Column_2'<br>indicating that col_1 from file_1 is included in col_2 of file_2.

### Syntax
```python 
python dp.py inclusion_dep cmpl_converted_2022.csv cmpl_converted_2023.csv kapl_converted_2023.csv
```

# Cleanning for CMPL files

# create_cmpl_csv and create_kapl_csv
this function takes two parameter

## parameter

| parameter     | Description | example|
| :---        |    :--- | :---|
| source      | relative path that user specify for the source file to be converted     | cmpl_2022_sales.csv|
| desc  | relative path that user specify for the output file destination       | cmpl_converted_2022.csv|

## function description
each of these parameters is a path that user specify.
the source file will be converted to the correct format. We will do a complete handling of missing values of categorical data and numerical data. We also handled date format, unnamed columns, inconsistant names and other errors we detected during profiling,then exported the correct csv file to desc.

## Syntax
```python 
python dp.py create_cmpl_csv cmpl_2022_sales.csv cmpl_converted_2022.csv
python dp.py create_cmpl_csv cmpl_2023_sales.csv cmpl_converted_2023.csv

python dp.py create_kapl_csv kapl_2023_sales.csv kapl_converted_2023.csv
```



# concat_cmpl_csv
## parameter

| parameter     | Description | example|
| :---        |    :--- | :---|
| source1     | path that user specify for the source file to be concatenated     | cmpl_2022_sales.csv|
| source2      | path that user specify for the source file to be concatenated     | cmpl_2023_sales.csv|
| desc  | relative path that user specify for the output file destination       | cmpl_combined_sales.csv|
## function description

source1 and source2 are the cmpl file that need to be concatentate together, and desc is the desctination path for output. Note that each source1 and source2 should be unprocessed ones.

## Syntax
```python 
python dp.py concat_cmpl_csv cmpl_2022_sales.csv cmpl_2023_sales.csv cmpl_combined_sales.csv 
```

### 

## spliting tables
this function takes one parameter

### parameter

| parameter    | Description                                                    | example                |
|:-------------|:---------------------------------------------------------------|:-----------------------|
| file1        | relative path that user specify for the source file to be read | cmpl_converted_2022.csv|
| company_name | specific company the dataset 'file1' came from                 | cmpl                   |


### function description
file1 is the file needed to be split. <br>
company_name is used as part of output file name.

## Syntax
``` python 
python dp.py split_tables cmpl_converted_2022.csv cmpl
```

# Putting the table into Database

## Creating PostgreSQL database

### step 1 open Postgre after installation
``` python
(base) cminus@Mbp ~ % psql
psql (15.4 (Homebrew), server 16.0)
WARNING: psql major version 15, server major version 16.
         Some psql features might not work.
Type "help" for help.
```

After installation of PostgreSQL, use psql to open postgreSQL in terminal

### step 2 ingest table from created tables
``` python
Create table customer_kapl(
ID text,
Name text,
Source text,
)
COPY customer_kapl from '/Users/cminus/Desktop/Customer_kapl.csv' WITH (FORMAT CSV, HEADER true, DELIMITER ';');

#used generated csv file to create kapl customer table same procedure for cmpl customer


CREATE Table transaction(
ID serial PRIMARY KEY,
Date DATE,
Category text,
Type text,
Customer_ID text,
Service_Codes text,
Therapist text,
Payment_Method text,
Amount_Paid float,
Fees float,
Additional_Fees float,
Actual_Amount float,
Consultant text,
Remarks text,
New text,
Day int,
Month int,
Year int);/Users/cminus/Desktop

 \COPY transaction from '/Users/cminus/Desktop/Transaction_kapl.csv' WITH (FORMAT CSV, HEADER true, DELIMITER ';', DATEFORMAT 'DD/MM/YY');

Create employee_kapl(
Id smallint,
Name text,);

Copy employee_kapl from '/Users/cminus/Desktop/employee_kapl.csv ’ 

#used generated csv file to create kapl employee table same procedure for cmpl employee

```

## step 3 handling some errors

```
create temporary table temp_payment_method(
method text,
charge text,
year smallint
);

 COPY temp_payment_method FROM '/Users/cminus/Desktop/payment_method_cmpl.csv' WITH (Format csv, Header true, delimiter ',');


UPDATE temp_payment_method
SET charge = REPLACE(charge, '%', '')::NUMERIC;

UPDATE temp_payment_method
SET charge = charge / 100.0;

 UPDATE temp_payment_method
SET charge = (charge::DOUBLE PRECISION)::NUMERIC(10, 4);


WITH duplicates AS (
    SELECT Method, charge, year
    FROM temp_payment_method
    GROUP BY Method, charge, year
    HAVING COUNT(*) > 1
)

DELETE FROM temp_payment_method
WHERE (Method, charge, year) IN (
    SELECT Method, charge, year
    FROM duplicates
    LIMIT 1
);

Create table payment_method(
method text,
charge text,
year smallint
);

INSERT INTO payment_method (Method, charge, year)
SELECT Method, charge, year
FROM temp_payment_method;
```

# Some example queries


## In the "kapl" table, who is the individual making the highest payment contribution?

```
SELECT
    cc.Name,
    SUM(t.Amount_Paid) AS TotalAmountPaid
FROM
    temp t
JOIN
    customer_cmpl cc ON t.Customer_ID = cc.ID
GROUP BY
    cc.Name
ORDER BY
    TotalAmountPaid DESC
LIMIT 1;
```

## we get the result
```
   name   | totalamountpaid 
----------+-----------------
 Sumi Foo |            6000
(1 row)
```

## Who are the three individuals with the highest payment contributions?

```
SELECT
    cc.Name,
    SUM(t.Amount_Paid) AS TotalAmountPaid
FROM
    temp t
JOIN
    customer_cmpl cc ON t.Customer_ID = cc.ID
GROUP BY
    cc.Name
ORDER BY
    TotalAmountPaid DESC
LIMIT 3;
```

## we get the result

 | Name            | Total Amount Paid |
|-----------------|-------------------|
| Sumi Foo        | 6000              |
| Tiffany Cook    | 4600              |
| Keshia Faculin  | 2850              |

## How frequently do these individuals make visits?

```
WITH TopCustomers AS (
    SELECT
        cc.ID,
        cc.Name,
        SUM(t.Amount_Paid) AS TotalAmountPaid
    FROM
        temp t
    JOIN
        customer_kapl cc ON t.Customer_ID = cc.ID
    GROUP BY
        cc.ID,
        cc.Name
    ORDER BY
        TotalAmountPaid DESC
    LIMIT 3
)

SELECT
    tc.Name,
    COUNT(t.Date) AS VisitFrequency
FROM
    TopCustomers tc
JOIN
    temp t ON t.Customer_ID = tc.ID
GROUP BY
    tc.Name
ORDER BY
    COUNT(t.Date) DESC; 
 ```
 
## The result

| Name            | Visit Frequency |
|-----------------|------------------|
| Sumi Foo        | 32               |
| Tiffany Cook    | 16               |
| Keshia Faculin  | 10               |

## Which payment method incurs the highest expense in the year 2023?

```
SELECT
    method,
    AVG(CAST(charge AS numeric)) AS AverageCharge
FROM
    payment_method
WHERE
    year = 23  -- Replace with the specific year you are interested in
GROUP BY
    method
ORDER BY
    AverageCharge DESC
LIMIT 1;
```

| method | averagecharge |
|--------|---------------|
| ATOME  | 0.06          |
 

# Provide a ranking for the payment methods based on their expense levels in 2023.

```
WITH PaymentRank AS (
    SELECT
        method,
        AVG(CAST(charge AS numeric)) AS AverageCharge
    FROM
        payment_method
    WHERE
        year = 23
    GROUP BY
        method
)

SELECT
    method,
    RANK() OVER (ORDER BY AverageCharge DESC) AS Ranking,
    ROUND(AverageCharge, 4) AS AverageCharge -- Round to four decimal places for clarity
FROM
    PaymentRank
ORDER BY
    Ranking;
```
| method               | ranking | averagecharge |
|----------------------|---------|---------------|
| ATOME                | 1       | 0.0600        |
| STRIPE (1x)          | 2       | 0.0340        |
| FRESHA               | 3       | 0.0329        |
| GRABPAY              | 4       | 0.0108        |
| E-CAPITALAND VOUCHER | 5       | 0.0000        |



## Who are the most popular therapists?

```
SELECT
    therapist_name,
    COUNT(*) AS visit_count
FROM (
    SELECT
        e.Name AS therapist_name
    FROM
        transaction_kapl t
    JOIN
        employee_kapl e ON t.Therapist = e.Id::text
    WHERE
        t.Therapist IS NOT NULL
    UNION ALL
    SELECT
        e.Name AS therapist_name
    FROM
        transaction_kapl t
    JOIN
        employee_kapl e ON t.Consultant = e.Id::text
    WHERE
        t.Consultant IS NOT NULL
) AS therapist_visits
GROUP BY
    therapist_name
ORDER BY
    visit_count DESC
LIMIT 5;
```
## the result is:
| therapist_name | visit_count |
|----------------|-------------|
| Natalie        | 968         |
| Jeslyn         | 844         |
| Huey Mei       | 825         |
| Kelly          | 769         |
| Amberly        | 688         |



