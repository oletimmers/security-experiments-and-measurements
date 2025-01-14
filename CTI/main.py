from general_data_editing import process_excel_multiple_sheets_to_csv, process_excel_combine_rows
import os

input_file = "data/CTI-Responses-Manual-Cleanup.xlsx"  # input file
input_file_2 = "data/CTI-Ground-Truth-Manual-Cleanup.xlsx"  # input file
responses_step1_file = "data/responses_step1.csv"  # .xlsx to csv of respondents
ground_truth_step1_file = "data/ground_truth_step1.csv"  # .xlsx to csv of respondents


def file_exists(file_path):
    return os.path.isfile(file_path)


def pre_processing(force_create=False):
    if (not file_exists(responses_step1_file)) or force_create:
        process_excel_multiple_sheets_to_csv(input_file, responses_step1_file)

    if (not file_exists(ground_truth_step1_file)) or force_create:
        process_excel_combine_rows(input_file_2, ground_truth_step1_file)


def define_details_about_students():
    pass



def main_pipeline():
    pre_processing()


if __name__ == '__main__':
    main_pipeline()
