import pandas as pd
from langdetect import detect, DetectorFactory
from langdetect.lang_detect_exception import LangDetectException
import re


# Seed for consistent results
DetectorFactory.seed = 0


def detect_language(text):
    """Detect if text is Arabic or English."""
    if not text or pd.isna(text):
        return 'unknown'
    
    # Simple heuristic: if contains Arabic characters, it's Arabic
    arabic_pattern = re.compile(r'[\u0600-\u06FF\u0750-\u077F]')
    if arabic_pattern.search(str(text)):
        return 'ar'
    
    try:
        lang = detect(str(text))
        if lang == 'ar':
            return 'ar'
        else:
            return 'en'
    except LangDetectException:
        return 'en'  # default to English


def parse_training_excel(filepath):
    """
    Parse the training Excel file and extract structured data.
    Expected columns: Subject Area, Training name (course name), Start Date, End Date
    """
    try:
        df = pd.read_excel(filepath)
    except Exception as e:
        raise ValueError(f"Could not read Excel file: {e}")
    
    # Normalize column names to handle variations
    df.columns = df.columns.str.strip().str.lower()
    
    # Map possible column variations
    column_mapping = {
        'subject area': 'subject_area',
        'subject_area': 'subject_area',
        'منطقة الموضوع': 'subject_area',
        'المجال': 'subject_area',
        'training name': 'training_name',
        'course name': 'training_name',
        'training_name': 'training_name',
        'course_name': 'training_name',
        'اسم التدريب': 'training_name',
        'اسم الدورة': 'training_name',
        'start date': 'start_date',
        'start_date': 'start_date',
        'تاريخ البداية': 'start_date',
        'end date': 'end_date',
        'end_date': 'end_date',
        'تاريخ النهاية': 'end_date'
    }
    
    # Rename columns
    for old_col in df.columns:
        if old_col in column_mapping:
            df = df.rename(columns={old_col: column_mapping[old_col]})
    
    # Verify required columns exist
    required_cols = ['subject_area', 'training_name']
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing required columns: {missing_cols}")
    
    # Clean data
    df = df.dropna(subset=['subject_area', 'training_name'])
    df['subject_area'] = df['subject_area'].astype(str).str.strip()
    df['training_name'] = df['training_name'].astype(str).str.strip()
    
    # Detect language from first few non-null subject areas
    sample_texts = []
    for _, row in df.head(10).iterrows():
        if pd.notna(row['subject_area']) and pd.notna(row['training_name']):
            sample_texts.extend([row['subject_area'], row['training_name']])
    
    # Determine primary language
    languages = [detect_language(text) for text in sample_texts[:20]]
    ar_count = languages.count('ar')
    en_count = languages.count('en')
    
    primary_language = 'ar' if ar_count > en_count else 'en'
    
    # Group by subject area
    subject_areas = {}
    for _, row in df.iterrows():
        subject = row['subject_area']
        training = row['training_name']
        
        if subject not in subject_areas:
            subject_areas[subject] = []
        
        training_record = {
            'name': training,
            'start_date': row.get('start_date'),
            'end_date': row.get('end_date')
        }
        subject_areas[subject].append(training_record)
    
    return {
        'primary_language': primary_language,
        'subject_areas': subject_areas,
        'total_records': len(df)
    }


def get_unique_subjects_and_courses(user_data):
    """Extract unique subject areas and all training names."""
    subjects = list(user_data['subject_areas'].keys())
    all_courses = []
    
    for subject, courses in user_data['subject_areas'].items():
        for course in courses:
            all_courses.append({
                'subject': subject,
                'name': course['name'],
                'start_date': course.get('start_date'),
                'end_date': course.get('end_date')
            })
    
    return subjects, all_courses