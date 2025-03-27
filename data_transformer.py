import pandas as pd
import numpy as np
from datetime import datetime

def format_student_id(student_id):
    """
    Add 'u' prefix to student ID if it doesn't already have one.
    
    Args:
        student_id: The student ID string
        
    Returns:
        str: Formatted student ID with 'u' prefix if needed
    """
    student_id = str(student_id).strip().lower()
    if not student_id.startswith('u'):
        return f"u{student_id}"
    return student_id

def transform_csv_for_matching(input_csv: str, output_csv: str):
    """
    Transform the downloaded CSV format to match the romantic_dates.csv format.
    
    Args:
        input_csv: Path to the input CSV file
        output_csv: Path where the transformed CSV should be saved
    """
    # Read the raw CSV
    df = pd.read_csv(input_csv)
    
    # Create a new DataFrame with the desired column structure
    transformed_df = pd.DataFrame()
    
    # Convert timestamp to desired format
    transformed_df['Timestamp'] = pd.to_datetime(df['submittedAt']).dt.strftime('%m/%d/%Y %H:%M:%S')
    
    # Create placeholder email from student ID
    formatted_ids = df['studentId'].apply(format_student_id)
    transformed_df['Student ID'] = formatted_ids
    transformed_df['Email Address'] = formatted_ids.apply(lambda x: f"{x}@warwick.ac.uk")
    transformed_df['Name (Full Name)'] = formatted_ids  # Using formatted ID as name as in original format
    transformed_df['Email ID'] = transformed_df['Email Address']  # Same as email address
    
    # Map gender identity
    gender_map = {
        'male': 'Man',
        'female': 'Woman',
        'non-binary': 'Non-Binary'
    }
    transformed_df['I identify as...'] = df['identity'].map(gender_map)
    
    # Map date preference
    date_map = {
        '11/21/24': 'Thursday, 21st Nov',
        '11/22/24': 'Friday, 22nd Nov',
    }
    transformed_df['Which day would you prefer the date to be on?'] = df['preferredDate'].map(date_map)
    
    # Map year of study
    year_map = {
        '1': '1st Year',
        '2': '2nd Year',
        '3': '3rd Year',
        '4': '4th Year',
        'postgraduate': 'Postgraduate'
    }
    transformed_df['Which year are you in?'] = df['yearOfStudy'].map(year_map)
    
    # Map year preference
    year_pref_map = {
        'same': 'Same year as me',
        'different': 'Different year as me',
        'any': 'Open to any year'
    }
    transformed_df['I would like to go on a date with someone who is...'] = df['yearPreference'].map(year_pref_map)
    
    # Map date type
    transformed_df['I want to go on a...'] = df['dateType'].str.capitalize() + ' Date'
    
    # Map date format preference
    transformed_df['I want a...'] = df['dateFormat']
    
    # Map partner preference
    partner_pref_map = {
        'men': 'Men',
        'women': 'Women',
        'everyone': 'Everyone'
    }
    transformed_df['I am interested in...'] = df['partnerPreference'].map(partner_pref_map)
    
    # Filter out rows where 'purchased' column is not 'yes'
    transformed_df = transformed_df[df['purchased'].str.lower() == 'yes']
    
    # Add all personality questions
    personality_questions = [
        'I like to be adventurous.',
        'I believe in true love.',
        'I am confident.',
        'I am looking for something serious.',
        'I like to have intellectual conversations.',
        'I like talking about my feelings and emotions.',
        'I am an extrovert.',
        'I care about the environment.',
        'I like to dance.',
        'I have a strong connection with religion.',
        'On a Friday night, I would be most likely out clubbing.',
        'I believe being close to your family is important.',
        'I like to travel.',
        'I tend to swear a lot.',
        'I am always very organised and tidy.',
        'I believe commitment is the most important factor in a relationship.',
        'I tend to prioritize my academic life over my social life.',
        'I like discussing books or/and movies.',
        'I am laid back.',
        'I like sarcastic people.',
        'I tend to base my decisions on feelings rather than rational thinking.',
        'In a heated argument, I am okay with being proven wrong and/or change my view based on what my opponent has said.',
        'Healthy living is important to me.',
        'I believe actions speak louder than words.',
        'I am passionate about talking about politics',
        "It's important for my partner to share the same morals as me.",
        'I am a romantic.'
    ]
    
    # Map the personality questions from the input column names to the exact format needed
    column_mapping = {
        'adventurous': 'I like to be adventurous.',
        'believeInTrueLove': 'I believe in true love.',
        'confident': 'I am confident.',
        'lookingForSerious': 'I am looking for something serious.',
        'intellectualConversations': 'I like to have intellectual conversations.',
        'talkingAboutFeelings': 'I like talking about my feelings and emotions.',
        'extrovert': 'I am an extrovert.',
        'careAboutEnvironment': 'I care about the environment.',
        'likeToDance': 'I like to dance.',
        'religiousConnection': 'I have a strong connection with religion.',
        'outClubbing': 'On a Friday night, I would be most likely out clubbing.',
        'closeToFamily': 'I believe being close to your family is important.',
        'likeToTravel': 'I like to travel.',
        'swearALot': 'I tend to swear a lot.',
        'organizedAndTidy': 'I am always very organised and tidy.',
        'commitmentImportant': 'I believe commitment is the most important factor in a relationship.',
        'prioritizeAcademics': 'I tend to prioritize my academic life over my social life.',
        'discussBooksMovies': 'I like discussing books or/and movies.',
        'laidBack': 'I am laid back.',
        'likeSarcasticPeople': 'I like sarcastic people.',
        'decisionBasedOnFeelings': 'I tend to base my decisions on feelings rather than rational thinking.',
        'openToChangingViews': 'In a heated argument, I am okay with being proven wrong and/or change my view based on what my opponent has said.',
        'healthyLiving': 'Healthy living is important to me.',
        'actionsOverWords': 'I believe actions speak louder than words.',
        'passionateAboutPolitics': 'I am passionate about talking about politics',
        'sharedMoralsImportant': "It's important for my partner to share the same morals as me.",
        'romantic': 'I am a romantic.'
    }
    
    # Add all personality question responses
    for old_col, new_col in column_mapping.items():
        transformed_df[new_col] = df[old_col].astype(float)
    
    # Ensure all values are in the correct format
    for col in personality_questions:
        transformed_df[col] = transformed_df[col].round(1)
    
    # Save the transformed DataFrame
    transformed_df.to_csv(output_csv, index=False)
    print(f"Transformed data saved to {output_csv}")
    print(f"Total number of entries: {len(transformed_df)}")

    # Validate the transformation
    original_format = pd.read_csv("date_matching/data/romantic_dates.csv")
    missing_columns = set(original_format.columns) - set(transformed_df.columns)
    if missing_columns:
        print(f"\nWarning: Missing columns compared to original format: {missing_columns}")
    extra_columns = set(transformed_df.columns) - set(original_format.columns)
    if extra_columns:
        print(f"\nWarning: Extra columns not in original format: {extra_columns}")

if __name__ == "__main__":
    transform_csv_for_matching(
        input_csv='questionnaire-responses-2024-11-19.csv',
        output_csv='transformed_romantic_dates.csv'
    )