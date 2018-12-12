# Marvel Heros
### Use the Marvel API, and scrape and crawl superhero data into a Database

## Description
This application uses the Marvel API to gather information on 100 random superheros (based on whose page was updated last).
Then depending on which command you pick, will display a different type of graph to visualize information about the heros.

## Getting Started
Run final.py
```
python3 final.py
```
*If you deleted the cache file, wait a few seconds and let the program populate the DB*

Next, you will be prompted by a user input. 

Commands: 
**list** 
Will list a set of super heros and their ID number.       

**stats (id num, from list)**
Will open a plot.ly page of a pie chart to visualize data for the superhero.

**top (Series, Comics, Events, or Stories)**
Will open a plot.ly page of a bar chart to show the Top 10 superheros and the number of (param).

**map**
Will display the a map of the world and display the origin locations of selective heros. 

## Testing
Run final_test.py
```
python3 final_test.py
```
*Make sure you comment out the first part of the final.py where I delete the database tables.*
