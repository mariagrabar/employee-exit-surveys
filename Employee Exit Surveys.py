#!/usr/bin/env python
# coding: utf-8

# # Analyzing Employee Exit Surveys to Improve Retention Strategies
# 
# In this project, we'll work with exit surveys from employees of the [Department of Education, Training and Employment](https://en.wikipedia.org/wiki/Department_of_Education_(Queensland)) (DETE) and the Technical and Further Education (TAFE) institute in Queensland, Australia. By analyzing the data collected from these surveys, organizations can gain insights into the underlying causes of employee dissatisfaction and tailor their retention strategies more effectively.
# 
# As a result of this project, we aim to answer the following questions: 
# - Are employees who only worked for the institutes for a short period of time resigning due dissatisfaction? What about employees who have been there longer?
# - Are younger employees resigning due to dissatisfaction? What about older employees?
# - Do female employees resign due to dissatisfaction more than male employees?
# - What institution has more ex-employees who resigned due to dissatisfaction?
# 
# ## Summary of results 
# - Employees with more than 7 years of work experience are more likely to quit due to some kind of dissatisfaction than the ones who worked for a short period of time.
# - 35% of young employees are resigning due to dissatisfaction. However, the number increases till 42% for older employees.
# - There is no relationship between resignation due to some kind of dissatisfaction and gender.
# - DETE has a twice higher proportion of employees resigning due to dissatisfaction, compared to TAFE.
# 
# ## Data dictionary 
# Below is a preview of a couple columns we'll work with from the `dete_survey.csv`:
# - `ID`: An id used to identify the participant of the survey
# - `SeparationType`: The reason why the person's employment ended
# - `Cease Date`: The year or month the person's employment ended
# - `DETE Start Date`: The year the person began employment with the DETE
# 
# Below is a preview of a couple columns we'll work with from the `tafe_survey.csv`:
# - `Record ID`: An id used to identify the participant of the survey
# - `Reason for ceasing employment`: The reason why the person's employment ended
# - `LengthofServiceOverall. Overall Length of Service at Institute (in years)`: The length of the person's employment (in years)
# 
# ## 1: Data cleaning
# ### Primary data exploration
# 
# We'll start by reading the datasets into pandas.

# In[1]:


# importing pandas and numpy using their common aliases
import pandas as pd
import numpy as np

dete_survey = pd.read_csv('dete_survey.csv')
tafe_survey = pd.read_csv('tafe_survey.csv') 


# Now we're going to print information about information about both dataframes, as well as the first few rows.

# In[2]:


pd.options.display.max_columns = 150 # to avoid truncated output

# for DETE survey
print(dete_survey.info()) # information about data
dete_survey.head() # first few entries


# Observations for the `DETE` survey:
# - 822 entries, 56 columns
# - Every other column except `Id` is object or boolean datatype
# - Although it states there are no null values in the `DETE Start Date`, it contains a `Not Stated` value

# In[3]:


# counting the number of null values in 'DETE Start Date'
dete_survey['DETE Start Date'].isnull().value_counts()


# Now we've confirmed that `Not Stated` is not represented as `NaN`. We will keep that as a note for now and will move on to the `tafe_survey`.

# In[4]:


# for TAFE survey
print(tafe_survey.info()) # information about data
tafe_survey.head() # first few entries


# Observations for the `TAFE` survey:
# - 702 rows, 72 columns
# - Every other column except `Id` is object datatype
# 
# Observations for both dataframes: 
# - Both dataframes contain many columns that we don't need to complete our analysis (e.g. `WorkUnitViews..`)
# - Each dataframe contains many of the same columns, but the column names are different (e.g. `Ill Health` and `Contributing Factors. Ill Health`)
# - There are multiple columns that indicate an employee resigned because they were dissatisfied (e.g. `Contributing Factors..`)
# 
# ### Fixing Missing Values 
# 
# As we noticed before, `Not Stated` should be represented as `NaN` in the `dete_survey` dataframe. 

# In[5]:


# reading the file again, specifying the missing values
dete_survey = pd.read_csv('dete_survey.csv', na_values = 'Not Stated')

# proving that the method has worked and null values are identified
dete_survey['DETE Start Date'].isnull().value_counts()


# Successful! Now Python can see 73 null values in the dataframe. Moving on.
# 
# ### Dropping Unnecessary Values
# 
# To make the dataframes easier to work with, we will drop columns that are not related to the primary goals of our analysis. 
# 
# As mentioned before, we want to focus on columns that contain resignation reasons and contributing factors, ages and job duration.

# In[6]:


# dropping unnecessary columns in DETE survey
dete_survey_updated = dete_survey.drop(dete_survey.columns[28:49], axis=1)
dete_survey_updated.head()


# In[7]:


# dropping unnecessary columns in DETE survey
tafe_survey_updated = tafe_survey.drop(tafe_survey.columns[17:66], axis=1)
tafe_survey_updated.head()


# ### Cleaning Common Column Names
# 
# Each dataframe contains many of the same columns, but the column names are different. Below are some of the columns we'd like to use for our final analysis, in `dete_survey` and `tafe_survey`, respectively:
# 
# - `ID` and `Record ID`
# - `SeparationType` and `Reason for ceasing employment`
# - `Cease Date` and `CESSATION YEAR`
# - `Age` and `CurrentAge. Current Age`
# - `Gender` and `Gender. What is your gender?`
# - `DETE Start Date` 
# - `LengthofServiceOverall. Overall Length of Service at Institute (in years)` (only for TAFE)
# 
# Because we eventually want to combine them, we'll have to standardize the column names. 

# In[8]:


# removing capitalization, removing whitespace from the end, replacing spaces with underscores
dete_survey_updated.columns = dete_survey_updated.columns.str.replace(' ', '_').str.strip().str.lower()

# checking if the column names have updated
dete_survey_updated.columns


# In[9]:


# standardizing TAFE column anmes according to DETE column names
tafe_survey_updated = tafe_survey_updated.rename(columns={'Record ID': 'id', 
                           'CESSATION YEAR': 'cease_date', 
                           'Reason for ceasing employment': 'separationtype',
                           'Gender. What is your Gender?': 'gender',
                           'CurrentAge. Current Age': 'age',
                           'Employment Type. Employment Type': 'employment_status',
                           'Classification. Classification': 'position', 
                           'LengthofServiceOverall. Overall Length of Service at Institute (in years)': 'institute_service',
                           'LengthofServiceCurrent. Length of Service at current workplace (in years)': 'role_service', })

tafe_survey_updated.columns


# Below, we can see that now columns that contain the same type of information in both dataframes have the same names.

# In[10]:


display(tafe_survey_updated.head(1))
dete_survey_updated.head(1)


# ### Filtering the Resignation Respondents
# 
# If we look at the tables above, there are different `separationtype` values. For this project, we only need to consider survey respondents who *resigned*.

# In[11]:


# checking 'separationtype' value variations and frequency for DETE
dete_survey_updated['separationtype'].value_counts()


# Interesting observation for the `dete_survey` - there are different `Resignation` types, all of which should be taken into account.

# In[12]:


# checking 'separationtype' value variations and frequency for TAFE
tafe_survey_updated['separationtype'].value_counts()


# Compared to DETE, TAFE contains only one `Resignation` category.

# In[13]:


# selecting DETE correspondents who resigned
dete_resignation_filter = dete_survey_updated['separationtype'].str.contains('Resignation')
dete_resignations = dete_survey_updated[dete_resignation_filter].copy() # to avoid SettingWithCopy Warning

dete_resignations.head()


# As we can see, we've isolated resignation-related DETE respondents successfully. Let's repeat with the TAFE survey.

# In[14]:


# selecting TAFE correspondents who resigned
tafe_resignation_filter = tafe_survey_updated['separationtype'].str.contains('Resignation', na=False)
tafe_resignations = tafe_survey_updated[tafe_resignation_filter].copy() # to avoid SettingWithCopy Warning

tafe_resignations.head()


# Likewise, we've also isolated resignation-related DETE respondents.
# 
# ### Veryfying the Employment Dates
# 
# In this step, we'll focus on verifying that the years in the `cease_date` and `dete_start_date` columns fall within the 1940-2024 period.
# 
# Reason to choose 2024 as the maximum value: 
# - Since the `dete_start_date` is the first employment year and the `cease_date` is the last employment year, it doesn't make sense to have years after the current date.
# 
# Reason to choose 1940 as the minimum value: 
# - Given that most people in this field start working in their 20s, it's also unlikely that the start date was before the year 1940

# In[15]:


# viewing the unique DETE cease years
dete_resignations['cease_date'].value_counts()


# To make the formatting in the `cease_date` consistent, we will clean the column a little.

# In[16]:


# extracting cease dates for DETE
dete_resignations['cease_date'] = dete_resignations['cease_date'].str.extract(r'(\d{4})').astype(float)

# checking for the cease date consistency for DETE
dete_resignations['cease_date'].value_counts()


# In[17]:


# checking for the start date consistency for TAFE
dete_resignations['dete_start_date'].value_counts()


# In[18]:


# checking for the cease date consistency for TAFE
tafe_resignations['cease_date'].value_counts()


# All dates fall within the desired range from 1940 to 2024.
# 
# Let's visualize and compare the distribution of `cease_date` with a boxplots for both DETE and TAFE.

# In[19]:


# importing matplotlib for building graphs
import matplotlib.pyplot as plt
get_ipython().run_line_magic('matplotlib', 'inline')

# specifying the bar char content
fig, (ax1, ax2)= plt.subplots(1,2, figsize=(6,4))
dete_resignations['cease_date'].value_counts().sort_index().plot(kind='bar', ax=ax1)
tafe_resignations['cease_date'].value_counts().sort_index().plot(kind='bar', ax=ax2)
ax1.set_xlabel('dete_cease_date')
ax2.set_xlabel('tafe_cease_date')


# `2012` seems to be one of the most frequent resignation months in both DETE and TAFE. Apart from that, the main resignation years don't show exact match. However, we're only focused on the reasons of resignation, not the dates, so we'll keep column as they are. 

# In[20]:


# check if cease_date is greater than start_date
(dete_resignations['cease_date'] - dete_resignations['dete_start_date']).unique()


# We can also confirm that all cease dates are followed by start dates, not vice versa.

# ### Adding the DETE institute service column
# 
# As TAFE survey already has the `institute_service` column, we will add the same one to the DETE dataframe. We do it to ensure that both surveys can be analyzed together.

# In[21]:


# adding the new column
dete_resignations['institute_service'] = (dete_resignations['cease_date'] - dete_resignations['dete_start_date'])

# confirming that the column appeared
dete_resignations['institute_service'].head()


# ### Identifying Dissatisfed Employees
# Now, we'll identify the employees who resigned due to dissatisfaction.
# 
# Below are the columns we'll use to categorize employees as "dissatisfied" from each dataframe.
# 
# 1. tafe_survey_updated:
# `Contributing Factors. Dissatisfaction`
# `Contributing Factors. Job Dissatisfaction`
# 
# 2. dete_survey_updated:
# `job_dissatisfaction`
# `dissatisfaction_with_the_department`
# `physical_work_environment`
# `lack_of_recognition`
# `lack_of_job_security`
# `work_location`
# `employment_conditions`
# `work_life_balance`
# `workload`
# 
# If the employee indicated any of the factors above caused them to resign, we'll mark them as `dissatisfied` in a new column.

# In[22]:


# viewing dissatisfaction values in TAFE
print('Unique values in "Contributing Factors. Dissatisfaction":')
print(tafe_resignations['Contributing Factors. Dissatisfaction'].unique())
print('\n')
print('Unique values in "Contributing Factors. Job Dissatisfaction":')
print(tafe_resignations['Contributing Factors. Job Dissatisfaction'].unique())


# As we notice, responses for both columns follow the same logic, so we assume that:
# 
#     - `-` means `No`
#     - `(Name of the Column)` means `Yes`
#     - `nan` means `NaN`
#     
# To identify the desired respondents, we will turn the reponses to `True`, `False` and `NaN`.

# In[23]:


# writing a function that will update the responses into a new format
def update_vals(value):
    if value == '-':
        return False
    elif pd.isnull(value):
        return np.nan
    else:
        return True
    
columns = ['Contributing Factors. Dissatisfaction', 
        'Contributing Factors. Job Dissatisfaction']
# to avoid the SettingWithCopy Warning 
tafe_resignations_up = tafe_resignations.copy()
# applying the function to TAFE survey
tafe_resignations_up[columns] = tafe_resignations_up[columns].applymap(update_vals)
# ensuring the function worked
tafe_resignations_up['Contributing Factors. Dissatisfaction'].value_counts()


# We can see that dissatisfied ex-`TAFE` employees were successfully identified. We don't need to repeat the same procedure for `DETE` as the data is already recorded in the desired format.
# 
# As the next step, we'll create a separate column `Dissatisfied` that will combine the result of both columns.

# In[24]:


# returns the result if dissatisfaction was True at least once
tafe_resignations_up['dissatisfied'] = tafe_resignations_up[columns].any(axis=1, skipna=False)
# confirming the result
tafe_resignations_up['dissatisfied'].value_counts(dropna = False)


# We can confirm that there are 91 dissatisfied ex-`TAFE` employees identified. Let's repeat the same procedure with `DETE`.

# In[25]:


# isolating desired columns in a list
columns = ['job_dissatisfaction', 
           'dissatisfaction_with_the_department',
           'physical_work_environment',
           'lack_of_recognition',
           'lack_of_job_security', 
           'work_location',
           'employment_conditions',
           'work_life_balance',
           'workload']

# to avoid the SettingWithCopy Warning
dete_resignations_up = dete_resignations.copy()
# returns the result if dissatisfaction was True at least once
dete_resignations_up['dissatisfied'] = dete_resignations_up[columns].any(axis=1, skipna=False)
# confirming the result
dete_resignations_up['dissatisfied'].value_counts(dropna = False)


# We've identified 149 ex-`DETE` employees who mentioned dissatisfaction in their surveys.

# ### Combining the Data
# At this step, we'll aggregate the data according to the `institute_service` column.
# 
# First, we'll add a column to each dataframe that will allows us to easily distinguish between the two.

# In[26]:


# to confirm that data was successfully combined
print(dete_resignations_up.shape)
print(tafe_resignations_up.shape)


# In[27]:


# 'identifier' for DETE
dete_resignations_up['institute'] = 'DETE'
# 'identifier' for TAFE
tafe_resignations_up['institute'] = 'TAFE'

combined = pd.concat([dete_resignations_up, tafe_resignations_up], ignore_index = True)
# the number of rows and columns should be the sum of rows and columns from non-combined dataframes
combined.shape


# The data was successfully combined. 
# 
# ### Dropping Unnecessary Columns
# To ensure that our analysis is valid, we'll also drop columns with less than 500 non-null values.

# In[28]:


# dropping columns with less than 500 non-null values
combined_updated = combined.dropna(axis='columns', thresh = 500).copy()
combined_updated.info()


# ### Cleaning the Dissatisfied Column
# As our analysis is focused on the employee dissatisfaction, we need to make sure that the column is clean and ready for the analysis.

# In[29]:


# confirming the True/False format and finding the number of missing values
combined_updated['dissatisfied'].value_counts(dropna=False)


# We've identified 8 missing values from the `dissatisfied` column. As this column is crucial for our analysis, we won't drop null values. Instead, we will replace them with the value that occurs most frequently in this column. 

# In[30]:


# finding the most frequently occurring value
most_occuring_val_dissatisfied = combined_updated['dissatisfied'].mode()[0]
# filling empty spaces with the most frequently ocurring value
combined_updated['dissatisfied'].fillna(most_occuring_val_dissatisfied, inplace=True)
# confirming the replacement was successful
combined_updated['dissatisfied'].value_counts(dropna=False)


# ### Cleaning the Service Column
# We also need to ensure that the service column is clean and ready for the analysis. First, we'll make sure that the data in the `institute_service` column is standardized. 

# In[31]:


# checking unique values in the 'institute_service' column and their frequencies
combined_updated['institute_service'].value_counts()


# As we can see, the data is presented in many different forms. To solve this issue, we'll convert these numbers into categories. Based on [this article](https://www.businesswire.com/news/home/20171108006002/en/Age-Number-Engage-Employees-Career-Stage), understanding employee's needs according to career stage instead of age is also more effective. 
# 
# Our definitions would be: 
# - `New`: Less than 3 years at a company
# - `Experienced`: 3-6 years at a company
# - `Established`: 7-10 years at a company
# - `Veteran`: 11 or more years at a company

# In[32]:


# converting all values in the 'institute_service' column to strings
combined_updated['institute_service'] = combined_updated['institute_service'].astype(str)

# extracting digits and converting them to floats
combined_updated['institute_service'] = combined_updated['institute_service'].str.extract(r'(\d+)').astype(float)

# checking updated institute service values
combined_updated['institute_service'].value_counts()


# The conversion was successful. Next, we'll map each value to one of the career stage definitions above.

# In[33]:


# creating a function that maps years of experience to career stage
def years_to_stages(val):
    if pd.isnull(val):
        return np.nan
    elif val < 3:
        return 'New'
    elif 3 <= val <= 6:
        return 'Experienced'
    elif 7 <= val <= 10:
        return 'Established'
    else:
        return 'Veteran'

# applying the function and creating a new column
combined_updated['service_cat'] = combined_updated['institute_service'].apply(years_to_stages)
# checking if the new column was created and the values are correct
combined_updated.head()


# As a final step, we will replace the missing values in the `institute_service` column to the most frequently ocurring ones.

# In[34]:


# checking the number of missing values
combined_updated['service_cat'].value_counts(dropna=False)


# We need to replace 88 missing values.

# In[35]:


# finding the most frequently occurring value
most_occuring_val_service = combined_updated['service_cat'].mode()[0]
# filling empty spaces with the most frequently ocurring value
combined_updated['service_cat'].fillna(most_occuring_val_service, inplace=True)
# confirming the replacement was successful
combined_updated['service_cat'].value_counts(dropna=False)


# ### Cleaning the Age column
# We will repeat the procedures with the `age` column as well, to make sure the data is ready for analysis.

# In[36]:


# displaying unique age values and their frequencies
combined_updated['age'].value_counts()


# The data should be displayed in a standardized way, so we will first extract age and then group it into categorical columns. Our columns will be:
# - `<20`
# - `21-30`
# - `31-40`
# - `41-50`
# - `51-60`
# - `>61`  

# In[37]:


# extracting the age number
combined_updated['age'] = combined_updated['age'].astype(str).str.extract(r'(\d+)').astype(float)
combined_updated['age'].value_counts()


# The ages were successfully extracted. Now we can group them into categorical columns for easier visualization. 

# In[38]:


# creating a function that maps years of experience to career stage
def ages_to_categories(val):
    if pd.isnull(val):
        return np.nan
    elif val < 20:
        return '<20'
    elif 21 <= val <= 30:
        return '21-30'
    elif 31 <= val <= 40:
        return '31-40'
    elif 41 <= val <= 50:
        return '41-50'
    elif 51 <= val <= 60:
        return '51-60'
    else:
        return '>61'

# applying the function and creating a new column
combined_updated['age_cat'] = combined_updated['age'].apply(ages_to_categories)
# checking if the new column was created and the values are correct
combined_updated.head()


# Finally, we need to replace missing values in the `age_cat` column.

# In[39]:


combined_updated['age_cat'].value_counts(dropna=False)


# More specifically, we'll need to replace 55 values.

# In[40]:


# finding the most frequently occurring value
most_occuring_val_age = combined_updated['age_cat'].mode()[0]
# filling empty spaces with the most frequently ocurring value
combined_updated['age_cat'].fillna(most_occuring_val_age, inplace=True)
# confirming the replacement was successful
combined_updated['age_cat'].value_counts(dropna=False)


# As 41-50 was the most frequently occuring category, NaN values are now associated with that group.

# ### Cleaning the Gender column 
# Let's explore how standardized the gender column is by displaying its unique values and frequencies.

# In[41]:


# displaying unique age values and their frequencies
combined_updated['gender'].value_counts(dropna=False)


# The values are standardized but we still need to replace missing values.

# In[42]:


# finding the most frequently occurring value
most_occuring_val_gender = combined_updated['gender'].mode()[0]
# filling empty spaces with the most frequently ocurring value
combined_updated['gender'].fillna(most_occuring_val_gender, inplace=True)
# confirming the replacement was successful
combined_updated['gender'].value_counts(dropna=False)


# ## 2: Data Analysis
# ### Percentage of Dissatisfied Employees Per Experience Group
# We will aggregate the `dissatisfied` column and calculate the number of people in each experience group to find the percentage and compare.

# As the replacement of missing values was successful, we will group the `dissatisfied` responses according to the `service_cat` group.

# In[43]:


# grouping dissatisfied responses
pivot_service = combined_updated.pivot_table(values = 'dissatisfied', index = 'service_cat')
# setting the order from lowest to highest number of service years
desired_order_service = ['New', 'Experienced', 'Established', 'Veteran']
# sorting accordigly
pivot_service = pivot_service.reindex(desired_order_service)
pivot_service


# In[44]:


# visualizing the results
plot = pivot_service.plot(kind = 'bar', title = 'Employee Dissatisfaction by Years in Service', legend=False, rot=45)
# removing ticks for cleaner visual
plot.tick_params(axis='both', which='both', bottom=False, top=False, left=False, right=False)
# removing axis labels
plot.set_xlabel('')  # Remove x-axis label
plot.set_ylabel('')
plt.show()


# We can make a tentative conclusion that employees with more than 7 years of work experience are more likely to quit due to some kind of dissatisfaction. 

# ### Percentage of Dissatisfied Employees Per Age Group

# As previously, we will aggregate the `dissatisfied` column and calculate the number of people in each age group to find the percentage and compare.

# In[45]:


# grouping by age
pivot_age = combined_updated.pivot_table(index='age_cat', values='dissatisfied')
# setting up the ascending order
desired_order_age = ['21-30', '31-40', '41-50', '51-60', '>61']
# sorting accordigly
pivot_age = pivot_age.reindex(desired_order_age)
pivot_age


# In[46]:


# visualizing the results
plot = pivot_age.plot(kind = 'bar', title = 'Employee Dissatisfaction by Age Group', legend=False, rot=45)
# removing ticks for cleaner visual
plot.tick_params(axis='both', which='both', bottom=False, top=False, left=False, right=False)
# removing axis labels
plot.set_xlabel('')  # Remove x-axis label
plot.set_ylabel('')
plt.show()


# The plot above tells us that the employee dissatisfaction remains similar in all age groups, varying from 35% to 42%. 
# 
# However, we can see gradual increase in the height of the bars meaning that, with age employee dissatisfaction increases.

# ### Percentage of Dissatisfied Employees per Gender
# We're going to use the same method to explore the relationship between gender and resignation due to dissatisfaction.

# In[47]:


# grouping by gender
pivot_gender = combined_updated.pivot_table(index='gender', values='dissatisfied')
pivot_gender


# In[48]:


# visualizing the results
plot = pivot_gender.plot(kind = 'bar', title = 'Employee Dissatisfaction by Gender', legend=False, rot=45)
# removing ticks for cleaner visual
plot.tick_params(axis='both', which='both', bottom=False, top=False, left=False, right=False)
# removing axis labels
plot.set_xlabel('')  # Remove x-axis label
plot.set_ylabel('')
plt.show()


# As we can see, there is no significant difference in resignation due to dissatisfaction by gender.

# ### Percentage of Dissatisfied Employees by Institute
# As a final step of our data analysis, we will check the proportion of employees who resigned due to some kind of dissatisfaction depending on the institute: DETE and TAFE.

# In[49]:


# grouping by institute
pivot_institute = combined_updated.pivot_table(index='institute', values='dissatisfied')
pivot_institute


# In[50]:


# visualizing the results
plot = pivot_institute.plot(kind = 'bar', title = 'Employee Dissatisfaction by Institute', legend=False, rot=45)
# removing ticks for cleaner visual
plot.tick_params(axis='both', which='both', bottom=False, top=False, left=False, right=False)
# removing axis labels
plot.set_xlabel('')  # Remove x-axis label
plot.set_ylabel('')
plt.show()


# The graph tells us that almost 50% of DETE respondents reported dissatisfaction. It is twice more than what was identified in the TAFE survey. 

# ## 3: Conclusions
# 
# This is the end of the cleaned and analyzed employee exit survey data from the Department of Education, Training and Employment (DETE) and the Technical and Further Education (TAFE) institute in Queensland, Australia.
# 
# The following observations were made:
# 
# - Over 50% of employees with more than 7 years of experience report job dissatisfaction as a reason for their resignation.
# - Employees over 60 years of age were 7% more dissatisfied at the time of leaving compared to younger employees (e.g. 31-40).
# - There was only a 4% difference in male (40%) versus female (36%) employees citing dissatisfaction as their primary resignation reason.
# - The dissatisfaction is more prevalent in the Department of Education, Training and Employment (DETE) with 49% of people resigning compared to only 28% of TAFE employees.
# 
# Based on the above findings, it is recommended that further survey be done on 'experienced' and 'veteran' employees to assess the reasons for employee dissatisfaction and what can be done to improve it.

# In[ ]:




