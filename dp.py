import pandas as pd
import argparse
import numpy as np
from itertools import combinations
import os
import re

pd.set_option('display.max_rows', 10)  # Set the maximum number of rows to display
pd.set_option('display.max_columns', 25)  # Set the maximum number of columns to display

pd.set_option('display.width', 1000)  # Set the display width
from datetime import datetime

# Read the CSV file into a DataFrame


# Define a custom function to combine columns 6 through 10 for each row and removing NaN
def combine_columns(row):
    non_nan_values = [str(val) for val in row[6:11] if not pd.isna(val)]
    return ', '.join(non_nan_values)

# Original date in the "Mon day, yy" format

def date_convert(row):
    original_date = row[0]
    # Parse the original date
    if(pd.isnull(original_date)):
        return 'NaN'
    parsed_date = datetime.strptime(str(original_date), "%b %d, %y")
    # Convert it to the "dd/mm/yy" format
    formatted_date = parsed_date.strftime("%d/%m/%y")
    return formatted_date;

def remove_dollar_and_convert(val):
    return pd.to_numeric(val.str.replace('$', ''), errors='coerce')

def replace_whitespace_with_empty(input_value):
    if isinstance(input_value, str):
        if re.match(r'^\s*$', input_value):
            return ""
    return input_value 

# not considering eamil for name
def transform_customer_name(group):
    for name in group:
        if '@' not in name:
            return name
    return group.iloc[0]

def combine_customer_name(df,prefix):
    counter = 0;
    for index, row in df.iterrows():
        if pd.isna(row['Cust ID']):
            df.loc[index, 'Cust ID'] = prefix + str(counter)
            counter += 1
    df['Customer Name'] = df.groupby('Cust ID')['Customer Name'].transform(transform_customer_name)
    return df;

def cmpl_conversion(filename):
    df = pd.read_csv(filename)
    rows_to_remove = []
    rows_amount_to_filled = []
    df.rename(columns={'Customer Name.1': 'Cust ID'})

    
    # Remove rows without dates
    for index,row in df.iterrows():
        
        #remove rows without date and customer Name
        if(pd.isna(row['Date'])or pd.isna(row['Customer Name'])):
            rows_to_remove.append(index);
        #fill in amount for actual Amount is 0
        if(pd.isna(row['Amount paid'])):
            df.loc[index, 'Amount paid'] = 0
            
        if((pd.isna(row['Charges for payment method']) or row['Charges for payment method'] == 'nan')):
            df.loc[index, 'Charges for payment method'] = 0
        else:
            percentage = row['Charges for payment method'].rstrip('%');
            percentage_float = float(percentage)/100.0;
            df.loc[index,'Charges for payment method'] = percentage_float;
        
        if(pd.isna(row['Additional Fees'])):
            df.loc[index, 'Additional Fees'] = 0
            
        if(row['Customer Category'] == 'new'):
            df.loc[index, 'Customer Category'] = 'New';
        if(isinstance(row['New Member?'], str) and row['New Member?'].isspace()):
            df.loc[index,'New Member?'] = '';
    
    
    #fillin New members to be no if its empty
    df['New Member?'].fillna('No', inplace=True)
    
    #the rest are all strings, consider as empty string.
    df.fillna('');
    
    df = df.drop(rows_to_remove)

    columns_to_clean = ['Amount paid','Fees','Additional Fees','Actual Amount']

    #remove dollar signs for fees
    for col in columns_to_clean:
        if col in df.columns:
            df[col] = df[col].astype(str).str.replace('$', '')

    #remove rows that dont count up
#     rows_to_remove=[]
#     for index,row in df.iterrows():
#         if(float(row['Fees']) + float(row['Additional Fees']) + 
#            float(row['Actual Amount']) != float(row['Amount paid'])):
#             rows_to_remove.append(index);
#     df = df.drop(rows_to_remove)
    
    #combining services codes
    df['service codes(combined)'] = df.apply(combine_columns,axis = 1)
    df['Service codes'] = df['service codes(combined)'].copy()
    columns_to_remove = ['Unnamed: 7', 'Unnamed: 8', 'Unnamed: 9', 'Unnamed: 10','service codes(combined)']
    df = df.drop(columns=columns_to_remove)

    #converting dates 
    df['Date(dd/mm/yy)'] = df.apply(date_convert,axis = 1)
    last_column = df.pop(df.columns[-1]);
    df.insert(0,last_column.name,last_column)
    df = df.drop(columns='Date')
    df[['Day', 'Month', 'Year']] = df['Date(dd/mm/yy)'].str.split('/', expand=True)
    
#   
    df=df.applymap(replace_whitespace_with_empty)
    
#     grouped = df.groupby('Cust ID')['Customer Name'].agg(lambda x: x.value_counts().idxmax()).reset_index()

#     # Merge the results back into the original DataFrame
#     df = df.merge(grouped, on='Cust ID', how='left', suffixes=('', '_new'))
#     df['Customer Name'] = df['Customer Name_new']
#     df.drop(columns=['Customer Name_new'], inplace=True)
    
    return df

def kapl_conversion(filename):
    df = pd.read_csv(filename)
    rows_to_remove = []
    df = df.rename(columns={'Unnamed: 5': 'Cust ID'})
    
    # Remove rows without dates
    for index,row in df.iterrows():
        #remove rows without date or without customer name
        if(pd.isna(row['Date']) or pd.isna(row['Customer Name'])):
            rows_to_remove.append(index);
            
        if(pd.isna(row['Amount paid'])):
            df.loc[index, 'Amount paid'] = 0
            
        if((pd.isna(row['Charges for payment method']) or row['Charges for payment method'] == 'nan')):
            df.loc[index, 'Charges for payment method'] = 0
        
        else:
            percentage = row['Charges for payment method'].rstrip('%');
            percentage_float = float(percentage)/100.0;
            df.loc[index,'Charges for payment method'] = percentage_float;

            
        if(pd.isna(row['Additional Fees'])):
            df.loc[index, 'Additional Fees'] = 0
            
        if(row['Customer Category'] == 'new'):
            df.loc[index, 'Customer Category'] = 'New';
            
        if(isinstance(row['New Member?'], str) and row['New Member?'].isspace()):
            df.loc[index,'New Member?'] = '';
    
    #fillin New members to be no if its empty
    df['New Member?'].fillna('No', inplace=True)
            
    df = df.drop(rows_to_remove)

    #remove dollar signs for fees
    columns_to_clean = ['Amount paid','Fees','Additional Fees','Actual Amount']
    for col in columns_to_clean:
        if col in df.columns:
            df[col] = df[col].astype(str).str.replace('$', '')
            
    #remove rows with $1 Promotion
    condition = df['Customer Name'].str.startswith('$')
    removed_rows=df[condition]
    
    df = df[~condition]
    
  
  
    #remove error rows that dont count up
#     rows_to_remove=[]
#     for index,row in df.iterrows():
#         if(float(row['Fees']) + float(row['Additional Fees']) + float(row['Actual Amount']) != float(row['Amount paid'])):
#             rows_to_remove.append(index);
#     df = df.drop(rows_to_remove)

    #combining services codes
    df['service codes(combined)'] = df.apply(combine_columns,axis = 1)
    df['Service codes'] = df['service codes(combined)'].copy()
    columns_to_remove = ['Unnamed: 7', 'Unnamed: 8', 'Unnamed: 9', 'Unnamed: 10','service codes(combined)']
    df = df.drop(columns=columns_to_remove)

    #get date in dd/mm/yy format
    df['Date(dd/mm/yy)'] = df.apply(date_convert,axis = 1)
    last_column = df.pop(df.columns[-1]);
    df.insert(0,last_column.name,last_column)
    df = df.drop(columns='Date')
    df = df.drop(columns='Unnamed: 21')
    df[['Day', 'Month', 'Year']] = df['Date(dd/mm/yy)'].str.split('/', expand=True)
    
    #one dollar promotion users
    odp_df = pd.DataFrame(columns=df.columns)
    odp_df = pd.concat([odp_df, removed_rows])

    #combine customer with same id, add id for random customers.
    df = combine_customer_name(df,'kt_')
    
    if os.path.exists('kapl_$1.csv'):
        os.remove('kapl_$1.csv')
    odp_df.to_csv('kapl_$1.csv',index=False, sep=';')
    
    
    return df

def concat_csv(file1,file2):
    df1 = cmpl_conversion(file1);
    df2 = cmpl_conversion(file2);
    df2.columns = df1.columns;
    combined_df = pd.concat([df1, df2], ignore_index=True)
    

    # Iterate through the DataFrame and fill empty strings with "temp_x"
    combined_df = combine_customer_name(combined_df,'ct_')
    
    return combined_df

def create_cmpl_csv(filename,destination):
    if not os.path.exists(filename):
        print('file '+filename +' does not exist');
        return;
    df = cmpl_conversion(filename)
    if os.path.exists(destination):
        os.remove(destination)
    df.to_csv(destination,index=False, sep=';')


def create_kapl_csv(filename,destination):
    if not os.path.exists(filename):
        print('file '+filename +' does not exist');
        return;
    df = kapl_conversion(filename)
    if os.path.exists(destination):
        os.remove(destination)
    df.to_csv(destination,index=False, sep=';')

def concat_cmpl_csv(file_1, file_2,dest):
    if not os.path.exists(file_1) or not os.path.exists(file_2):
        print('files do not exist');
        return;
    df = concat_csv(file_1,file_2)
    if os.path.exists(dest):
        os.remove(dest)
    df.to_csv(dest,index=False, sep=';')
# create new dataframe 'payment method'
def create_payment_table(df):
    df_payment_method = df[['Payment method', 'Charges for payment method', 'Year']].drop_duplicates()

    df_payment_method = df_payment_method.rename(columns={
        'Payment method': 'Method',
        'Charges for payment method': 'Charge',
    })

    df_payment_method = df_payment_method.dropna(subset=['Method'])

    return df_payment_method


# create new dataframe 'Employee'
def create_employee_table(df):
    employee = pd.concat([df['Therapist'], df['Consultant']], axis=0).reset_index(drop=True)

    df_employee = pd.DataFrame({'Name': employee})
    df_employee = df_employee.dropna(subset=['Name'])
    df_employee.drop_duplicates(inplace=True)

    df_employee.insert(0, 'ID', range(1, len(df_employee) + 1))

    return df_employee


# create new dataframe 'Customer'
def create_cust_table(df):
    df_customer = df[['Cust ID', 'Customer Name']].drop_duplicates()
    df_customer['Source'] = df['How did they know About us? (New Cust only)']

    df_customer = df_customer.rename(columns={
        'Cust ID': 'ID',
        'Customer Name': 'Name',
    })

    df_customer = df_customer.dropna(subset=['ID'])

    return df_customer


# create new datarame 'Transaction'
def create_trans_table(df):
    df = df.drop(columns=['Charges for payment method', 'Customer Name', 'How did they know About us? (New Cust only)'])

    df.insert(0, 'ID', range(1, len(df) + 1))

    df = df.rename(columns={
        'Type of Sale (if customer paying for existing package, put Package)': 'Type',
        'Date(dd/mm/yy)': 'Date',
        'Cust ID': 'Customer ID',
        'Service codes': 'Service Codes',
        'Payment method': 'Payment Method',
        'Amount paid': 'Amount Paid',
        'Customer Category': 'Category',
        'Remarks + REASON FOR NOT JOINING MEMBERSHIP/ Package': 'Remarks',
        'New Member?': 'New',
    })

    return df


def split_and_save_data(file_name, company_name):
    df=pd.read_csv(file_name, delimiter=";")

    payment = create_payment_table(df)
    emp = create_payment_table(df)
    cust = create_cust_table(df)
    trans = create_trans_table(df)

    payment.to_csv(f'Payment_Method_{company_name}.csv', index=False)
    emp.to_csv(f'Employee_{company_name}.csv', index=False)
    cust.to_csv(f'Customer_{company_name}.csv', index=False)
    trans.to_csv(f'Transaction_{company_name}.csv', index=False)

def merge_function(array):
    out = []
    for cur in array:
        N = len(cur)
        to_store = ''
        for index in range(N):
            to_store += str(cur[index])
        out.append(to_store)
    out = np.array(out)
    return out

df_list = []
df_name = []

def self_check(i):
    df1 = df_list[i]
    for col_1 in df1.columns:
        val_1 = df1.drop_duplicates(subset=col_1)[col_1].values
        for col_2 in df1.columns:
            if col_1 == col_2:
                continue
            val_2 = df1.drop_duplicates(subset=col_2)[col_2].values
            if np.isin(val_1, val_2).all():
                print(df_name[i] + " : " +  col_1 + '-> ' + df_name[i] + " : " + col_2)

def inclusion_dependency_check(df_1, df_2):
    df1 = df_list[df_1]
    df2 = df_list[df_2]
    lhs = []
    rhs = []
    for col_1 in df1.columns:
        val_1 = df1.drop_duplicates(subset=col_1)[col_1].values
        for col_2 in df2.columns:
            val_2 = df2.drop_duplicates(subset=col_2)[col_2].values
            if np.isin(val_1, val_2).all():
                lhs.append(col_1)
                rhs.append(col_2)
                print(df_name[df_1] + " : " +  col_1 + '-> ' + df_name[df_2] + " : " + col_2)
    lhs = np.array(lhs)
    lhs = np.unique(lhs)
    rhs = np.array(rhs)
    rhs = np.unique(rhs)
    
    for N in range(2,min(len(rhs),len(lhs))):
        col_combinations_1 = list(combinations(lhs, N))
        col_combinations_2 = list(combinations(rhs, N))
        for col_1 in col_combinations_1:
            col_1 = list(col_1)
            val_1 = df1.drop_duplicates(subset=col_1)[col_1].values
            val_1 = merge_function(val_1)
            for col_2 in col_combinations_2:
                col_2 = list(col_2)
                val_2 = df2.drop_duplicates(subset=col_2)[col_2].values    
                val_2 = merge_function(val_2)
                if np.isin(val_1, val_2).all():
                    output = df_name[df_1] + ' : '
                    for i in col_1:
                        output += (i + '， ')
                    output += (' -> ' + df_name[df_2] + ' : ')
                    for i in col_2:
                        output += (i + '， ')
                    print(output)


def profiling(data_file):
    df = pd.read_csv(data_file)

    print(df.head(5))

    print(df.info())

    print(df.describe())

    print(df.describe(include=[object]))

    # Checking duplicate rows
    print(df[df.duplicated()])

    # Checking date format and consistency
    try:
        df['Date'] = pd.to_datetime(df['Date'], format='%d/%m/%Y', errors='coerce')
        failures = df['Date'].isna().sum()
    except Exception as e:
        conversion_info = str(e)
    else:
        conversion_info = 'Date conversion successful with {} failures'.format(failures)

    print(conversion_info)

    date_info = df['Date'].describe()

    date_nan = df['Date'].isna().sum()

    print(date_info, date_nan)

   # Finding any posible combined keys(no more than 3 keys) as the primary key

   # Finding any posible combined keys(no more than 3 keys) as the primary key
def find_candidate_keys(df, max_combo=3):
    candidate_keys = []
    columns = df.columns.tolist()

    for i in range(2, max_combo + 1):
        for cols in combinations(columns, i):
            if df[list(cols)].drop_duplicates().shape[0] == df.shape[0]:
                candidate_keys.append(cols)
                for col in cols:
                    if col in columns:
                        columns.remove(col)
    return candidate_keys


def fd(df):
    fds = {}
    for col in df.columns:
        for dep_col in df.columns.drop(col):
            if df.groupby(col)[dep_col].nunique().max() == 1:
                if col in fds:
                    fds[col].append(dep_col)
                else:
                    fds[col] = [dep_col]

    return fds


def find_rules(df, file_name):
    df = df.drop(['Day', 'Month', 'Year'], axis=1)
    uniq = {col: df[col].is_unique for col in df.columns}
    all_false = all(not unique for unique in uniq.values())
    if all_false:
        candi_keys = find_candidate_keys(df)
        print(file_name, '\npossible combined primary key', candi_keys)
    else:
        true_cols = [col for col, unique in uniq.items() if unique]
        print(file_name, '\npossible primary key', true_cols)

    fds = fd(df)
    print(file_name, '\nrules', fds)


# Function to read a file and handle potential errors
def read_file(filepath):
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        return None
    try:
        return pd.read_csv(filepath, delimiter=';')  # Change as necessary for file format
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return None


def main():
    global df_list, df_name
    parser = argparse.ArgumentParser(description="Description of your script")
    
    # Add an argument to specify the function to call
    parser.add_argument("function", choices=["concat_cmpl_csv",
                                            "create_cmpl_csv",
                                            "create_kapl_csv",
                                            "split_tables",
                                            "functional_dep",
                                            "inclusion_dep",
                                            "profiling",
                                            "functional_dep",
                                            ], help="Specify which function to call")
    parser.add_argument("arg1", type=str, help="Description of arg1")
    parser.add_argument("arg2", type=str, nargs='?', default=None,help="Description of arg2")
    parser.add_argument("arg3", type=str,  nargs='?', default=None,help="Description of arg3")
    args = parser.parse_args()

    # Call the selected function
    if args.function == "concat_cmpl_csv":
        concat_cmpl_csv(args.arg1,args.arg2, args.arg3)
    elif args.function == "create_cmpl_csv":
        create_cmpl_csv(args.arg1,args.arg2);
    elif args.function == 'create_kapl_csv':
        create_kapl_csv(args.arg1,args.arg2);
    elif args.function == 'split_tables':
        split_and_save_data(args.arg1,args.arg2);
    elif args.function == 'inclusion_dep':
        file1 = args.arg1;
        file2 = args.arg2;
        file3 = args.arg3;
        df_name=[file1,file2,file3];
        for each in df_name:
            if(each != None):
                a = pd.read_csv(each,sep=';');
                df_list.append(a);
        # cmpl_2022 = pd.read_csv(file1,sep=';')
        # cmpl_2023 = pd.read_csv(file2,sep=';')
        # kapl_2023 = pd.read_csv(file3,sep=';')
        # df_list = [cmpl_2022,cmpl_2023,kapl_2023];
        for i in range(len(df_list)):
            for col in df_list[i].columns:
                if df_list[i][col].isnull().sum() > 0:
                    if col == 'Fees':
                        df_list[i][col] = df_list[i][col].fillna(0)
                    elif col == 'Actual Amount':
                        df_list[i][col] = df_list[i][col].fillna(0)
                    else:
                        df_list[i][col] = df_list[i][col].fillna('')
        for df in range(len(df_list)):
            print('\n self check: ' + df_name[df] + '\n')
            self_check(df)
        for i in range(len(df_list)):
            for j in range(len(df_list)):
                if(i != j):
                    print("\n Inclusion Dependency: " + df_name[i] + ' '+df_name[j] + '\n');
                    inclusion_dependency_check(i, j);
    elif args.function == 'profiling':
        profiling(args.arg1);
    elif args.function == 'functional_dep':
        df = read_file(args.arg1)
        if df is not None:
            find_rules(df, args.arg1)
    else:
        print("Invalid function name")

    # match args.function:
    #     case "concat_cmpl_csv":
    #         if(args.arg3 == None):
    #             print('missing argument');
    #             return;
    #         concat_cmpl_csv(args.arg1,args.arg2, args.arg3)
    #     case "create_cmpl_csv":
    #         create_cmpl_csv(args.arg1,args.arg2);
    #     case 'create_kapl_csv':
    #         create_kapl_csv(args.arg1,args.arg2);
    #     case _:
    #         print()
if __name__ == "__main__":
    main()