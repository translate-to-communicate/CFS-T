June 10
 - Added 2 functions "call" and "col_edit" which reduces the overall space of the "main" function
 - Removed excess comments
 - GUI code commented out but left in - working on making a singular window to address all prompts
 - Fixed an issue where if the user did not give the agency an updated name the new file extension was added </br> on top of the old file extension (e.g., .xlsx became .xlsx.csv)

June 13
- Updated the col_edit function to identify "Mandatory" columns based on the global 'final_columns' list
- Added a final message window that will display the first 5 rows of the final document to include the column headers

June 15
- Fixed an error that caused the col_edit loop to end if the user chose to keep a column ('break' used instead of 'pass')
- Added in the API for St. Pete, FL. Successfully pulls data; formatting to follow in future updates.
- Reset the testing branch to fix security issues
- Modified the main file name
- Added additional mandatory columns to the final_columns list: disposition, case, map, subdivision, <br> latitude, longitude, lat, lon.

June 16
- Restructured the file directory
- Added setup.py, __init__.py
- Fixed an error where no file directory chosen would result in the C:/ being chosen by default
- Added run.py to call the primary function to occur
- Removed the .idea folder from the repository

June 20
- Added two functions (input and output directory calls) to reduce code inside the main function. Allows for quicker<br> swapping between test code and production code.
- Added a loop to the col_edit function to skip empty data and provide a useful example for the user
- Created a function to display the percentage of a column that is empty (not currently used)
- Adjusted col_edit to add in a statement showing the percentage of the column that is empty (not currently used)
- Adjusted col_edit to auto-remove columns that contain 'http' or 'https'

June 21
- Function for API calls has been added. A variable in the 'main' function, 'api_option', is set to False by default<br> to skip the call.

June 26
- Created function to generate the final columns from a text file. Removes the global list and allows updating via <br> a .txt file.
- Created a location function to manage the location data

June 27
- Updated location function to merge columns for better processing
- Geocoding struggles with Nominatim

June 28
- Added a dictionary to allow for content replacement during location processing. Nominatim struggled due to an <br> inability to locate the address without the proper city (VAB does not exist - it is Virginia Beach).
- A large issue is the request limit that is placed on the geocoding by the Nominatim Usage Policy. The volume <br> of requests ultimately results in an error "geopy.exc.GeocoderServiceError: Non-successful status code 502".

June 29
- Moved the API and location processing to separate files
- Updated requirements to include geopy
- Updated location script to process various location data by priority / ease of consumption. A lat/long is the <br> desired outcome. However, not all location information currently produces a lat/long. If the agency <br> only provides a block address then the system will not be able to identify its location (even with a zip).

June 30
- Cleaned up the main file
- The api_option variable has been moved to the APIs file to allow a singular point of editing for all API needs

July 3
- Created a new function in LocationProcessing to take the location data provided and convert to the correct <br> lat/long format. Data provided is typically written as "POINT (longitude, latitude)" and needs to be "latitude, longitude"
- Added 3 lines to the main function to assign Agency UIDs based on the Agency information and the index number

July 4
- Small updates to columns text and to the AUID

July 5
- Added Seattle, WA API
- Fixed issue with AUID getting deleted

July 6
- Modified the dataframe (df) to keep columns that have words that match the final columns list (the intersection <br> does only full strings and not individual words)
- Fixed API integration. The separate API script returned a list which caused the list to become a list of lists <br> which the system could not concat
- Modified the API calls to include Timeout error handling.
- Modified the dictionary and created a separate agency specific reference that will be used in future work**
- Updated setup to include additional requirements
- Created a dataframe that will be used for agency specific references - might work better than the dictionary. The <br> user will only need to update the fields as they pertain to the new agencies.
- Created a dictionary that is generated based on an external xlsx file.
- Functions created that: create a dictionary based on an external xlsx file, remove empty values from the <br> dictionary, and rename the headers of the dataframe based on that dictionary.

July 7
- Using a dataframe to properly assign the correct column headers to the agency files based on an external spreadsheet.
- Fixed the "replace_column_name" function to catch KeyError
- Removed unnecessary comments
- Added a dictionary and list that pulls the agency name based on the file. Avoids asking the user questions for <br> agency name unless the name doesn't appear in the dictionary.
- Currently, only 4 key steps are required before a user can run the program.
  - Place all files that are to be used in the same directory
  - Properly name the file based on the file naming convention
  - Update the external spreadsheet to align with the common data standard designed for this system
  - If using an API, update the API file to account for specific API requirements (usr/pass/token etc.)

July 10
- Fixed an issue that was causing concat issues
- Added an AUID function to add the agency column and AUID column
- Created a date_edits function to handle the varied date time formats that are ingested
- Reworked the initial processing of columns from each agency - all agencies will have 12 total columns before the <br> agency and AUID columns are added.
  - Call Date and Call Time are processed, merged, and then dropped
  - Dispatch Date and Dispatch Time are processed, merged, and then dropped
  - Latitude and Longitude are processed, merged, and dropped
  - Agency, Incident Number, Call Type, Call Date/Time, Dispatch Date/Time, Block Address, and Location (Lat/Long) <br> are the columns that will remain at the end of processing. The agency specific columns are separated and stored in a separate file.
- Fixed an issue with some agencies having a double comma in the lat/long

July 11
- Separated the "replace_column_names", "date_edits", and "auid_addition" functions to a separate module
- Modified the date_edits function to delete the "dispatch date", "dispatch time", "call date", "call time" <br> columns after processing
- Modified the LocationProcessing module to delete any latitude and longitude columns after processing
- Current final columns are:
  - UID, AUID, Agency, Incident Number, Call Type, Block Address, Location(Lat/Long), Call Date/Time, Dispatch Date/Time

July 12
- Updated the location service to account for the APIs bringing in extra content to the location (lat/long) column
- Addressed some minor errors in variable names
- Removed data from dictionary.txt as it will likely be phased out

July 13
- Updated the LocationProcessing module to address the varied information picked up via the Location (Lat/Long) column
- Added a function to Col_Edits that cleans the 'Call Type' column at the end - the issue was an agency used <br> "=--" or combinations of those to prepend the call type. This function removes those while preserving any that appear within the remaining string.
- Modified the call_type_edit function to convert data to string if not in that format prior to operation
- Added the Fort Lauderdale API connection

July 14
- Updated project to include "Agency Reference.xlsx" in the app folder
- Updated the reference sheet to include city/state information if not present (user requirement)
- Updated LocationProcessing module to support the new "City CFS" and "State CFS" columns - merges "block address" <br> and "city" to send to geoprocessing function
- Added LAPD API
- Removed excess/unused code
- Added an if/else statement to catch empty dataframes resulting from an empty API pull

July 17
- Updated the city dictionary to include city abbreviations currently occurring - geocoding modified to support <br> new column names

July 18
- Modified the API module to utilize a function for the socrata api calls (reduced lines required)

July 19
- Added a json api function to handle the Opendatasoft Explore API v2 (currently only used for Jersey City, NJ).

July 27
- Added a statement in the "date_edits" function that will pull time (in seconds) that is provided by the agency <br> from the time the call was picked up to the time a unit was dispatched. This date/time is recorded as Dispatch Date/Time. 
- Updated LocationProcessing to include a percentage tracker for location data provided by the agencies to <br> determine if the number of empty cells is above 50 percent to take the address information and geoprocess it instead
- Added a field to identify if the type of location data:
  - Centroid - identifies that a lat/long provided represents the center of a designated area (e.g., Hollywood, Los Angeles will return a singluar point)
  - Block - identifies that a lat/long provided represents an address block (e.g., 1400 W IRIS DR, GILBERT, AZ is not a specific house but represents all houses in the 1400-1499 range)
  - No Value - no information is provided
- Fixed an issue with the name check prior to starting the processing
- Added a condition to skip a file if no agency name is found after the user is prompted for an updated agency name <br> (three attempts before skip)
- Created a "failed_agency" list to collect the failed filenames to allow for further analysis
  - Current iteration has the list display in the final message box
  - Next iteration will save a log file

July 28
- Added the location code to identify how the location information is provided
  - 1 - directly from the agency
  - 2 - separate lat/lon joined from agency
  - 3 - block address conversion
  - 4 - no data
- Added the call type output file for unique call types
  - Current iteration is done at the end across all agencies (i.e., if two agencies have a "Fire Call" then only <br> the first instance of that call type will appear in the list)
  - Next iteration may be reworked to allow for agency specific call types (i.e., if two agencies have a "Fire Call <br> then both agencies will have that appear)

July 29
- Renamed the main function under CFS.py to "calls_for_service" and then created a new main function that will call <br> the "calls_for_service" function
- Modified run.py to prompt the user for a choice of running the main function or the rename_call_types function <br> (the rename_call_types function is not yet implemented)
- Updated two separate filepaths to account for using run.py (added a current directory variable using os)

July 30
- Added CallTypes.py to handle updating the call types
  - Current iteration updates the call type on an agency basis (if Agency 1 and Agency 2 have the same call type, <br> but only agency 1 has a "new call type" then it will be updated not both)
  - Will design a separate process to enable updating regardless of agency if desired
- Updated date/time edits to account for missing information in the "Time to Dispatch" column
  - Places a 0 for all empty cells
  - Converts the column to int data type

August 01
- Removed the "api_yn" function and added a checkbox to the run script to capture if the user wants to run the APIs
  - This may be reversed as the user already needs to update APIs.py to input the usrname/psword/apptoken
- Default option for API use is "False". If the user does not run with run.py, they will need to update the code <br> to ensure the api_option is set to "True"
- Removed the quick testing portions of code

**Transitioned the project to a single file**
- All the CFS translation work is now located in a single file for easy of use.
- The setup.py file will install the required packages and has been updated to ignore a soft warning.
- The README has been updated.
- The Agency Reference has been updated.
- Various minor modifications.

v1.0.1
- Removed the comments from the geocoding portion - system will now send all required geo information to Nominatim
- Updated comments to add more clarity to a few functions

v1.0.2
- Updated the request limit for the SODA API to 1000. Max is 1000 per hour per the SODA API, requests for more need to go through the SODA support team.
- Updated the README to highlight the above change.

v1.0.3
- Removed unnecessary comments and print statements

v1.0.4
- Updated the python script file name to CFS-T.py
- Updated the README to reflect the change