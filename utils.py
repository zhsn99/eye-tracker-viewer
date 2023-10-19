import os
import csv
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns



def reading_file(folder_path, folder, file):
        # Read the excel file
        file_path = os.path.join(folder_path, folder, file)
        df = pd.read_excel(file_path)
        return df

def check_file_type(file):
        print("Processing file: " + file + " ...")
        if file.endswith(".xlsx"):
            print("This is a excel file. Processing...")
            return True
        else:
            print("This is not a excel file. Skipping...")
            return False

def pupil_correlation(df, folder_path, folder, file):

    columns_of_interest = [
        'T1.leftPupilDiameter', 'T1.rightPupilDiameter', 'T2.leftPupilDiameter', 'T2.rightPupilDiameter']
    
    subset = df[columns_of_interest]
    correlation_matrix = subset.corr()

    plt.figure(figsize=(10, 8))
    sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', fmt='.2f')
    plt.title('Correlation Matrix between Pupil Diameters T1 and T2')
    if not os.path.exists(folder_path + folder +"/results/"):
        os.makedirs(folder_path + folder +"/results/")
    results_folder = os.path.join(folder_path, folder, "results")  # Use os.path.join for path construction

    plt.savefig(os.path.join(results_folder, f'correlation_matrix_pupil_{file}.png'))  # Save it afterward


# loading data raw data
def process_raw_data(folder_path, action):
    # check if results folder exits
    valid_actions = ["eye_contact_detection", "pupil_correlation", "your_processed_action"]
    # loop through folders in folder path
    folders = os.listdir(folder_path)
    print(folders)
    for folder in folders:
        files = os.listdir(folder_path + folder)
        print(os.path.join(folder_path, folder))
        print(files)
        print(20*"#",f"start folder {folder}", 20*"#")
        for file in files:
            if check_file_type(file):
                df = reading_file(folder_path, folder, file)
                if action == valid_actions[0]:
                     pass
                elif action == valid_actions[1]:
                     df = pupil_correlation(df, folder_path, folder, file)
                elif action == valid_actions[2]:
                     pass
                else:
                     print(f"Invalid action. Supported actions: {', '.join(valid_actions)}")
            else:
                continue
            # If it was the last file, print "Done!"
            if file == files[-1]:
                print(f"Done! {folder_path + folder}")
            else:
                print("Done!, next file...")


def process_processed_data(folder_path, action):
     return 0

