# Project-A.N.T.S

Introduction
------------

Project A.N.T.S is a simple web application that demonstrates project management. It aims to create efficient project schedules, focusing on minimising completion time and manpower for any given project. This is the user manual to help one effectively utilise A.N.T.S for their project management task.

Features
--------

- Activity On Arrow (AOA): A visual representation of project activities and their dependencies.
- Activity On Node (AON): A visual representation of project activities and their dependencies.
- Duration VS Resources Graph: A plot to show the cumulative resources used vs cumulative duration.
- Gantt Chart: A clear, visual representation of the project timeline and task dependencies, making it easy to understand the project flow.
- Resource Levelling Gantt Chart: Allows users to adjust activities which can lead to a decrease in the maximum amount of resources utilised, directly decreasing the total expenditure.
- S-Curve: A graph that shows the cumulative costs and cash inflows over time. 
- Critical Path: The minimal completion time of the project or the longest path through the network that determines the duration of the project.
- Crash Budget: A method to speed up the project by employing additional resources.

Installation 
-------------

To install this project, follow these steps:

1. Download the zip file "myflaskapp" and unzip it.
2. Search the Start menu for Command Prompt and run Command Prompt.
3. Navigate to the project directory by typing "cd C:\myflaskapp"(if the myflaskapp folder is in the C drive on windows) or "cd Desktop/myflaskapp"(if the my flask app is in Desktop for Mac) and press enter, followed by "python app.py" and pressing enter once more(input the command based on where you have placed the file, the commands given here are examples).
4. Next, while long-pressing the "ctrl" key(for windows) , click on the link generated or copy the link and paste in into your web browser(for Mac). This will lead you to the loading page of Project A.N.T.S

Please take note of the libraries and the versions required(install if missing any):
blinker==1.8.2
certifi==2024.7.4
charset-normalizer==3.3.2
click==8.1.7
colorama==0.4.6
flask==3.0.3
idna==3.7
importlib-metadata==8.2.0
itsdangerous==2.2.0
jinja2==3.1.4
MarkupSafe==2.1.5
numpy==1.24.4
requests==2.32.3
urllib3==2.2.2
werkzeug==3.0.3
zipp==3.19.2

In the command line input: pip install library_name==version_number to install the missing library. If an alternate version of the library already exists, please uninstall it using the following command pip uninstall library_name and then use: pip install library_name==version_number to install it again.

Usage
------
To run the application, follow these steps:

1. First, click on "Choose File" to upload your dataset.
2. Once it has been successfully uploaded, click on the "Upload" button.
3. Ensure your data is accurate by cross referencing with the table under "Uploaded Activity Details"(Please follow the steps on how to format the data present in the "ANTS Excel instructions.pdf" document). 
4. Finally, based on your own specific requirements, click on which graphs and charts you would like to explore by clicking on their respective buttons. If you would like to save the graphs, you may right click on the graphs to save them.
5. If you would like to generate more than one graph, click on the "Go Back" button at the bottom of the page to return to "Uploaded Activity Details". Note that whenever you see a "Start Over" button, it will lead you back to the first page where you would have to upload your dataset again to run the application. 
6. There are three features which are interactive in nature; namely "Resource Levelling Gantt Chart", "S-Curve" and "Crash Budget". More specific details on how to run the application for these three features would be specified below. 
7. If at any point the webpage is not responding or if you feel like its giving the wrong results, please close it and run steps 3 and 4 from Installation again to generate a new link(the session might have timed out due to inactivity).

Do check out "User Manual_V2.pdf" which is the manual we provide for the live demonstration of our software if you want to.

Resource Levelling Gantt Chart
-------------------------------
To generate the Resource Levelling Gantt Chart, follow these steps:

1. Click on "Generate Resource Levelling Gantt Chart". 
2.Critical Path activities are activities generated in the last row, while non-critical path activities are the activities on the other rows.
3. You can adjust non-critical Path activity by inputting any non-critical path activity as well as their new start time (days) before pressing the "Adjust Activity" to see how your decision affects the Resource Levelling Gantt Chart.
4. Based on the conditions placed by the uploaded dataset, such as the predecessors of activities, whether the activity is on the critical path or not, as well as how much free float an activity has, the system will prompt you with an error message to identify if and why your adjusted activity is infeasible, if necessary. 

S-Curve
--------
To generate the S-Curve, follow these steps:

1. Click on "Generate S-Curve". 
2. Fill in the table with how much cash injections will be added, as well as the time that it will occur. If needed, click on "Add Another Cash Injection", to add more cash injections at their specific timings.
3. Once done, click on "Generate S-Curve". 
4. If you click on "Go Back" after the S-Curve has been generated, it will lead you back to the "Uploaded Activity Details" page. If you click on "Generate S-Curve" again, the system automatically remembers the previous data under "Existing Cash Injections". If you try to click on the "Generate S-Curve" button, the system will prompt you to "Please fill out this field" to add new cash injections. However, if you have none, you may simply input "0" for both fields, before generating the S-Curve again. 

Crash Budget
-------------
To generate the Crash Budget, follow these steps:

1. Click on "Adjust Cash Budget".
2. Input the total cash budget you have to perform crashing for the activities. 
3. Click on "Adjust Cash Budget".
4. The system remembers this adjusted Gantt Chart for Crashing version. Hence, if you would like to change your total budget with respect to the original data, you would have to click on "Start Over" to restart the process from uploading your dataset into the application. 

We hope that you have a pleasant experience while using our beloved software!
