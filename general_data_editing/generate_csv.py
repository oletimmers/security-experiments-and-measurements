import pandas as pd


def process_excel_multiple_sheets_to_csv(excel_file, csv_file):
    # Read the Excel file
    xls = pd.ExcelFile(excel_file)

    # Initialize an empty DataFrame for the combined data
    combined_df = pd.DataFrame()

    # Iterate through each sheet in the Excel file
    for sheet_name in xls.sheet_names:
        # Read the sheet into a DataFrame
        df = pd.read_excel(xls, sheet_name=sheet_name)

        # Append the DataFrame to the combined DataFrame, aligning columns and filling missing values with NaN
        combined_df = pd.concat([combined_df, df], ignore_index=False, sort=False)

    # Save the combined DataFrame to a CSV file
    combined_df.to_csv(csv_file, index=False)


def process_excel_combine_rows(excel_file, csv_file):
    # Read the Excel file
    df = pd.read_excel(excel_file, sheet_name='Sheet1')

    columns = ['report_id', 'source', 'recommendation', 'ncsc_likelihood']
    new_df = pd.DataFrame(columns=columns)

    for i in range(0, len(df) - 1, 2):
        current_row = df.iloc[i]
        next_row = df.iloc[i + 1]

        for j in range(1, 9):
            report_nr = j
            rand_group = current_row['ID']
            source_and_recommendation = current_row[report_nr].split(" - ")
            report_id = f"{report_nr}_{rand_group}"
            source = source_and_recommendation[0]
            recommendation = source_and_recommendation[1]
            likelihood = next_row[report_nr]

            # Step 4: Append data to the new DataFrame
            new_df.loc[len(new_df)] = [report_id, source, recommendation, likelihood]

    new_df.to_csv(csv_file, index=False)


if __name__ == "__main__":
    input_file = "your_input_file.xlsx"  # Replace with your input Excel file
    output_file = "output_combined_data.csv"  # Replace with your desired output CSV file
    process_excel_multiple_sheets_to_csv(input_file, output_file)
