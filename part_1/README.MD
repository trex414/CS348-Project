# Food Tracker Application

## Overview
A Django-based food tracking application that allows users to manage their daily meals, track nutritional information, and generate reports. The application implements both ORM and prepared statements for database operations, with proper transaction management and isolation levels.

---

## Features

### **Food Tracker Main Page**
- Requirement 1 completed with:
  - Create, Edit, Delete, View.

### **Day Planner Page**
- Requirement 2 completed with:
  - Dynamic list of meals.
  - Filtering for the list and table.
  - Visualizing the data.

---

## Database Access Methods

### **ORM Usage (70% of Database Operations)**
- User Authentication and Session Management.
- Meal Tracking and Nutrition Analysis.
- Reporting and Analytics.

### **Prepared Statements (30% of Database Operations)**
- Advanced Query Execution.
- Export Reports.
- Performance Optimization.

---

## Isolation Levels
- **Read Committed:**  
  - Used on the Day Planner Page.

- **Repeatable Read:**  
  - Used to move a plan entry or modify a food entry.

- **Serializable:**  
  - Used to create food entries and update user information.

---

## Lessons Learned

This was the first time I ever had to create a website and use Django. I am so happy I did; Django was Instead, and I have thoroughly enjoyed this class. Another reason is because I want to create more websites in the future. 

The main concepts I had to advance my knowledge in during this project were when to use ORM and prepared statements, as well as how to create an authentication system. I created a very basic authentication system, and on the online server, it does not work as a login but more as a way for a user to save data under a name. However, understanding how to create one and where to save the data was complex and will help me in my future creations. 

When going through Django, I learned a lot more about ORM than I thought I would (as it is the default for Django). I also learned how to work with an HTML file/page. It was new to me, and being able to change the style of things took a lot of time to figure out, but it was cool once I got it.

Finally, if I were to start over again, I would have created a financial web page. The main reason is that after this school year, I am going to build one, but it would have been nice to start a draft now. Another thing I would have done differently is how to learn to code in HTML and Django; I mostly threw myself into it, and because of that, wasted a lot of time. Instead, I could have watched more tutorials and been able to do it better and quicker. 

Overall, I am very proud of my project and am going to put it on my resume. I hope I will be able to look at it in a couple of years and think of it as very basic compared to what my talents can do then.