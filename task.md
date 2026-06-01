# **Mini Hackathon Project: Campus Data-Based Program Prototype**

## **Gemini Code Assist**

[https://developers.google.com/gemini-code-assist/docs/set-up-gemini?hl=ko](https://developers.google.com/gemini-code-assist/docs/set-up-gemini?hl=ko)  
VSCode extension:  
[https://marketplace.visualstudio.com/items?itemName=Google.geminicodeassist](https://marketplace.visualstudio.com/items?itemName=Google.geminicodeassist)  
Karpathy claude.md:  
[https://github.com/multica-ai/andrej-karpathy-skills/blob/main/CLAUDE.md](https://github.com/multica-ai/andrej-karpathy-skills/blob/main/CLAUDE.md)

## 

## **Task**

Since AI code assistants are now commonly used in software development, this project is designed to give you hands-on practice using them to build a working prototype.

In this project, your team will design and implement a small **campus data-based program prototype**.

The goal is to build a program that uses mock campus data to solve or improve a realistic campus-related problem. 

Use AI code assistants during the project.

Your program should clearly demonstrate the following structure:

| user input → mock campus data → processing pipeline → output |
| :---- |

The output does not need to be a single fixed result: your program may have multiple branches that produce different outputs, and each branch may ask the user for additional input if needed.

## **Team**

This is a team project.

Each team will consist of 4 students. Team members may freely divide responsibilities. In the `README.md` file, briefly describe what each team member mainly contributed to the project.

## **Project Theme**

Your project should propose and implement a prototype of a program that could be useful on campus.

The campus data does **not** need to actually exist. Your team may assume that certain types of campus data are available, as long as the assumption is reasonable. You will then create mock data and use it in your program.

Possible types of campus data include, but are not limited to:

\- Course data: course names, schedules, departments, classrooms, enrollment limits  
\- Classroom data: room capacity, location, available equipment, reservation status  
\- Library or study space data: seat availability, congestion level, opening hours  
\- Cafeteria data: menus, prices, locations, dietary tags, expected congestion  
\- Shuttle or transportation data: stops, routes, schedules, estimated travel time  
\- Campus event data: event time, location, target audience, topic tags  
\- Club or student organization data: activity time, interests, recruitment fields  
\- Facility data: gym, lounge, printer, lab, or other campus facility information

Your team may choose one of these ideas or create a different campus-related idea.

## **Important Notes**

The data does not need to be real. You should create mock data that is reasonable for your project.

Your program should use the mock data you submit. A project that only describes an idea but does not run as a program is not sufficient.

You do not have to build a polished app. A simple command-line program is sufficient. The UI is not important. What matters is that your program receives or uses input, processes mock campus data, and produces a meaningful output.

The submitted zip file should be less than 100MB.

## **Submission**

Submit one compressed folder, named team\[XX\].zip.

You can find your team number from: [https://docs.google.com/spreadsheets/d/1scJciLM7gxh3v4hDXoxmjdov7\_BjMfdcMnGnAP0P2KA/edit?usp=drive\_web\&ouid=107958937572750740914](https://docs.google.com/spreadsheets/d/1scJciLM7gxh3v4hDXoxmjdov7_BjMfdcMnGnAP0P2KA/edit?usp=drive_web&ouid=107958937572750740914) 

When the folder is unzipped, the top-level directory must contain the following files and folders:

| teamXX/  README.md   main.py  src/  sample\_input.json  data/ |
| :---- |

The `data/` folder should contain the mock campus data used by your program.

The `sample_input.json` file should contain an example input that can be used to test your program.

The `main.py` file should be the main entry point of your program.

The `src/` folder may contain other \*.py files if necessary`.`

## **Dependencies and Execution**

Your `README.md` must clearly explain how to install and run your program.

If your project requires additional packages, you must provide clear installation instructions. For example, you may include a `requirements.txt` file and explain how to use it.

Your classmates will evaluate your project based on what they can actually run and test. You can use any libraries (You can even call LLM\!), but if your program is difficult to install or execute, and this causes lower peer review scores, your team is responsible for that outcome.

## **README Requirements**

Your `README.md` file must include the following sections.

| \# Project Title \#\# 0\. team members (Name & Student ID)\#\# 1\. ProblemWhat campus-related problem does your program address?Explain the problem clearly. Also explain why this problem matters to students, instructors, staff, or other campus users.\#\# 2\. Target UsersWho would use this program?Examples:\- Students\- Teaching assistants\- Instructors\- Club organizers\- Dormitory residents\- Library users\- Cafeteria users\- Campus visitors\#\# 3\. Assumed Campus DataWhat campus data does your program assume exists?Describe the mock data files included in the *\`data/\`* folder.| File | Columns / Fields | Description ||---|---|---|| data/example.csv | ... | ... || data/example.json | ... | ... |\#\# 4\. User InputWhat information does the user provide?Describe the structure of *\`sample\_input.json\`*.Example:{  "preferred\_location": "library",  "available\_time": "Tuesday 14:00",  "priority": "quiet"}\#\# 5\. PipelineExplain the internal pipeline of your program.For each major step, describe the input, output, and purpose.You do not need to follow this exact pipeline. However, your README should clearly explain how data flows through your program. \#\# 6\. How to RunProvide the exact command or commands needed to run your program.Example:python main.pyIf additional installation steps are needed, include them here.Example:pip install \-r requirements.txtpython main.py\#\# 7\. Example Output(s)Show examples of the outputs produced by your program. \#\# 8\. Team ContributionsBriefly describe what each team member mainly contributed. |
| :---- |

## **Submission link**

Upload the \*.zip file to the ETL “토론” session: [https://myetl.snu.ac.kr/courses/296230/discussion\_topics/362259](https://myetl.snu.ac.kr/courses/296230/discussion_topics/362259) 

The submission should include:  
1\. team\[XX\].zip file  
2\. Copy & paste of your README.md  
