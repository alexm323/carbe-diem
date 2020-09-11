# 1. What goal will your website be designed to achieve?

There are many apps that attempt to help people become healthier by means of calorie tracking but many of these once clean websites have been inundated with unecessary spam in the form of advertisements and advertisements thinly veiled as health content. We seek to remedy this by providing a web app for simple food journaling to help people take positive steps towards their health and fitness goals whatever they may be. 

# 2. What kind of users will visit your site? What is the demographic of your users?

Anyone is welcome to help reach their health goals but a major focus is going to be on the calorie tracking (Calories In vs Calories Out also known as CICO) which appeals to people looking to lose weight. There is a large market for this kind of application especially if we expand to users that use specialized diets and want meal plans in an expanded version of the app for special diets, atkins,keto,etc. 

# 3. What data do you plan on using? 

 I am still considering applications but there is contenders including FDC Nutrient Data(from the USDA), Spoonacular, and potentially MyFitnessPal API(pending their application approval). 

# 4. In brief, outline your approach to creating your project:

The primary focus is on a healthy space for the user to store data about their fitness/health goals as well as to keep information regarding their caloric and nutritional intake as well as other factors such as age,weight, TDEE(Total Daily Energy Expenditure) and there can be additional information on how to get body fat percentages and other measurements of physical fitness/health.

The focus will be on displaying the 'stats' from the database for the user. I am going to start simple with a caloric diary and hopefully scale up features over time. The API will serve to acquire the nutritional information for the food that the user is inputting.


## a. What does your database schema look like?
For starters:

__users__ (one user)

id (PK) | fullname |username | password | Age | Height | TDEE | calorie_diary 


__calorie_diary__(one calorie diary to one user)

id(PK) | entry_id(FK) |  entry_date  | entry_time/part(breakfast,lunch,dinner) | user_id(FK)

__entries__(many entries to one calorie diary)

id(PK) | food_id(FK) | calorie_total(for one entry) | water_intake 

__foods__(many foods to one entry)

id(PK) | API_Food_id | name | calories | fat | protein | carbs | sugar | sodium 


One user should have one calorie diary. 
Each diary will track many entries.
Each entry will have many foods
Every food has values including calories,macros,and nutrients. I could also break this down further but not sure how to far to break down the data. 

## b. What kinds of issues might you run into with your API?
I'm having trouble finding a straightforward API to work with and I don't have experiencing masking my API auth key to avoid putting it out into the general public. The API that I choose should have both calories data as well as nutritional data about a specific food to get a breakdown of the macros within it. 

## c. Is there any sensitive information you need to secure?
User password will need to be hashed and secured as well as masking API auth key.
## d. What functionality will your app include?

## e. What will the user flow look like?
User registers on the home page (No functionality without registration)/Logs in

Based off of their inputs they are presented with a TDEE for each day based on their height, weight, and age

On that page they are able to input foods and water intake for the day and then they are shown a graph that shows the comparison between their current caloric intake and their TDEE to show the calories remaining. There can be a few graphs on the page. Weight change overtime, nutrients fulfilled, macro goals, caloric goals. 


## f. What features make your site more than CRUD? Do you have any stretch goals? 
The idea is to assist people track their calories as there is research that shows that tracking calories is the most effective way to stick to weight loss programs. And there are several potential ways to scale up the web app. 

I want to start simple but future updates could include the following:

Tracking exercise
Tracking specific nutrients (think iron intake for anemic people)
Recommending meal plans based off of diet preferences within calorie goals 
Fasting Tracker for people doing intermittent fasting
Basic information about the effectiveness of certain diets and sustainability ( Keto long term)
Recommending exercise based off of body impact level 
Meditation exercises for body and mind combination 