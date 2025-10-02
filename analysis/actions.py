import os
import csv
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from utils import *

def avg_eyes_correlation(df, folder_path, folder, file):
    columns_of_interest = [
        'T1.leftPupilDiameter', 'T1.rightPupilDiameter', 'T2.leftPupilDiameter', 'T2.rightPupilDiameter']
    
    #get average of T1.leftPupilDiameter', 'T1.rightPupilDiameter' columns row by row
    df['T1.averagePupilDiameter'] = df[columns_of_interest[0:2]].mean(axis=1)
    #get average of T2.leftPupilDiameter', 'T2.rightPupilDiameter' columns row by row
    df['T2.averagePupilDiameter'] = df[columns_of_interest[2:4]].mean(axis=1)
    columns_of_interest = ['T1.averagePupilDiameter', 'T2.averagePupilDiameter']
    df_smoothed = df[columns_of_interest].apply(lambda col: conditional_kernel(col, 50, 1.5, 5))
    # calculate corrolation between T1.averagePupilDiameter and T2.averagePupilDiameter
    correlation = df_smoothed[columns_of_interest].corr()

    # Plot the heatmap
    plt.figure(figsize=(10, 8))
    sns.heatmap(correlation, annot=True, cmap='coolwarm', fmt='.2f')
    plt.title('Correlation Matrix between Pupil Diameters T1 and T2 avg between eyes')

    #save in the results folder same directory as script
    if not os.path.exists(folder_path + folder +"/smoothed_results/"):
        os.makedirs(folder_path + folder +"/smoothed_results/")
    results_folder = os.path.join(folder_path, folder, "smoothed_results")  # Use os.path.join for path construction
    plt.savefig(os.path.join(results_folder, f'avg_eyes_correlation_matrix_pupil_{file}.png'))  # Save it afterward


def avg_pupil_correlation(conditions):
    print("Calculating average pupil correlation...")
    data = {
        'T1.leftPupilDiameter': [0.000000, 0.000000, 0.000000, 0.000000],
        'T1.rightPupilDiameter': [0.000000, 0.000000, 0.000000, 0.000000],
        'T2.leftPupilDiameter': [0.000000, 0.000000, 0.000000, 0.000000],
        'T2.rightPupilDiameter': [0.000000, 0.000000, 0.000000, 0.000000]
    }

    # Create a DataFrame with the specified shape
    

    keys = conditions.keys()
    for k in keys:
        average_matrix = pd.DataFrame(data, columns=data.keys(), index=data.keys())
        print(20*"#","Working on Conidition: ", k,20*"#")
        sum_matrix = pd.DataFrame(data, columns=data.keys(), index=data.keys())
        for file in conditions[k]:
            print("Processing file: " + file + " ...")
            df = reading_file(file)
            columns_of_interest = [
        'T1.leftPupilDiameter', 'T1.rightPupilDiameter', 'T2.leftPupilDiameter', 'T2.rightPupilDiameter']
            df_smoothed = df[columns_of_interest].apply(lambda col: conditional_kernel(col, 50, 1.5, 5))
            #subset = df[columns_of_interest]
            correlation_matrix = df_smoothed[columns_of_interest].corr()
            sum_matrix = sum_matrix + correlation_matrix
        average_matrix = average_matrix + sum_matrix/len(conditions[k])
        plot_correlation_matrix(average_matrix, k)

def pupil_correlation(df, folder_path, folder, file):

    columns_of_interest = [
        'T1.leftPupilDiameter', 'T1.rightPupilDiameter', 'T2.leftPupilDiameter', 'T2.rightPupilDiameter']
    
    df_smoothed = df[columns_of_interest].apply(lambda col: conditional_kernel(col, 50, 1.5, 5))
    correlation_matrix = df_smoothed[columns_of_interest].corr()

    plt.figure(figsize=(10, 8))
    sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', fmt='.2f')
    plt.title('Correlation Matrix between Pupil Diameters T1 and T2')
    if not os.path.exists(folder_path + folder +"/smoothed_results/"):
        os.makedirs(folder_path + folder +"/smoothed_results/")
    results_folder = os.path.join(folder_path, folder, "smoothed_results")  # Use os.path.join for path construction

    plt.savefig(os.path.join(results_folder, f'correlation_matrix_pupil_{file}.png'))  # Save it afterward
 