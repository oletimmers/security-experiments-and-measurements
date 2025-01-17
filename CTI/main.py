import pandas as pd
import matplotlib

matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from general_data_editing import process_excel_multiple_sheets_to_csv, process_excel_combine_rows
import os

input_file = "data/CTI-Responses-Manual-Cleanup.xlsx"  # input file
input_file_2 = "data/CTI-Ground-Truth-Manual-Cleanup.xlsx"  # input file
responses_step1_file = "data/responses_step1.csv"  # .xlsx to csv of respondents
ground_truth_step1_file = "data/ground_truth_step1.csv"  # .xlsx to csv of ground truth
details_respondents_step2_file = "data/responses_step2.csv"
respondents_scenarios_step2_file = "data/respondents_scenarios_step2.csv"


def file_exists(file_path):
    return os.path.isfile(file_path)


def pre_processing(force_create=False):
    if (not file_exists(responses_step1_file)) or force_create:
        process_excel_multiple_sheets_to_csv(input_file, responses_step1_file)

    if (not file_exists(ground_truth_step1_file)) or force_create:
        process_excel_combine_rows(input_file_2, ground_truth_step1_file)


def generate_properties(force_create=False):
    if (not file_exists(details_respondents_step2_file)) or force_create:
        define_details_about_respondents()

    if (not file_exists(respondents_scenarios_step2_file)) or force_create or True:
        generate_scenario_rows()


def define_details_about_respondents():
    responses_file = responses_step1_file
    ground_truth_file = ground_truth_step1_file

    responses_df = pd.read_csv(responses_file)
    ground_truth_df = pd.read_csv(ground_truth_file)

    columns = [
        'respondent_id',  # Data direct from raw data
        'duration_of_experiment',
        'exp_risk_assessment',
        'exp_blackbox',
        'exp_developing_ml',
        'exp_reading_ti_reports',
        'random_group',  # Properties made now
        'rep1_likelihood_correct',  # Whether the respondent had same likelihood as the NCSC.
        'rep2_likelihood_correct',  # For all 8 reports
        'rep3_likelihood_correct',
        'rep4_likelihood_correct',
        'rep5_likelihood_correct',
        'rep6_likelihood_correct',
        'rep7_likelihood_correct',
        'rep8_likelihood_correct',
        'total_likelihood_correct',
        'average_confidence_assessment',  # from 1-5, range => not at all - fully
        'average_considered_impact',
        'good_understanding',
        'sufficient_time',
        'prepared_well_by_training'
    ]

    new_df = pd.DataFrame(columns=columns)

    # indexes 0-4 + 1 eventually
    confidence_list = ["I'm not confident at all", "I'm slightly confident", "I'm somewhat confident",
                       "I'm fairly confident", "I'm completely confident"]
    agreement_list = ["Strongly Disagree", "Disagree", "Neither agree nor disagree", "Somewhat agree", "Strongly agree"]

    for index, row in responses_df.iterrows():
        id_of_row = row['STAT_ID']
        duration = row['STAT_Duration_sec']
        exp_risk_assessment = row['MLEX_exp_in_vulnerability_risk_assessment']
        exp_blackbox = row['MLEX_exp_black_box_ml_algo']
        exp_developing_ml = row['MLEX_exp_developing_ml_algorithms']
        exp_reading_ti_reports = row['MLEX_exp_reading_threat_intelligence_reports']

        random_group = None
        for col in row.index:
            if col.startswith('RAND_') and row[col] > 0:
                random_group = col[-1]

        rep_likelihood_correct = []
        total_likelihood_correct = 0

        sum_confidence_assessment = 0
        sum_considered_impact = 0

        for i in range(1, 9):
            truth_row_for_this_report = ground_truth_df.loc[ground_truth_df['report_id'] == f"{i}_{random_group}"].iloc[
                0]
            own_likelihood = row[f"REP{i}_own_recomm_of_likelihood"]
            if own_likelihood == truth_row_for_this_report['ncsc_likelihood']:
                rep_likelihood_correct.append(True)
                total_likelihood_correct += 1
            else:
                rep_likelihood_correct.append(False)
            confidence = row[f"REP{i}_confident_that__vulnerability_assessment_is_correct"]
            considered_impact = row[f"REP{i}_i_considered_impact_of_vulnerability"]
            confidence_score = 0
            if confidence in confidence_list:
                confidence_score = confidence_list.index(confidence) + 1
            else:
                confidence_score = agreement_list.index(confidence) + 1
            considered_impact_score = agreement_list.index(considered_impact) + 1
            sum_confidence_assessment += confidence_score
            sum_considered_impact += considered_impact_score

        average_confidence_assessment = sum_confidence_assessment / 8
        average_considered_impact = sum_considered_impact / 8

        understanding = row["EVAL_i_had_good_understanding"]
        if understanding == "Agree":
            understanding = "Somewhat agree"
        good_understanding = agreement_list.index(understanding) + 1
        sufficient_time = agreement_list.index(row["EVAL_i_had_sufficient_time"]) + 1
        prepared_well_by_training = agreement_list.index(row["EVAL_training_prepared_me_well"]) + 1

        data_to_add = [
            id_of_row, duration, exp_risk_assessment, exp_blackbox, exp_developing_ml, exp_reading_ti_reports,
            random_group,
            rep_likelihood_correct[0], rep_likelihood_correct[1], rep_likelihood_correct[2], rep_likelihood_correct[3],
            rep_likelihood_correct[4], rep_likelihood_correct[5], rep_likelihood_correct[6], rep_likelihood_correct[7],
            total_likelihood_correct,
            average_confidence_assessment, average_considered_impact,
            good_understanding, sufficient_time, prepared_well_by_training
        ]

        new_df.loc[len(new_df)] = data_to_add

    new_df.to_csv(details_respondents_step2_file, index=False)


def generate_scenario_rows():
    responses_file = responses_step1_file
    ground_truth_file = ground_truth_step1_file

    responses_df = pd.read_csv(responses_file)
    ground_truth_df = pd.read_csv(ground_truth_file)

    columns = [
        'respondent_scenario_id',
        'respondent_id',  # Data direct from raw data
        'scenario_id',
        # metric 1
        'recommendation_source',
        'consistent_recommendation',
        'agree_with_recommendation',  # also metric 2
        # metric 2a
        'biased',
        'impartial',
        'confident',
        'objective',
        'subjective',
        # metric 2b
        'trustworthy'
    ]

    new_df = pd.DataFrame(columns=columns)

    # indexes 0-4 + 1 eventually
    confidence_list_pre = ["I'm not confident at all", "I'm slightly confident", "I'm somewhat confident",
                           "I'm fairly confident", "I'm completely confident"]
    confidence_list = [s.lower() for s in confidence_list_pre]
    agreement_list = ["strongly disagree", "disagree", "neither agree nor disagree", "somewhat agree", "strongly agree"]

    subjective_list_pre = ["The assessment was objective", "The assessment was slightly subjective",
                           "The assessment was somewhat subjective",
                           "The assessment was fairly subjective", "The assessment was very subjective"]
    subjective_list = [s.lower() for s in subjective_list_pre]

    for index, row in responses_df.iterrows():
        id_of_respondent = row['STAT_ID']

        random_group = None
        for col in row.index:
            if col.startswith('RAND_') and row[col] > 0:
                random_group = col[-1]

        for i in range(1, 9):
            scenario_id = f"{i}_{random_group}"
            respondent_scenario_id = f"{id_of_respondent}-{scenario_id}"
            truth_row_for_this_report = ground_truth_df.loc[ground_truth_df['report_id'] == f"{scenario_id}"].iloc[
                0]

            recommendation_source = truth_row_for_this_report['source'].split()[0].lower()
            consistent_recommendation = truth_row_for_this_report['recommendation'].split()[0].lower() == 'consistent'
            agree_with_recommendation = 5 if row[f"REP{i}_agree_with_final_intern_recomm_of_secteam"].lower() == 'yes' else 1
            biased_string = row[f"REP{i}_overall_final_recommendation_look_biased"]
            impartial_string = row[f"REP{i}_overall_final_recommendation_look_impartial"]
            biased_prop = agreement_list.index(biased_string.lower()) + 1
            impartial_prop = agreement_list.index(impartial_string.lower()) + 1

            confidence_string = row[f"REP{i}_confident_that__vulnerability_assessment_is_correct"].lower()
            confidence_prop = 1
            if confidence_string in confidence_list:
                confidence_prop = confidence_list.index(confidence_string) + 1
            else:
                confidence_prop = agreement_list.index(confidence_string) + 1

            objective_string = row[f"REP{i}_i_was_objective"]
            objective_prop = agreement_list.index(objective_string.lower()) + 1
            subjective_string = row[f"REP{i}_i_was_subjective"]
            subjective_string = subjective_string.replace('difficult', 'subjective')

            subjective_prop = subjective_list.index(subjective_string.lower()) + 1

            persuasive_metric = agree_with_recommendation + -1 * (biased_prop + impartial_prop)
            validation_metric = confidence_prop + objective_prop - subjective_prop
            trustworthy = persuasive_metric + validation_metric

            data_to_add = [
                respondent_scenario_id, id_of_respondent, scenario_id,
                recommendation_source, consistent_recommendation,
                agree_with_recommendation,
                biased_prop, impartial_prop,
                confidence_prop, objective_prop, impartial_prop,
                trustworthy
            ]

            new_df.loc[len(new_df)] = data_to_add

    new_df.to_csv(respondents_scenarios_step2_file, index=False)


def main_pipeline():
    pre_processing()
    generate_properties()


if __name__ == '__main__':
    main_pipeline()
