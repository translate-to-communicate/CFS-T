# Calls for Service - Translator (CFS-T)

The Calls for Service - Translator (CFS-T) program is a python script that is aimed at providing a service to extract data from various police agencies through direct connections of their data repositories and/or through locally stored files. The program translates the data, with respect to a data standard designed for this program, and then loads it into a final archive document (.csv) in the directory chosen by the user.

Currently supported local file formats: Excel 2010 files (i.e., .xlsx), .xls, and .csv <br>
API connections: Socrata Open Data API (1000 request limit per hour due to SODA Consumer API policy. See Step 5 of "Before You Begin" for more)<br>
JSON function designed to support JSON requests <br>

## Before You Begin
1. Download the ZIP and extract to your desired location. Keep all files together.
2. Ensure python is installed (minimum version requirement is 3.9.0)
3. Install the required packages using the setup.py file or pip: (Required packages are listed at the end of this document)
   - From within the CFS-T-main folder: python setup.py install
   - python -m pip install "replace with required package" (do not include quotations)
4. If using local files, ensure they are in the correct file format (see above for supported formats). The system will run regardless, however any file formats not supported will be ignored. A message will appear, once the program is done, that shows which documents were not processed.
5. If using the Socrata Open Data API or any JSON requests you must modify CFS-T.py:
   - Lines 37-39: enter the username, password, and apptoken inside the quotation marks (Socrata)
   - Add any additional agency connections. Copy the code snippet below or follow the examples starting on line 44 for all Socrata connections. Replace the first three variables (Agency Name, URL, and Client-Code) for the specific agency. Do not remove the quotation marks. 
     - api_li, api_liz = socrata_api("Agency Name", "URL", "Client-Code", myapptoken, usrname,
                                  psword, opath, api_agency_ref, api_li, api_liz)
     - JSON requests require the user to enter the URL as defined by the agencies data repository. An example is provided on line 72.
   - Line 98: Update the snippet "limit=1000" to change the limit of records to be pulled from the data repository based on your requirements. ***Note that SODA Consumer API has a max request limit of 1000 per hour with an app token. To gain more requests you will need to contact the SODA support team at: https://support.socrata.com/hc/en-us/requests/new***  
6. Update "Agency Reference.xlsx" with the agency column headers (follow the example agencies provided). ***Case Sensitive***
7. Update "Dictionary.txt" if city abbreviations are used. Follow the example cities given inside Dictionary.txt.

## How To Run
1. Run CFS-T.py through a command terminal, powershell window, or command prompt
   - From the inside the CFS directory - "python CFS-T.py"
   - From anywhere else, you must specify the full directory. Example - python "C:\Users\johndoe\Desktop\CFS-T-main\CFS-T-main\CFS\CFS-T.py"
2. A window will appear with 4 buttons and a checkbox
   - Option 1 - "**Run CFS**". This will run the program with local files. 
     - The checkbox is to select whether you want to run the system with or without API/JSON connections.
     - Default is unchecked - no API option.
   - Option 2 - "**Run CFS - API Only**". This will only run the API/JSON connections.
   - Option 3 - "**Rename Call Types**". This will take the updated call type file (originally created as "001_Unique_Call_Types.csv") and update the file ("00_Final_Archival.csv") creating a new file called "001_Updated_Call_Types".
     - You need to run CFS at least once (with or without the API option) to generate "001_Unique_Call_Types.csv"
     - The user can rename "001_Unique_Call_Types.csv" as long as the file remains a .csv. You will be prompted to select the updated file.
   - Option 4 - Close. Ends the program.
3. Once you've made a selection, you will be prompted to select the ***OUTPUT*** file directory. This is where all the files will be saved to.
4. Unless you selected the API Only option, you will be prompted to select the ***INPUT*** file directory. This is where your local files are currently stored.
5. A final window will appear once the program has finished. This will show the first 5 rows of data in the final document, as well as any files that were not processed.

## The CFS Extract, Translate, Load (ETL) Process
![ETL Process](CFS%20-%20ETL.gif)


## Extract
The extraction process is designed to pull all available data from an agency and store it in a pandas dataframe. The program can extract data locally from Excel 2010 files (i.e., .xlsx), as well as .xls and .csv formats, and it can extract from agency databases through the Socrata Open Data API or JSON requests. 
For each agency, regardless of the method of extraction, the first action is to save an original copy of the data to ensure data preservation and to allow comparison to the processed data at a later time.

The second action is the translation process.

## Translate
The translation process converts the data into a standard format to allow for future analysis. The translation process consists of multiple steps:

1. Rename the column headers to comply with the data standard. For example, agency A has the column header “Type of Event”. The user, having updated the agency reference sheet, identified this to be “Call Type”. The program will then update the header to the correct name. Additional city and state information is added if not provided by the agency – this is used for the geocoding portion later.
2. Separate the data, based on the data standard, into two distinct dataframes – one for the standard and one for agency specific information.
3. Date and time information is updated to reflect the data standard. If there is no dispatch date/time but there is a column to reflect the time (in seconds) it took to dispatch a unit, that time is added to the call time and reflected under “Dispatch Date/Time”.
4. Agency unique identification number (AUID) is added to the data.
5. Location data is processed, coded, and assigned a type based on how the data is retrieved. Lat/Long information is generated through cleaning and organizing the Lat/Long data provided or by combining the address/city/state information and processing through the Nominatim service. If there are city acronyms, a dictionary text file can be updated to annotate that and to update the data with the long form name (e.g., VAB translates to Virgina Beach).
   - Code 1 - Information pulled directly from agency data.
   - Code 2 – Latitude and longitude information pulled from two separate columns and combined into one. Information is still pulled directly from the agency data. 
   - Code 3 – Address information is converted, via the Nominatim service, into latitude and longitude coordinates.
   - Code 4 – No location information is provided.
   - Types are assigned by the user in the agency reference sheet. Future updates will add a feature to automatically assign the type based on location data processed.
      - Block - A block address is given
      - Centroid – A center point within an area that all records in that region will be assigned to. (An example would be the location information is an area, like “Hollywood”, and all reports for that area would be a center point of that area.)
      - No Value – No information available

After each agency has been processed, the dataframes are combined into a singular dataframe and a unique identification number (UID) is assigned to each row. Lastly, all unique call types from each agency are extracted and translated to a separate dataframe.

## Load
There are three main files that are loaded for each agency: an original copy of the data, an agency specific copy housing only the information not required by the data standard, and the final copy that meets the data standard. These files are loaded into the output file directory chosen at the beginning of the program. In addition, there are two more files loaded: the archive document which contains the combined data of all the agencies (in the data standard) and the unique call types file, “001_Update_Call_Types.csv”. The update call types file is used by the user to redefine call types, by agency, and have the final document updated. Users must run the CFS program at least once to generate the update file.

## The Common Data Standard
A common data standard, built using an agency reference sheet, was required in order to extract data from a wide range of agencies and the different methods the data is stored. This data standard relies on the user updating the reference sheet with the corresponding column headings based on the agency – examples are given to aid in the process. The required column headings are: Agency, Incident Number, Call Type, Call Date/Time, Call Date, Call Time, Merged Address, Dispatch Date/Time, Dispatch Date, Dispatch Time, Time to Dispatch, Block Address, Latitude, Longitude, Location (Lat/Long), Type of Location, City, State, City CFS, State CFS.

Each column heading requires a value, even if no value is represented in the agency data. In the event no value is present in the agency data, the user must enter “No Value” (without the quotations) for that column.

The final document will have the following columns: UID, AUID, Agency, Incident Number, Call Date/Time, Dispatch Date/Time, Call Type, Location (Lat/Long), Type of Location, and Location Code.

## Python Package Requirements
The table below highlights the python packages required for the system to function. *Higher versions of any package is ok.* <br>

| Package  | Version |                                                                                                  Description |
|----------|:-------:|-------------------------------------------------------------------------------------------------------------:|
| pandas   |  2.0.2  |                                                           an open source data analysis and manipulation tool |
| tabulate |  0.9.0  |                                                                          pretty-print tabular data in Python |
| numpy    | 1.24.3  |                                                       fundamental package for scientific computing in Python |
| sodapy   |  2.2.0  |                                                                a python client for the Socrata Open Data API |
| geopy    |  2.3.0  |                                                   a Python client for several popular geocoding web services |
| requests | 2.31.0  |                                                                         allows you to send HTTP/1.1 requests |
| openpyxl |  3.1.2  |                                          a Python library to read/write Excel 2010 xlsx/xlsm/xltx/xltm files |
| xlrd     |  2.0.1  |         a library for reading data and formatting information from Excel files in the historical .xls format |


