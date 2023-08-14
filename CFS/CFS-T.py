# Author: Christopher Romeo
# XML files have not been tested
import tkinter as tk
from tkinter import *
from tkinter.simpledialog import askstring
import tkinter.messagebox as mbox
from tkinter import filedialog
import pandas as pd
from pandas import ExcelFile
import tabulate
from tabulate import tabulate
import os
import glob
from datetime import date
import re
from sodapy import Socrata
import requests
from geopy.geocoders import Nominatim
import time
from tkinter.filedialog import askopenfilename

pd.options.mode.chained_assignment = None


# Functions requiring user updates are upfront
# Only the API calls currently require changes

# APIs
# The function is edited by the user with the required api information per agency. The information is then sent to
# the socrata_api function or the json_api function to be processed.
def api_calls(opath, agency_ref):
    # Add the API code here. Be sure to add your API user/pass and token.
    api_agency_ref = agency_ref
    api_li = []
    api_liz = []
    opath = opath
    usrname = "***"
    psword = "***"
    myapptoken = "***"

    # Replace the first three variables (Agency Name, URL, and Client-Code) to modify for specific agency
    # St. Petersburg, FL
    api_li, api_liz = socrata_api("St.Pete API", "stat.stpete.org", "2eks-pg5j", myapptoken, usrname,
                                  psword, opath, api_agency_ref, api_li, api_liz)

    # Montgomery County Police Department
    api_li, api_liz = socrata_api("MCPD API", "data.montgomerycountymd.gov", "98cc-bc7d", myapptoken, usrname,
                                  psword, opath, api_agency_ref, api_li, api_liz)

    # New Orleans, LA Police Department
    api_li, api_liz = socrata_api("NOPD API", "data.nola.gov", "nci8-thrr", myapptoken, usrname,
                                  psword, opath, api_agency_ref, api_li, api_liz)

    # Seattle, WA PD
    api_li, api_liz = socrata_api("Seattle API", "data.seattle.gov", "33kz-ixgy", myapptoken, usrname,
                                  psword, opath, api_agency_ref, api_li, api_liz)

    # Fort Lauderdale, FL
    api_li, api_liz = socrata_api("Fort Lauderdale API", "fortlauderdale.data.socrata.com", "d7g7-86hw",
                                  myapptoken, usrname, psword, opath, api_agency_ref, api_li, api_liz)

    # Los Angeles PD, CA
    api_li, api_liz = socrata_api("LAPD API", "data.lacity.org", "84iq-i2r6", myapptoken, usrname,
                                  psword, opath, api_agency_ref, api_li, api_liz)

    # Corona PD, CA
    api_li, api_liz = socrata_api("Corona PD API", "corstat.coronaca.gov", "4sdt-qjy7", myapptoken, usrname,
                                  psword, opath, api_agency_ref, api_li, api_liz)

    # Jersey City PD, NJ
    api_li, api_liz = json_api("Jersey City",
                               "https://data.jerseycitynj.gov/api/explore/v2.1/catalog/datasets/calls-for-service-"
                               "call-codes/exports/json?select=%2A&limit=-1&lang=en&timezone=US%2FEastern&use_labels"
                               "=true&epsg=4326", opath, api_agency_ref, api_li, api_liz)

    return api_li, api_liz


# The function is used to standardize the connection to the Socrata open data api and pull the requested agency data.
# The function sends the data through the entire process to include column edits, date edits, and geocoding.
def socrata_api(agency, url, client_code, apptoken, username, password, opath, agencyref, api_li, api_liz):
    myapptoken = apptoken
    usrname = username
    psword = password
    cli_code = client_code
    api_agency_ref = agencyref
    api_li_copy = api_li
    api_liz_copy = api_liz

    client = Socrata(f"{url}",
                     myapptoken,
                     username=usrname,
                     password=psword)

    print(f"Now running: {agency}")

    try:
        results = client.get(f"{cli_code}", limit=1000)
        # Convert to pandas DataFrame
        results_df = pd.DataFrame.from_records(results)
        if results_df.empty:
            print(f"{agency} returned no data!")
            results_df.to_csv(f"{opath}/01_Original_{agency}.csv", index=False)
            pass
        else:
            # Save the original data
            results_df.to_csv(f"{opath}/01_Original_{agency}.csv", index=False)

            results_df, testing_df = replace_column_names(results_df, api_agency_ref, agency)
            print("This is the updated dataframe according to the data standard:")
            print(tabulate(results_df.head(5), headers='keys', tablefmt='psql'))
            print("This is the agency specific columns")
            print(tabulate(testing_df.head(5), headers='keys', tablefmt='psql'))

            # Send to date_edits function to process date/time
            results_df = date_edits(results_df)

            # Send the 2 dataframes to the AUID function to assign the AUID and add the agency column
            results_df, testing_df = auid_addition(results_df, testing_df, agency)

            # results_df.insert(0, 'Agency', agency)

            api_li_copy.append(results_df)

            results_df = location_coding(results_df)
            print("After Location:")
            print(results_df.head(5))

            # results_df = CFS.col_edit(results_df, columns_final)
            testing_df.to_csv(f"{opath}/02_Agency_Specific_{agency}.csv", index=False)
            # results_df = results_df[results_df.columns.intersection(columns_final)]

            api_liz_copy.append(results_df)

            results_df.to_csv(f"{opath}/03_Final_{agency}.csv", index=False)
    except requests.Timeout:
        print(f"Connection to {agency} failed.")
    except requests.RequestException:
        print("Unknown Error")

    return api_li_copy, api_liz_copy


# The function is used to standardize the process for traditional json requests and pull the requested agency data.
# The function sends the data through the entire process to include column edits, date edits, and geocoding.
def json_api(agency, url, opath, agencyref, api_li, api_liz):
    api_agency_ref = agencyref
    api_li_copy = api_li
    api_liz_copy = api_liz
    json_agency = agency
    json_url = url

    try:
        results_df = pd.read_json(json_url)
        if results_df.empty:
            print(f"{json_agency} returned no data!")
            results_df.to_csv(f"{opath}/01_Original_{json_agency}.csv", index=False)
            pass
        else:
            # Save the original data
            results_df.to_csv(f"{opath}/01_Original_{json_agency}.csv", index=False)

            results_df, testing_df = replace_column_names(results_df, api_agency_ref, json_agency)
            print("This is the updated dataframe according to the data standard:")
            print(tabulate(results_df.head(5), headers='keys', tablefmt='psql'))
            print("This is the agency specific columns")
            print(tabulate(testing_df.head(5), headers='keys', tablefmt='psql'))

            # Send to date_edits function to process date/time
            results_df = date_edits(results_df)

            # Send the 2 dataframes to the AUID function to assign the AUID and add the agency column
            results_df, testing_df = auid_addition(results_df, testing_df, json_agency)

            # results_df.insert(0, 'Agency', agency)

            api_li_copy.append(results_df)

            results_df = location_coding(results_df)
            print("After Location:")
            print(results_df.head(5))

            # results_df = CFS.col_edit(results_df, columns_final)
            testing_df.to_csv(f"{opath}/02_Agency_Specific_{json_agency}.csv", index=False)
            # results_df = results_df[results_df.columns.intersection(columns_final)]

            api_liz_copy.append(results_df)

            results_df.to_csv(f"{opath}/03_Final_{json_agency}.csv", index=False)
    except requests.Timeout:
        print(f"Connection to {json_agency} failed.")
    except requests.RequestException:
        print("Unknown Error")

    return api_li_copy, api_liz_copy


# The function updates each dataframe index to allow for a singular dataframe to be created.
def reindex_dataframes(li):
    reindexed_dataframes = []
    start_index = 0

    for ndf in li:
        end_index = start_index + len(ndf)
        new_index = pd.RangeIndex(start=start_index, stop=end_index)
        reindexed_df = ndf.set_index(new_index)
        reindexed_dataframes.append(reindexed_df)
        start_index = end_index

    return reindexed_dataframes


# The function extracts the Agency Reference sheet and creates a dataframe
def agency_reference():
    current_directory = os.path.dirname(os.path.abspath(__file__))
    agency_ref_path = os.path.join(current_directory, 'Agency Reference.xlsx')
    xls = ExcelFile(agency_ref_path)
    df_dict = xls.parse(xls.sheet_names[0], index_col=0)
    return df_dict


# The function asks the user for the file directory to pull local files
def input_file_directory():
    ipath = Tk()
    ipath.withdraw()
    ipath.directory = filedialog.askdirectory(initialdir="C:/", title="Input Directory for CFS Files")
    while ipath.directory == '':
        result = mbox.askyesno("File Selection Error", "No file directory chosen. Would you like to try again?")
        if result:
            ipath.directory = filedialog.askdirectory(initialdir="C:/", title="Input Directory for CFS Files")
        else:
            quit()
    print('The chosen input directory is: ' + ipath.directory)
    return ipath.directory


# The function asks the user for the file directory to save all files once complete
def output_file_directory():
    opath = Tk()
    opath.withdraw()
    opath.directory = filedialog.askdirectory(initialdir="C:/", title="Output Directory for CFS Translation Results")
    while opath.directory == '':
        result = mbox.askyesno("File Selection Error", "No file directory chosen. Would you like to try again?")
        if result:
            opath.directory = filedialog.askdirectory(initialdir="C:/", title="Output Directory for CFS Files")
        else:
            quit()
    print('The chosen output directory is: ' + opath.directory)
    return opath.directory


# Function to identify the specific agency for the file being processed. Allows the user to edit the name if needed.
def ask_agency(agency_name, fail_counter):
    counter = 3 - fail_counter
    win = tk.Tk()
    win.geometry("")
    win.withdraw()
    agency_initial_name = agency_name
    # print(agency_initial_name)
    enta = askstring(f'Agency. Tries Remaining: {counter}',
                     f'What is the responsible agency for the file: {agency_initial_name}?')
    win.destroy()
    if enta == '':
        print(f'No input given for: {agency_initial_name}')
        return agency_initial_name
    elif enta is None:
        print(f'No input is given for: {agency_initial_name}')
        return agency_initial_name
    else:
        print(f'Name has been changed to: {enta}')
        return enta


# Function to split up words that are in CamelCase.
def camel_case_split(identifier):
    matches = re.finditer('.+?(?:(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])|$)', identifier)
    return [m.group(0) for m in matches]


# Function to present the user with a window to acknowledge completion and provide a small preview of the data generated
def final_message(df, failed_agencies):
    def close():
        root.destroy()
        quit()

    failed = failed_agencies.copy()
    root = tk.Tk()
    root.geometry("2000x600")
    root.title("Final Output Preview")
    final_df = df
    root.protocol('WM_DELETE_WINDOW', close)

    screen = Text(root, height=200, width=1500)  # This is the text widget and parameters
    exit_button = Button(root, text="Exit", command=close)  # This is the exit button
    exit_button.pack(side="bottom")
    screen.pack(side="top")

    screen.insert(tk.END, tabulate(final_df.head(15), headers='keys', tablefmt='psql'))
    screen.insert(tk.END, "\n")
    screen.insert(tk.END, f"The following files were not processed: {failed}")

    root.mainloop()


# The primary function of the system
def calls_for_service(api_option, local_option):
    # The following code was used to enable all the data from a dataframe to be displayed in the run window (PyCharm)
    # The code is a part of the pandas package
    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', None)
    pd.set_option('display.max_colwidth', None)

    # Creates the Agency Reference Dataframe
    agency_ref = agency_reference()
    agency_check = agency_ref.index
    failed_agencies = []

    # Open the file explorer to allow the user to select both the input and output directories
    # ipath is the input directory path and opath is the output directory path
    # There will be two versions of this directory information to allow for faster testing

    # Call the functions for input and output directory folders
    # If you want to stop asking for the directory remove "input_file_directory()" with the absolute path of the desired
    # directory. Do the same for opath.

    opath = output_file_directory()  # Production Code

    # The following code creates empty lists to store all the dataframes
    li = []  # This list will be the unaltered dataframes
    liz = []  # This list will be the altered dataframes

    # The goal is to bring in each individual file and store it as its own dataframe and not as a large dictionary
    # Here we loop through the list of files previously scanned, read each one into a dataframe, and append to the list

    # api_option = APIs.api_yn()  # Set this to True if API calls are being made

    # API call
    if api_option:
        li, liz = api_calls(opath, agency_ref)
    else:
        print("No API calls")

    # Here I am attempting to make a list of the agency names based on the file
    if local_option:
        # Create a glob to hold the files for processing
        ipath = input_file_directory()  # Production Code
        csv_files_csv = glob.glob(ipath + '/*')

        file_dct = {}
        for f in csv_files_csv:
            agency_file_name = os.path.basename(f)
            head, sep, tail = agency_file_name.partition('_')
            file_dct[agency_file_name] = head

        for f in csv_files_csv:
            # Get the filename
            agency = os.path.basename(f)
            print(f"Now processing: {agency}")
            agency_found = False
            skip = False

            # This checks the agency dictionary against the agency reference sheet for the agency name
            if ".csv" in f or ".xlsx" in f or ".xls" in f or ".xml" in f:
                fail_counter = 0
                while agency_found is False:
                    if agency in file_dct:
                        # Set the agency name based on the dictionary that was built
                        agency = file_dct[agency]
                        if agency in agency_check:
                            print(f"Found the agency: {agency}")
                            agency_found = True
                        else:
                            print("Agency was not found. Requesting agency name.")
                            n_agency = ask_agency(agency, fail_counter)
                            if n_agency in agency_check:
                                agency = n_agency
                                agency_found = True
                            else:
                                fail_counter += 1
                                if fail_counter == 3:
                                    skip = True
                                    break
                                else:
                                    agency_found = False
                    else:
                        print("Agency was not found.")
                        agency = ask_agency(agency, fail_counter)  # Ask for user input on agency name
            else:
                print("This file is not supported!")
                skip = False

            if skip:
                print(f"System could not identify the responsible agency for: {agency}")
                failed_agencies.append(agency)
                continue

            # Read in the document based on format
            if ".csv" in f:
                temp_df = pd.read_csv(f)
                # Create a new processed sheet for each agency. No new data has been created.
                temp_df.to_csv(f"{opath}/01_Original_{agency}.csv", index=False)
                # Clean the data before injecting new content

                # HERE WE WANT TO RUN THE AGENCY REFERENCE DF AGAINST THE NEW SHEET AND RELABEL THE COLUMNS AS DEFINED
                # IN THE EXTERNAL SPREADSHEET. AGENCY SPECIFIC COLUMNS ARE EXTRACTED AND SEPARATED INTO A NEW DF

                temp_df, testing_df = replace_column_names(temp_df, agency_ref, agency)
                print("This is the updated dataframe according to the data standard:")
                print(tabulate(temp_df.head(5), headers='keys', tablefmt='psql'))
                print("This is the agency specific columns")
                print(tabulate(testing_df.head(5), headers='keys', tablefmt='psql'))

                # Send to date_edits function to process date/time
                temp_df = date_edits(temp_df)

                # Send the 2 dataframes to the AUID function to assign the AUID and add the agency column
                temp_df, testing_df = auid_addition(temp_df, testing_df, agency)

                # Add the modified dataframe to the list
                # Only the dataframe that is now in compliance with the data standard is added
                li.append(temp_df)

                # Send to LocationProcessing
                temp_df = location_coding(temp_df)
                # print("After Location:")
                # print(tabulate(temp_df.head(5)))

                # Now we save the modified agency file to its own separate file
                testing_df.to_csv(f"{opath}/02_Agency_Specific_{agency}.csv", index=False)

                # Add to the intersected list
                liz.append(temp_df)
                temp_df.to_csv(f"{opath}/03_Final_{agency}.csv", index=False)
                # print(temp_df.dtypes)
            elif ".xlsx" in f or ".xls" in f or ".xlsm" in f or ".xltx" in f or ".xltm" in f:
                temp_df = pd.read_excel(f)

                # Create a new processed sheet for each agency. No new data has been created.
                temp_df.to_csv(f"{opath}/01_Original_{agency}.csv", index=False)
                # Clean the data before injecting new content

                # HERE WE WANT TO RUN THE AGENCY REFERENCE DF AGAINST THE NEW SHEET
                temp_df, testing_df = replace_column_names(temp_df, agency_ref, agency)
                print("This is the updated dataframe according to the data standard:")
                print(tabulate(temp_df.head(5), headers='keys', tablefmt='psql'))
                print("This is the agency specific columns")
                print(tabulate(testing_df.head(5), headers='keys', tablefmt='psql'))

                # Send to date_edits function to process date/time
                temp_df = date_edits(temp_df)

                # Send the 2 dataframes to the AUID function to assign the AUID and add the agency column
                temp_df, testing_df = auid_addition(temp_df, testing_df, agency)

                # Add the modified dataframe to the list
                # Only the dataframe that is now in compliance with the data standard is added
                li.append(temp_df)

                # Send to location service testing
                temp_df = location_coding(temp_df)
                # print("After Location:")
                # print(tabulate(temp_df.head(5)))

                # Save the modified agency file
                testing_df.to_csv(f"{opath}/02_Agency_Specific_{agency}.csv", index=False)

                # Add to the intersected list
                liz.append(temp_df)
                temp_df.to_csv(f"{opath}/03_Final_{agency}.csv", index=False)
                # print(temp_df.dtypes)
            elif ".xml" in f:
                temp_df = pd.read_xml(f)
                # Create a new processed sheet for each agency. No new data has been created.
                temp_df.to_csv(f"{opath}/01_Original_{agency}.csv", index=False)
                # Clean the data before injecting new content

                # HERE WE WANT TO RUN THE AGENCY REFERENCE DF AGAINST THE NEW SHEET
                temp_df, testing_df = replace_column_names(temp_df, agency_ref, agency)
                print("This is the updated dataframe according to the data standard:")
                print(tabulate(temp_df.head(5), headers='keys', tablefmt='psql'))
                print("This is the agency specific columns")
                print(tabulate(testing_df.head(5), headers='keys', tablefmt='psql'))

                # Send to date_edits function to process date/time
                temp_df = date_edits(temp_df)

                # Send the 2 dataframes to the AUID function to assign the AUID and add the agency column
                temp_df, testing_df = auid_addition(temp_df, testing_df, agency)

                # add it to the updated dataframe to list
                li.append(temp_df)

                # Send to LocationProcessing
                temp_df = location_coding(temp_df)
                # print("After Location:")
                # print(tabulate(temp_df.head(5)))

                # Now we save the modified agency file to its own separate file
                temp_df.to_csv(f"{opath}/02_Agency_Specific_{agency}.csv", index=False)

                # Add to the intersected list
                liz.append(temp_df)
                temp_df.to_csv(f"{opath}/03_Final_{agency}.csv", index=False)
                # print(temp_df.dtypes)
            else:
                # Display a message to indicate the file extension found is not able to be converted at this time
                failed_agencies.append(agency)
                print(f"This file format is not available to be converted at this time: {agency}")

    # Does above but for the data with the removed columns
    reindexed_dataframes = reindex_dataframes(liz)

    if not reindexed_dataframes:
        print("No data was extracted. Please verify local files or API connections.")
    else:
        df2 = pd.concat(reindexed_dataframes, axis=0)

        df2.reset_index(drop=True, inplace=True)

        uid = "CFS"  # This is the uid for the project
        now = date.today()

        df2.index = df2.index.astype(str)
        df2.index.name = 'uid'
        df2.index = f"{uid}-{now}-" + df2.index

        df2['call type'] = df2['call type'].apply(call_type_edit)

        if 'merged address' in df2.columns:
            df2 = df2[['auid', 'agency', 'incident number', 'call date/time', 'dispatch date/time', 'call type',
                       'merged address', 'location (lat/long)', 'type of location', 'location code']]
        else:
            df2 = df2[['auid', 'agency', 'incident number', 'call date/time', 'dispatch date/time', 'call type',
                       'location (lat/long)', 'type of location', 'location code']]
        df2.to_csv(f"{opath}/00_Final_Archival.csv")
        print('')
        print('The following is the first 15 rows from the combined data:')
        print(tabulate(df2.head(15), headers='keys', tablefmt='psql'))
        print("The following files were not processed:")
        print(failed_agencies)
        # Send all unique call types to a separate file
        unique_df = df2
        unique_df.drop_duplicates(subset=['call type'], keep='first', inplace=True)
        unique_df = unique_df[["agency", "call type"]]
        unique_df['new call type'] = ''
        unique_df.to_csv(f"{opath}/001_Unique_Call_Types.csv")
        #
        # Final message to the user
        #
        final_message(df2, failed_agencies)
    quit()


# Location Processing
# The location_coding function modifies the location data to ensure compliance with the data standard:
# lat/long information is generated through cleaning and organizing the lat/long data provided or by combining the
# address/city/state information and sending to the geocoding function to be processed by the Nominatim service.
# If there are city acronyms, a dictionary txt file can be updated to annotate that, it will be used by this function to
# generate a python dictionary and update the data with the long form name (e.g., VAB translates to Virgina Beach).
def location_coding(df):
    dict1 = {}  # Create a blank dictionary

    current_dir = os.path.dirname(os.path.abspath(__file__))
    dict_path = os.path.join(current_dir, 'Dictionary.txt')

    with open(dict_path) as f:  # Import the dictionary from the text file
        for line in f:
            key_value = line.rstrip('\n').split(":")
            if len(key_value) == 2:
                dict1[key_value[0]] = key_value[1]

    dict2 = {v: k for k, v in dict1.items()}  # Swap the dictionary around since the city name appeared before the abv.

    working_df = df.copy()
    new_columns = []
    for col in working_df:
        ncol = col  # Sets the new column (ncol) variable to the column name from the dataframe
        ncol = camel_case_split(ncol)  # Splits the column name based on if CamelCase is present (produces a list)
        ncol = ' '.join(ncol)  # Joins the list back into a single string separated by a space
        ncol = ncol.lower()  # Lowers the string to allow easy comparison to the 'final_columns' list
        ncol = ncol.replace('_', ' ')  # Replaces the underscore with a space to allow better comparison
        new_columns.append(ncol)

    working_df.columns = new_columns

    # Add a column to the dataframe that captures how the lat/long conversion is done and give it a rating 1-4
    # 1 - directly from the agency, 2 - separate lat/lon joined from agency, 3 - block address conversion, 4 - no data
    working_df['location code'] = 4

    # By priority, we will conduct geocoding work if necessary. No geocoding is required if Lat/Long information is
    # already given.

    if 'location (lat/long)' in working_df.columns:
        working_df['location (lat/long)'] = working_df['location (lat/long)'].astype(str)

        for i in range(len(working_df['location (lat/long)'])):
            numbers_only = re.findall(r"-?\d+\.?\d*", working_df['location (lat/long)'].iloc[i])
            result = ' '.join(numbers_only)
            working_df['location (lat/long)'].iloc[i] = result

        for i in range(len(working_df['location (lat/long)'])):
            temp_lat_long = working_df['location (lat/long)'].iloc[i]
            if pd.isna(temp_lat_long):
                pass
            else:
                temp_lat_long = temp_lat_long.split()
                temp_lat_long.sort(reverse=True)
                temp_lat_long = ', '.join(temp_lat_long)
                working_df['location (lat/long)'].iloc[i] = temp_lat_long
            i += 1
        working_df['location code'] = 1

    elif 'latitude' in working_df.columns and 'longitude' in working_df.columns:
        print("Merging latitude and longitude information.")

        # Calculate the number of empty cells to determine whether to geoprocess or use lat/long info
        num_empty = round(pd.isna(working_df['latitude']).mean() * 100, 1)
        print(num_empty)

        if num_empty >= 50:
            if 'city' in working_df.columns:
                working_df = working_df.replace({'city': dict2})
                working_df['merged address'] = \
                    working_df['block address'] + ', ' + working_df['city'] + ', ' + working_df['state']
                # Send new location information to the geocoding function. **Comment this section to skip geocoding**
                working_df['location (lat/long)'] = \
                    working_df['merged address'].apply(lambda row: geocoding(row))
            elif 'city cfs' in working_df:
                working_df['merged address'] = \
                    working_df['block address'] + ', ' + working_df['city cfs'] + ', ' + working_df['state cfs']
                # Send new location information to the geocoding function. **Comment this section to skip geocoding**
                working_df['location (lat/long)'] = \
                    working_df['merged address'].apply(lambda row: geocoding(row))
        else:
            working_df['location (lat/long)'] = \
                working_df['latitude'].apply(str) + ', ' + working_df['longitude'].apply(str)
            working_df.drop('latitude', axis=1, inplace=True)
            working_df.drop('longitude', axis=1, inplace=True)
            working_df['location code'] = 2

    elif 'lat' in working_df.columns and 'long' in working_df.columns:
        print("Merging lat/long information.")
        working_df['location (lat/long)'] = working_df['lat'].apply(str) + ' ' + working_df['long'].apply(str)
        working_df.drop('lat', axis=1, inplace=True)
        working_df.drop('long', axis=1, inplace=True)
        working_df['location code'] = 2

    elif 'location' in working_df.columns:
        print("Working through location information.")
        working_df['location'] = working_df['location'].replace('\(|\)', '', regex=True)
        working_df['location'] = working_df['location'].replace('POINT', '', regex=True)
        working_df['location (lat/long)'] = working_df['location']
        working_df['location (lat/long)'] = working_df['location (lat/long)'].apply(lambda row: sort_nums(row))
        working_df.drop('location', axis=1, inplace=True)
        working_df['location code'] = 1

    elif 'block address' in working_df.columns and 'city' in working_df.columns:
        print("Converting Block Address and City Name to a Lat/Long.")
        # Create a new column in the dataframe to store the merged information
        working_df = working_df.replace({'city': dict2})
        working_df['merged address'] = \
            working_df['block address'] + ', ' + working_df['city'] + ', ' + working_df['state']
        # Create a new column to store the Lat/Long information
        # Send new location information to the geocoding function. **Comment this section to skip geocoding**
        working_df['location (lat/long)'] = working_df['merged address'].apply(lambda row: geocoding(row))
        working_df['location code'] = 3

    elif 'block address' in working_df.columns and 'city cfs' in working_df.columns:
        print("Converting Block Address and City Name to a Lat/Long.")
        # Create a new column in the dataframe to store the merged information
        working_df['merged address'] = \
            working_df['block address'] + ', ' + working_df['city cfs'] + ', ' + working_df['state cfs']
        # Create a new column to store the Lat/Long information
        # Send new location information to the geocoding function. **Comment this section to skip geocoding**
        working_df['location (lat/long)'] = working_df['merged address'].apply(lambda row: geocoding(row))
        working_df['location code'] = 3

    elif 'city' in working_df.columns and 'state' in working_df.columns:
        # temp_df.insert(3, 'merged location', (temp_df['block address'] + ' : ' + temp_df['location']))
        print("Merging city and state information.")
        working_df['city and state'] = working_df['city'] + ', ' + working_df['state']

    else:
        print("No location information available")

    if 'latitude' in working_df.columns:
        working_df.drop('latitude', axis=1, inplace=True)
    if 'longitude' in working_df.columns:
        working_df.drop('longitude', axis=1, inplace=True)
    if 'state' in working_df.columns:
        working_df.drop('state', axis=1, inplace=True)
    if 'city' in working_df.columns:
        working_df.drop('city', axis=1, inplace=True)
    if 'block address' in working_df.columns:
        working_df.drop('block address', axis=1, inplace=True)
    if 'state cfs' in working_df.columns:
        working_df.drop('state cfs', axis=1, inplace=True)
    if 'city cfs' in working_df.columns:
        working_df.drop('city cfs', axis=1, inplace=True)
    # Remove the comment from the below code if you want to see remove the combined address column.
    # if 'merged address' in working_df.columns:
    #     working_df.drop('merged address', axis=1, inplace=True)

    return working_df


# The sort_nums function sorts the latitude/longitude to ensure the data is in the proper format.
def sort_nums(row):
    newlocation = row
    numbers = ''

    if pd.isna(newlocation):
        print("No data to convert")

    else:
        newlocation = str(newlocation)
        numbers = [float(s) for s in re.findall(r'-?\d+\.?\d*', newlocation)]
        numbers.sort(key=lambda x: int(-x))
        print(f"This is the reorder lat/long info: {numbers}")

    return numbers


# The geocoding function takes the address information from each row in the dataframe and sends it to the Nominatim
# service to be processed.
def geocoding(address):
    time.sleep(2)
    geolocator = Nominatim(user_agent="CFS_App")
    location = address
    nlat_long = ''

    if pd.isna(location):
        print("No address")
    else:
        try:
            loc = geolocator.geocode(location, timeout=10)
            if loc is None:
                print(f"Nothing found for: {location}")
            else:
                nlat, nlon = loc.latitude, loc.longitude
                nlat_long = str(f"{nlat}, {nlon}")
                print(f"Service found {nlat_long} for {location}")
        except (AttributeError, KeyError, ValueError):
            print(location, "Error")

    return nlat_long


# Column Editing
# This section of functions will edit the column names for each dataframe to ensure compliance with the data standard
# that is defined in the Agency Reference Excel and to separate the agency specific columns into a separate dataframe.
# This module also modifies the date/time columns to conform to the Y/M/D/H/M/S standard, adds the agency unique
# identification number, and cleans the call type data to remove special characters.

# The replace_column_names function replaces column names with the correct data standard name as established in the
# Agency Reference Excel. The function also separates agency specific columns into a separate dataframe to be stored.
def replace_column_names(df_a, df_b, row_index):  # This function renames the columns based on an external spreadsheet
    win = tk.Tk()
    win.geometry("")
    win.withdraw()

    # Make a copy of the dataframe to not mess with the original
    temp_df = df_a.copy()
    specific_df = df_a.copy()

    try:
        # Get the values from the correct agency row DataFrame B (agency reference)
        column_name_check = df_b.loc[row_index].values
        # Create a list to map column names from DataFrame A to DataFrame B
        new_columns = []
        specific_columns = []
        # Iterate over columns in DataFrame A
        for col in temp_df:
            # Check if the column name is present in the desired column names from DataFrame B
            if col in column_name_check:
                # Get the index of the column name in column_names
                index = list(column_name_check).index(col)
                new_columns.append(df_b.columns[index])
                specific_df.drop(col, axis=1, inplace=True)
            else:
                # If the column name is not present in column_names, keep the original column name
                specific_columns.append(col)  # This captures the column and stores it for the specific agency file
                temp_df.drop(col, axis=1, inplace=True)

        # Rename columns in DataFrame A using the new columns list
        temp_df.columns = new_columns
        specific_df.columns = specific_columns

        if 'City' not in temp_df:
            temp_df.insert(0, 'City CFS', df_b.loc[row_index, 'City CFS'])

        if 'State' not in temp_df:
            temp_df.insert(0, 'State CFS', df_b.loc[row_index, 'State CFS'])

        temp_df['Type of Location'] = column_name_check[13]

    except KeyError:
        print("That agency is not listed in the reference")

    return temp_df, specific_df


# The date_edits function processes the date and time information in the dataframes. By priority, through a series of
# if/elif/else statements, the columns are updated with the correct standard “Y/m/d/H/M/S”. If date and time are in
# separate columns, they are combined and updated. If there is a time to dispatch column, the time (in seconds) is
# added to the call time to get the dispatch time.
def date_edits(primary_df):
    temp_df = primary_df.copy()

    # By priority, process call date/time columns
    if 'Call Date/Time' in temp_df.columns:
        temp_df['Call Date/Time'] = pd.to_datetime(temp_df['Call Date/Time']).dt.strftime('%Y-%m-%d %H:%M:%S')
        if 'Call Date' in temp_df.columns:
            temp_df.drop('Call Date', axis=1, inplace=True)
        if 'Call Time' in temp_df.columns:
            temp_df.drop('Call Time', axis=1, inplace=True)
        if 'Time to Dispatch' in temp_df.columns:
            temp_df['Time to Dispatch'] = temp_df['Time to Dispatch'].fillna(0)
            temp_df['Time to Dispatch'] = temp_df['Time to Dispatch'].astype(int)
            temp_df['Dispatch Date/Time'] = pd.to_datetime(temp_df['Call Date/Time']) + \
                                            pd.to_timedelta(temp_df['Time to Dispatch'], unit='s')
            temp_df.drop('Time to Dispatch', axis=1, inplace=True)

    elif 'Call Date' in temp_df.columns and 'Call Time' in temp_df.columns:
        temp_df['Call Date'] = pd.to_datetime(temp_df['Call Date']).dt.date
        temp_df['Call Date/Time'] = temp_df['Call Date'].astype(str) + ' ' + temp_df['Call Time'].astype(str)
        temp_df['Call Date/Time'] = pd.to_datetime(temp_df['Call Date/Time']).dt.strftime('%Y-%m-%d %H:%M:%S')
        temp_df.drop('Call Date', axis=1, inplace=True)
        temp_df.drop('Call Time', axis=1, inplace=True)
    else:
        print("No Call Date/Time information available")

    # By priority process dispatch date/time columns
    if 'Dispatch Date/Time' in temp_df.columns:
        temp_df['Dispatch Date/Time'] = pd.to_datetime(temp_df['Dispatch Date/Time']).dt.strftime('%Y-%m-%d %H:%M:%S')
        if 'Dispatch Date' in temp_df.columns:
            temp_df.drop('Dispatch Date', axis=1, inplace=True)
        if 'Dispatch Time' in temp_df.columns:
            temp_df.drop('Dispatch Time', axis=1, inplace=True)
    elif 'Dispatch Date' in temp_df.columns and 'Dispatch Time' in temp_df.columns:
        temp_df['Dispatch Date'] = pd.to_datetime(temp_df['Dispatch Date']).dt.date
        temp_df['Dispatch Date/Time'] = temp_df['Dispatch Date'].astype(str) + ' ' + \
                                        temp_df['Dispatch Time'].astype(str)
        temp_df['Dispatch Date/Time'] = pd.to_datetime(temp_df['Dispatch Date/Time']).dt.strftime('%Y-%m-%d %H:%M:%S')
        temp_df.drop('Dispatch Date', axis=1, inplace=True)
        temp_df.drop('Dispatch Time', axis=1, inplace=True)

    else:
        print("No Dispatch Date/Time information available")

    return temp_df


# The auid_addition function inserts a new column into the dataframes and fills in the unique identification number per
# agency (the AUID is a combination of the agency name and the index number).
def auid_addition(primary_df, secondary_df, agency):
    temp1_df = primary_df.copy()
    temp2_df = secondary_df.copy()

    # Create a new column with the file name for the agency at the leftmost portion of the dataframe
    temp1_df.insert(0, 'Agency', agency)
    temp1_df['Agency'] = temp1_df['Agency'].replace('.csv', '', regex=True)

    if 'Agency' in temp2_df:
        temp2_df.insert(0, 'Agency_CFS', agency)
        temp2_df['Agency_CFS'] = temp2_df['Agency_CFS'].replace('.csv', '', regex=True)
    else:
        temp2_df.insert(0, 'Agency', agency)
        temp2_df['Agency'] = temp2_df['Agency'].replace('.csv', '', regex=True)

    # Remove any underscores from the column headers
    temp1_df = temp1_df.rename(columns=lambda name: name.replace('_', ' '))
    temp2_df = temp2_df.rename(columns=lambda name: name.replace('_', ' '))

    # Assign the Agency Unique ID (AUID)
    tindex = temp1_df.index.astype(str)
    auid = f"{agency}-" + tindex
    temp1_df.insert(0, 'auid', auid)

    tindex = temp2_df.index.astype(str)
    auid = f"{agency}-" + tindex
    temp2_df.insert(0, 'auid', auid)

    return temp1_df, temp2_df


# The call_type_edit function cleans up the call type column to remove special characters.
def call_type_edit(string):
    if not type(string) == str:
        new_string = str(string)
    else:
        new_string = string
    clean_calltype = re.sub(r'^(=+|-+)', '', new_string)

    return clean_calltype


# Call Type Editing
# This section takes the output from the CFS module (001_Call_Types.csv), which has been modified by the user, to
# replace specific call types for agencies on an agency specific basis.

# The update_call_types function creates a dictionary with the new call types. If the new call type column is empty in
# the spreadsheet the original call type is kept.
def update_call_types(df):
    name_dicts = {}

    for _, row in df.iterrows():
        name = row['agency']
        type_val = row['call type']
        new_type_val = row['new call type']

        if pd.isna(new_type_val):
            new_type_val = type_val

        if name in name_dicts:
            name_dicts[name][type_val] = new_type_val
        else:
            name_dicts[name] = {type_val: new_type_val}

    return name_dicts


# The update_dataframe function updates the final archive spreadsheet, converted into a dataframe, with the
# new call types.
def update_dataframe(df, name_dicts):
    for _, row in df.iterrows():
        name = row['agency']
        type_val = row['call type']

        if name in name_dicts and type_val in name_dicts[name]:
            df.at[_, 'call type'] = name_dicts[name][type_val]

    return df


# The call_types function creates a window to get the file (the updated excel with the new call types) and another
# window to get the output directory (using the output_file_directory function). The output is an updated csv file
# with the new call types.
def call_types():
    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', None)
    pd.set_option('display.max_colwidth', None)

    # Ask the user for the file that has the updated call types
    root = tk.Tk()
    root.withdraw()
    filename = askopenfilename()
    root.destroy()

    # Ask the user where they want to save the updated file
    # opath = "C:/Users/chris/Desktop/School Assignments/Summer/TEST OUTCOME"  # Quick Testing Code Only
    opath = output_file_directory()

    final = pd.read_csv(f"{opath}/00_Final_Archival.csv")

    df = pd.read_csv(filename)
    df = df.drop('uid', axis=1)
    # print(df.head(100))
    agency_dicts = update_call_types(df)
    # print(agency_dicts)
    # for name, types in agency_dicts.items():
    #     type_str = ", ".join(f"{t}: {nt}" for t, nt in types.items())
    #     print(f"{name} - {type_str}")

    df = update_dataframe(final, agency_dicts)
    # print(df.head(100))
    df.to_csv(f"{opath}/001_Updated_Call_Types.csv")

    quit()


# Takes the user input to run calls_for_service, with or without the api option, or call_types
def on_choice(choice, root, c1_value):
    if choice == "1. Run CFS":
        if c1_value.get():
            api_option = True
            local_option = True
            root.destroy()
            calls_for_service(api_option, local_option)
        else:
            api_option = False
            local_option = True
            root.destroy()
            calls_for_service(api_option, local_option)
    elif choice == "2. Run CFS - API Only":
        api_option = True
        local_option = False
        root.destroy()
        calls_for_service(api_option, local_option)
    elif choice == "3. Rename Call Types":
        root.destroy()
        call_types()
    elif choice == "4. Close":
        root.destroy()
        quit()


# Presents the user with a window to select the api option (checked for True and unchecked for False) and
# the option to run calls_for_service or call_types
def main():
    root = tk.Tk()
    root.title("Select an Option")
    root.geometry('300x200')

    frame = tk.Frame(root, padx=5, pady=5)
    frame.pack()

    options = ["1. Run CFS", "2. Run CFS - API Only", "3. Rename Call Types", "4. Close"]

    for choice in options:
        tk.Button(frame, text=choice, command=lambda pick=choice: on_choice(pick, root,
                                                                            c1_value)).pack(pady=5)

    c1_value = tk.IntVar()
    tk.Checkbutton(frame, text="API Option", variable=c1_value).pack(pady=5)

    root.mainloop()
    # calls_for_service(api_option)


if __name__ == "__main__":
    main()
