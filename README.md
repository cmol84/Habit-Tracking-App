# Habit-Tracking-App

## About the app

This version of the habit tracking app is built on the concept that a habit will contain a couple
of  
tasks to do, that when completed, will accrue up to a streak and a successful completion of the  
habit for its given period.

The app allows users to manage existing habits and tasks, create new ones and also delete unwanted  
ones, all through an interactive and intuitive CLI program.

## Installation

Requirements: Make sure you have Python 3.10+ installed on your computer. You can download the  
latest version of Python [here](https://www.python.org/downloads/).

### Required Packages:

```click``` version 8+ (installable via ```pip install click```)    
```tabulate``` version 0.9 (installable via ```pip install tabulate```)

### Required Package to run the tests:

pytest = ">=7.4"

### How To:

## Usage and Main Functionalities

To get an overview of all options available to you, run the following command in the root   
directory of the project: ```pipenv run main```. Then, to execute a specific action, as   
described in the list, execute ```pipenv run main``` + the command you want to run   
```create-habit```, so your command should end up looking like ```pipenv run main   
create-habit```.

To abort any command at any point in the process, just enter ```control + c```.

### Main functionality in detail

1. Habits 
    1. Create a new habit    
       You are able to create your own habits. To do so, you are prompted for a habit name,  
       periodicity (Daily, Weekly, Monthly) and a list of tasks to be used as a template.
    2. List all habits    
       With this functionality you are enabled to see all the currently active habits, with their  
       periodicity and current streak counter.
    3. Delete a habit    
       To delete a habit, you will first get a full list of habits to select from, and then you
       can  
       input the ID of the habit you want to delete. After confirmation the Habit and all its  
       contained tasks will be deleted.
    4. Mark a habit as completed    
       To track your progress, you need to mark your tasks as completed when done.
       When all tasks are done, the streak counter is increased by 1.    
       To mark your progress, you will first get a full list of all habits with their
       corresponding tasks, including the checkmark if already completed, and you only need to
       select the tasks  
       you want to mark as complete.  
       You can select a single task or a list of tasks, they will be updated accordingly.   
       You can mark a task as completed any time.    	
       If you save the progress multiple times per day it is only counted as a one-day-streak.
       Failing to complete all tasks for a day will result in a reset of the streak back to 0  
       and the data initial data saved for reporting.
2. Tasks  
   A snapshot of the tasks will be triggered and saved in the reports table as soon as either all
   tasks are marked as completed or tasks become overdue.
   On both occasions the current task list is deleted and the new tasks for the period is generated.
3. Reports  
   When running the ```analyse-data``` command, you will first get a list of possible reports that
   can be extended at any point.
    1. Your current streak overview.  
       Shows you a list of all your habits and their respective current streaks.
       Displays all weekly and all daily habits.
    2. Your habits with the same periodicity  
       Shows you a list of all your habits having the same periodicity.
    3. Your longest streak per habit  
       You can also find out what your best / longest streak for a specific habit is.  
       Just type in the name of the habit to find out.
    4. Longest run streak of all defined habits  
       Tells you what your longest daily and longest weekly streak are among all your habits.
    5. Shortest run streak of all defined habits
       Tells you what your shortest streak is among all your habits.