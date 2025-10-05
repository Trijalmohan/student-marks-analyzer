import pandas as pd
import numpy as np
import os
sample_path = "students_sample.csv"
sample_df = pd.DataFrame([
    {"StudentID": "S001", "Name": "Asha",   "Math": 92, "Science": 88, "English": 76},
    {"StudentID": "S002", "Name": "Rahul",  "Math": 85, "Science": 90, "English": 90},
    {"StudentID": "S003", "Name": "Priya",  "Math": 92, "Science": 85, "English": 88},
    {"StudentID": "S004", "Name": "Vikram", "Math": 70, "Science": 75, "English": 80},
    {"StudentID": "S005", "Name": "Neha",   "Math": 92, "Science": 88, "English": 76},
])
sample_df.to_csv(sample_path,index=False)
def readstudent_csv(path):
    df =pd.read_csv(path)
    cols_lowe = [c.lower() for c in df.columns]
    id =None
    name= None
    for cand in ("studentid","id","roll","rollno"):
        if cand in cols_lowe:
            id = df.columns[cols_lowe.index(cand)]
            break
    for cand in ("name","studentname","student_name"):
        if cand in cols_lowe:
            name =df.columns[cols_lowe.index(cand)]
            break
    if id is None:
        id =df.columns[0]
    if name is None:
        for c in df.columns:
            if c != id and df[c].dtype == object:
                name =c
                break
        if name is None:
            name = df.columns[1] if len(df.columns) >1 else df.columns[0]
    subject_cols = [c for c in df.columns if c not in (id,name)]
    return df , id , name , subject_cols
df , id , name , subject_cols = readstudent_csv(sample_path)


def valid_prepare(df , subject_cols , full_marks =100 , missing_policy ='fill_zero'):
    for c in subject_cols:
        df[c] = pd.to_numeric(df[c],errors = 'coerce')
    invalid_report = {c : df[c].isna().sum() for c in subject_cols if df[c].isna().sum() >0}
    print("invalid report :",invalid_report)

    if missing_policy == "fill_zero":
        df[subject_cols] =  df[subject_cols].fillna(0)
    elif missing_policy == "drop":
        df= df.dropna(subset = subject_cols)
    elif missing_policy == "raise":
        if not invalid_report:
            raise ValueError(f"Invalid marks found :{invalid_report}")
    for c in subject_cols:
        df[c] = df[c].clip(lower = 0 ,upper = full_marks)
    return df
    
df =valid_prepare(df , subject_cols , full_marks =100 , missing_policy ='fill_zero')

def compute_scores(df,subject_cols , full_marks =100):
    df['Total'] = df[subject_cols].sum(axis =1)
    df['Average'] = df[subject_cols].mean(axis =1)
    df['Percentage'] = df ['Total'] /(len(subject_cols) * full_marks) *100
    max_possible = len(subject_cols) *full_marks

    df['Total'] = df['Total'].round(2)
    df['Percentage'] = df['Percentage'].round(2)
    return df

df = compute_scores(df , subject_cols ,full_marks =100)

df['Rank'] = df['Total'].rank(method  = 'dense' ,ascending = False).astype(int)

topper_list =[]
for subj in subject_cols:
    maxmark = df[subj].max()
    topper = df[df[subj] == maxmark] [[id, name ,subj]].copy()
    topper['Subject'] = subj
    topper_list.append(topper.rename(columns = {subj: 'TopScore'}))
subject_topper_df = pd.concat(topper_list ,ignore_index = True)


stats = []
for subj in subject_cols:
    stats.append({
        "subject": subj,
        "Mean": df[subj].mean().round(2),
        "Median" :df[subj].median().round(2),
        "stdev" : df[subj].std().round(2),
        "TopScore" : df[subj].max().round(2)
    })
stats_df = pd.DataFrame(stats)


sample_path = "students_sample.csv"
results_path = "results.csv"
toppers_path = "subject_toppers.csv"
stats_path = "class_stats.csv"

df.to_csv(results_path , index = False)
subject_topper_df.to_csv(toppers_path , index = False)
stats_df.to_csv(stats_path , index =False)

print("\n Files creates:")
print("- sample csv:",sample_path)
print("- results csv:",results_path)
print("- toppers csv:",toppers_path)
print("- stats csv:",stats_path)

print("Topper students are :")
print(df.sort_values(['Total','Average'],ascending = [False,False])
      [[id , name ,'Total' , 'Average' , 'Percentage' , 'Rank']].head(10))
