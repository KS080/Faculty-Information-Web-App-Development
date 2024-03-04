

from flask import Flask, render_template, request
web_app = Flask(__name__)
from bs4 import BeautifulSoup
import urllib3
import json
import re

# List to store emails extracted from the website
emails_list = []

# Here in the code below this line I tried to retirve OFFICE Hours data from webiste I was succesful to retirve but wasn't able to convert it to list and add it to json file it was showing error so I didn't added Office Hours info in json and made a webpage where I input name of faculty like "Gerard Awanou" and get email as output


# Function to retrieve emails from the faculty page
def retrieve_emails():
    web_client = urllib3.PoolManager()
    faculty_url = "https://mscs.uic.edu/people/faculty/"
    response = web_client.request('GET', faculty_url)
    soup = BeautifulSoup(response.data.decode('utf-8'), "html5lib")

    email_tags = soup.find_all('span', attrs={'class': '_email'})

    # Extract email addresses from the parsed HTML
    for tag in email_tags:
        anchor_tags = tag.find_all('a')
        for anchor in anchor_tags:
            email = anchor.text
            emails_list.append(email)

    return None

# Execute the email retrieval function
retrieve_emails()

# Clean and strip the extracted emails
cleaned_emails = []
for email in emails_list:
    cleaned_email = email.strip()
    cleaned_emails.append(cleaned_email)

# List to store names extracted from the website
names_list = []

# Function to extract faculty name from their individual profile page
def extract_name(profile_url):
    web_client = urllib3.PoolManager()
    response = web_client.request('GET', profile_url)
    soup = BeautifulSoup(response.data.decode('utf-8'), "html5lib")
    name_tag = soup.find('div', attrs={'class': '_colB'})
    headers = name_tag.find_all('h1')
    name = headers[0].text

    names_list.append(name)

# Function to automate the process of scraping names
def automate_name_scraping():
    web_client = urllib3.PoolManager()
    faculty_url = "https://mscs.uic.edu/people/faculty/"
    response = web_client.request('GET', faculty_url)
    soup = BeautifulSoup(response.data.decode('utf-8'), "html5lib")
    name_tags = soup.find_all('span', attrs={"class": "_name"})

    # Loop through each name tag and extract names
    for tag in name_tags:
        anchor = tag.find_all('a')[0]
        profile_url = anchor['href']
        extract_name(profile_url)
    return None

# Execute name scraping
automate_name_scraping()

# Mapping emails to names
email_name_dict = dict(zip(cleaned_emails, names_list))

# List to store teaching schedules
teaching_schedules = []
final_schedules = []

# Function to get teaching schedule from a profile page
def get_schedule(profile_url):
    web_client = urllib3.PoolManager()
    response = web_client.request('GET', profile_url)
    soup = BeautifulSoup(response.data.decode('utf-8'), "html5lib")

    schedule_tags = soup.find_all('div', attrs={'class': 'u-rich-text'})

    # Extract teaching schedules
    for tag in schedule_tags:
        lists = tag.find_all("ul")
        for list_item in lists:

            schedule_text = list_item.text
            split_schedule = schedule_text.split()
            teaching_schedules.append(split_schedule)

            # Process each schedule to extract time information
            for schedule in teaching_schedules:
                time_list = []
                for item in schedule:
                    if re.match(
                            r'[0-9]{2}\:[0-9]{2}\:[0-9]{2}\-[0-9]{2}\:[0-9]{2}\:[0-9]{2}',
                            item):
                        time_list.append(item)

        final_schedules.append(time_list)

# Function to automate the process of scraping teaching schedules
def automate_schedule_scraping():
    web_client = urllib3.PoolManager()
    faculty_url = "https://mscs.uic.edu/people/faculty/"
    response = web_client.request('GET', faculty_url)
    soup = BeautifulSoup(response.data.decode('utf-8'), "html5lib")
    name_tags = soup.find_all('span', attrs={"class": "_name"})

    # Loop through each name tag and extract schedules
    for tag in name_tags:
        anchor = tag.find_all('a')[0]
        profile_url = anchor['href']
        get_schedule(profile_url)
    return None

# Execute schedule scraping
automate_schedule_scraping()

# Combine all extracted information into a single dictionary
combined_info = {name: (email, schedule) for name, email, schedule in zip(names_list, cleaned_emails, final_schedules)}

# Write the combined data to a JSON file
with open('combined_data.json', 'w') as data_file:
    json.dump(combined_info, data_file, indent=4)

# Define route for the home page
@web_app.route('/')
def index(): 
    return render_template('index.html')

# Define route to handle form submission
@web_app.route('/', methods=['POST'])
def getvalue():
    entered_email = request.form['email'] 
    display_value = ""

    # Load the combined data and search for the entered email
    with open("combined_data.json") as data_file:
        loaded_json = json.load(data_file)

    for key in loaded_json.keys():
        if ' '.join(key.split()).lower() == entered_email.lower():
            display_value = loaded_json[key][0] 
            break

    return render_template('pass.html', email=display_value)



# Run the Flask app
web_app.run(host='0.0.0.0', port=81)
