# Project Vaccine Distribution

This repository provides a basic structure for collaborating with your teammates on project Vaccine Distribution. Read the following content carefully to understand the file structure as well as how to work with git and SQLite. 

## File structure
This section explains which file goes under which folder. It's important to upload your code and report to the right folder so that TAs can easily find them for grading

    .project-vaccine-distribution
    ├── code                              # Submit code required to run the code for project part II & III
    │   ├── .gitignore
    │   ├── requirements.txt              # IMPORTANT: see NOTES below
    │   ├── part2.py                      # python file for part II
    │   ├── part3.py                      # python file for part III
    │   ├── part2.sql                     # sql file for part II
    │   ├── part3.sql                     # sql file for part III
    ├── data                              # contain the sample data for Vaccine Distribution projects
    │   ├── sampleData.xls                # sample data as an excel file
    ├── database                          # IMPORTANT: see NOTES below
    │   ├── .gitignore
    │   ├── vaccine.db                    # final version of Vaccine Distribution database
    ├── report                            # Submit report for the relevant part
    │   ├── partI.pdf
    │   ├── ....
    └── README.md

### NOTES:
1. **requirements.txt**

    In order to keep track of Python modules and packages required by your project, we provided a ```requirements.txt``` file with some starter packages required for data preprocessing. You can install these packages by running ```pip install -r requirements.txt```. Please add additional packages that you install for the project to this file. 

2. **(DEFAULT OPTION) SQLite database**

    Most SQL database engines are are client/server based such as PostgreSQL, MySQL, etc. Client/server SQL database engines strive to implement a shared repository of data. They support scalability, concurrency, centralization, and control. 
    
    SQLite is an serverless database. It is designed to provide **local data storage** for individual applications and devices. SQLite supports an unlimited number of simultaneous readers, but it will only allow one writer at any instant in time.
    
    Read more: [SQLite Is Serverless](https://sqlite.org/serverless.html) and [Appropriate Uses For SQLite](https://www.sqlite.org/whentouse.html)

    In order to avoid git conflicts when multiple team members write to a shared database, it is advisable that each team member creates their own project database on local machine for testing. You can skip pushing the SQLite database to group repository by adding ```project_database.db``` file to ```.gitignore```. In development phase, you only need to push the code for creating and querying the database. The code updates will only affect your local database.

    Once there are no need to edit the database file, you can push it to group repository, under database folder. 

## How to work with git

Here's a list of recommended next steps to make it easy for you to get started with project. However, understanding the concept of git workflow and git fork is essential. 

-   [Create a fork of this official repository](https://docs.gitlab.com/ee/user/project/repository/forking_workflow.html#creating-a-fork)
-   [Add a SSH key to your gitlab account](https://docs.gitlab.com/ee/user/ssh.html#add-an-ssh-key-to-your-gitlab-account)
-   Clone the fork to your local repository
```
git clone git@version.aalto.fi:cs-a1153_databases_projects/project-vaccine-distribution.git
```
-   [Add a remote to keep your fork synced with the official repository](https://docs.gitlab.com/ee/user/project/repository/forking_workflow.html#repository-mirroring)
```
git remote add upstream git@version.aalto.fi:cs-a1153_databases_projects/project-vaccine-distribution.git
git pull upstream main                                  # if the official repository is updated you must pull the upstream
git push origin main                                    # Update your public repository
```

### Git guideline
-   [Feature branch workflow](https://docs.gitlab.com/ee/gitlab-basics/feature_branch_workflow.html)
-   [Feature branch development](https://docs.gitlab.com/ee/topics/git/feature_branch_development.html)
-   [Add files to git repository](https://docs.gitlab.com/ee/gitlab-basics/add-file.html#add-a-file-using-the-command-line)


## (ADVANCED OPTION) How to work with Postgres (Sophie & Ezra)