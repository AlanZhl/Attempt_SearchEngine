# Job Searching and Management Platform
Any comments and advices are welcomed!
_(For the detailed documentation, click [here](/doc))_

## Overview
This project aims to design a simple job searching website. It provides users with up-to-date job post information and supports job searching and filtering. It also allows companies to post and manage new job opportunities decently. The resources are collected from [Indeed](https://sg.indeed.com/?r=us). The developer hopes to realize similar functions as a normal job searching website.

## Structure Outline
This project is built up with 4 important components, which can be listed as follows:
* __web crawler:__ used to collect job posts from Indeed routinely
* __front-end UI:__ provide user interfaces for job searching and result displaying
* __back-end API:__ realize the logic for web pages, retrieve and proceed with user inputs while interact with databases to collect and return the results
* __databases__: used to store all the useful information (roles, users, jobs, etc.) and provide quick searches for job posts.

Meanwhile, the job searching platform generally provides the following functions:
* job posts searching platform open to any users (registered or unregistered); the page also supports post-searching operations like filtering and sorting;
* registration and logging in for users;
* a simple recommendation of jobs for users based on searching histories when no search is conducted;
* creation and management of job posts specified for companies;
* management of users specified for administrators.

## Infrastructure
The overall project is written in __Python__, and supported by __Flask__.

The web crawler uses Selenium to retrieve the static / dynamic contents from the original website. Once the contents are collected, they are proceeded locally with Beautiful Soup (bs4).

The front-end pages are displayed as html files with CSS styles. Bootstrap is chosen for page rendering. The results of interaction between front-end and back-end APIs are reflected in web pages with the help of Jinja2 template rendering engine, which is provided by Flask.

The back-end logics are realized with Flask, a lightweight Python framework. The visiting activities are recorded by cookies and sessions, and the sessions are stored in __Redis__.

Apart from the use of Redis, two types of database systems are applied in this project. __MySQL__ is selected for storing all the detailed information, including roles, accounts and job posts (forward indexed). Sqlalchemy is applied to interact with MySQL through Python script. Meanwhile, since the main function of a job searching site is the search for jobs, __Elasticsearch__ is adopted to support inverted indexing of the job posts in order to accelerate the searching process. 

