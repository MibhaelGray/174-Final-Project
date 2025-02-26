import pandas as pd
import os


csv_folder = "Data/Original_CSVs"
cleaned_folder = "Data/Cleaned_CSVs"
os.makedirs(cleaned_folder, exist_ok=True)

keep_columns = [
    "UTC Timestamp (Interval Ending)",
    "Local Timestamp Central Time (Interval Beginning)",
    "Local Timestamp Central Time (Interval Ending)",
    "Local Date",
    "Hour Number",
    "Bus average LMP",
    "North LMP",
    "Hub average LMP"
]

df_list = []
for file in sorted(os.listdir(csv_folder)):  
    if file.endswith(".csv"):
        file_path = os.path.join(csv_folder, file)  # Define file_path here
        
        try:
            df = pd.read_csv(file_path)
            df = df[keep_columns]
            cleaned_path = os.path.join(cleaned_folder, file)
            df.to_csv(cleaned_path, index=False)
            df_list.append(df)

        except Exception as e:
            print(f"Error processing file: {file_path}. Error: {e}")

merged_df = pd.concat(df_list, ignore_index=True)
merged_df.to_csv("cleaned_LMP_data.csv", index=False)
print(f"Processed {len(df_list)} files. Cleaned versions saved in '{cleaned_folder}', and merged dataset saved as 'cleaned_LMP_data.csv'.")


# Converting the cleaned data to have proper datetime formatting
cleaned_lmp = pd.read_csv("Data\Cleaned_Merged\cleaned_LMP_data.csv")



cleaned_lmp['UTC Timestamp (Interval Ending)'] = pd.to_datetime(cleaned_lmp['UTC Timestamp (Interval Ending)'])
cleaned_lmp['Local Timestamp Central Time (Interval Beginning)'] = pd.to_datetime(cleaned_lmp['Local Timestamp Central Time (Interval Beginning)'])
cleaned_lmp['Local Timestamp Central Time (Interval Ending)'] = pd.to_datetime(cleaned_lmp['Local Timestamp Central Time (Interval Ending)'])
cleaned_lmp['Local Date'] = pd.to_datetime(cleaned_lmp['Local Date'])


# Save the DataFrame with datetime-converted columns to a new CSV
output_path = "Data/Cleaned_Merged/cleaned_LMP_data_with_datetime.csv"
cleaned_lmp.to_csv(output_path, index=False)

print(f"Data with converted datetimes saved to '{output_path}'.")



