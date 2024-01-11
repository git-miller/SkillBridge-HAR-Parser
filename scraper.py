import json
import csv

# Until I can find a better way to manage this, the HAR file is pulled
# by opening the skillsbridge site in Firefox:
# https://skillbridge.osd.mil/locations.htm
# opening the dev tools (F12) then click the network tab. 
# It should be cleared, but if not click the trash can icon
# Click "Search" with blank text boxes on the webpage
# You should see a file show as XML in the type column
# it should be fairly large (MBs)
# Right click anywhere on that line and "Save All as HAR"
# Save that to the same directory as this script

# Ensure this name matches your HAR file in the directory
HAR_FILENAME = 'newdata.har'
# Can be anything
CSV_FILENAME = 'newdata4.csv'

# Loads some of the info as JSON
with open(HAR_FILENAME, 'rb') as file:
    data = json.load(file)

# Some of the data doesn't convert directly to JSON
# but this gets to the bulk of the data required.
responseData = data["log"]["entries"][0]["response"]["content"]["text"]

# Searching for the first sign of good data
start = responseData.find('''{"COST":''')
# This looks for the final "}, characters,
# but backwards due to the reverse -1 string ,}""
end = len(responseData) - 1 - responseData[::-1].find(''',}"''')

# Slices up only the text we need for the job listings
cleanedData = responseData[start:end]

# Removing extra characters that aren't needed
cleanedData = cleanedData.replace("\\", "")

# Need to change characters splitting information to retain
# some information in descriptions without breaking it up
cleanedData = cleanedData.replace("\",\"", "\"||\"")

# Discusting way to remove some bad encoding data that
# I can't figure out how to decode properly
# Still have a few things to figure out
# as a couple entries have their processing shifted due
# to bad characters that aren't properly removed below
while cleanedData.find('\00') != -1:
    first = cleanedData.find('\00') - 4
    second = cleanedData.find("octet-stream") + 12
    cleanedData = cleanedData[:first] + cleanedData[second:]

# Split jobs, making a list for each one
preSplit = cleanedData.replace(r"},{", r"}},{{")
jobList = preSplit.split(r"},{")

# Fields
fields = []
for title in jobList[0][1:-1].split("||"):
    fields.append(title.split(":")[0][1:-1])
with open(CSV_FILENAME, 'a', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(fields)


# Fill in CSV
for job in jobList:
    fields = []
    for section in job[1:-1].split("||"):
        fields.append(section.split(":")[1][1:-1])
    
    
    with open(CSV_FILENAME, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(fields)
