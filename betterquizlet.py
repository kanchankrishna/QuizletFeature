from flask import Flask, flash, render_template, request, redirect, url_for, session
from apscheduler.scheduler import Scheduler
import sqlite3 as sql
import atexit
import time 

app = Flask(__name__)
app.secret_key = "random string"

class DatabaseInfo:
    def __init__(databaseinfo, databasename, connection, cursor):
        databaseinfo.name = databasename
        databaseinfo.connection = connection
        databaseinfo.cursor = cursor

    def getDatabaseName(databaseinfo):
        return databaseinfo.name

    def getDatabaseCursor(databaseinfo):
        return databaseinfo.cursor

    def getDatabaseConnection(databaseinfo):
        return databaseinfo.connection

#polymorphism show this one 
def getdatabaseconn(dbname, isselect=False): 
        if isselect:
            con = sql.connect(dbname)
            con.row_factory = sql.Row
            cur = con.cursor()
            dbconnection = DatabaseInfo(dbname, con, cur)
        else:
            con = sql.connect("database.db")
            cur = con.cursor()
            dbconnection = DatabaseInfo(dbname, con, cur)
        return dbconnection 



@app.route("/about")
def show_about():
    return render_template("about.html")

@app.route("/learnstudyset", methods=["POST", "GET"])
def learn():
    #this is for if you get the form:
    #if request.method == 'POST':
        #the user has to choose either a term or definition
    return render_template("learnstudyset.html")

@app.route("/afterstudyset", methods=["POST"])
def after_learn():
    if request.method == 'POST':
        termordef = str(request.form.get('studyset'))
        #we got the first row, now we need the definition
        #check what the user selected in the drop down
        #boomer is term and mommy is the definition
        #pass what the user selected to the next page, which is this one
        databaseconn = getdatabaseconn('database.db', True);
        conn = databaseconn.getDatabaseConnection()
        cur = databaseconn.getDatabaseCursor()
        #definition is the column name 
        #limit 2 would give you the first row
        #gives me the list of definition columns, we have the rows
        #to display the first row, do rows[0]
        cur.execute(
            "select term, definition from studysets"
        )
        #length of the list is the number of rows 
        rows = cur.fetchall()
        length = len(rows)
        max_confidence_level = length
        #length is the number of rows, which gives the number of terms and definitions (each) 
        for index in range(1):
            firstrow = rows[index]
            #this gets the first value that we want 
            firstdef = firstrow["definition"]
            firstterm = firstrow["term"]
        #user_answer1 = request.form['thefirstterm']
        #below is the dropdown, NOT checking the user answer if it is correct or not 
        if termordef == "term":
            msg = firstdef
        #we need an else to show that we are now providing the term to the user and they have to write the definition
        #now we are going to check the definition
        if termordef == "definition":
            msg = firstterm
        #then they hit submit
        #now we are doing the confidence level stuff
        #start timing so get the current time
        starttime = time.time()
        #end = time.time()
        #elapsed_time = end - start         
        return render_template("afterstudyset.html", msg = msg, termordef=termordef, firstdef=firstdef, firstterm=firstterm, starttime = starttime, max_confidence_level = max_confidence_level)

#this is after you click the answer button 
@app.route("/answerstudyset", methods=["POST"])
def answerstudyset():
    #this is where we check whether or not the user's answer is correct
    if request.method == 'POST':
        #we are just getting the value
        #the starttime is an integer but then when it gets passed to the HTML file, it gets passed a string, so we have to convert it to a float in order to do the math operation
        confidence_level = 0
        correct_terms = 0
        starttime = request.form['hiddenfield4']
        endtime = time.time()
        diff1 = endtime - float(starttime)
        user_answer1 = request.form['thefirstterm']
        termordef = request.form['hiddenfield1']
        firstdef = request.form['hiddenfield3']
        firstterm = request.form['hiddenfield2']
        if termordef == "term":
            msg = firstdef
        elif termordef == "definition":
            msg = firstterm
        max_confidence_level = request.form['hiddenfield5']
        if termordef == "definition":
            #if they got the answer correct after choosing definition
            if user_answer1 == firstdef:
                 if diff1 <=10:
                     confidence_level = confidence_level + 1
                     correct_terms = correct_terms + 1 
                     correct_msg_under10 = "You got it correct under 10 seconds. Your proficiency level is:" + str(confidence_level) 
                     flash(correct_msg_under10)
                 elif diff1>10 and diff1<=20:
                     confidence_level = confidence_level - 1
                     correct_terms = correct_terms + 1
                     #by under 20 we mean between 10 and 20 
                     correct_msg_under20 = "You got it correct between 10 and 20 seconds.Your proficiency level has gone down to:" + str(confidence_level)
                     flash(correct_msg_under20)
                     return render_template("afterstudyset.html", msg = msg, termordef=termordef, firstdef=firstdef, firstterm=firstterm, starttime = starttime, max_confidence_level = max_confidence_level)
                 else:
                     confidence_level = confidence_level - 1
                     correct_terms = correct_terms - 1
                     correct_msg_above20 = "You got it correct but time has run out!Your proficiency level has gone down to:" + str(confidence_level)
                     flash(correct_msg_above20)
                     return render_template("afterstudyset.html", msg = msg, termordef=termordef, firstdef=firstdef, firstterm=firstterm, starttime = starttime, max_confidence_level = max_confidence_level)

            else:
                #else if they get it wrong...
                confidence_level = confidence_level - 1
                correct_terms = correct_terms - 1
                incorrect_msg = "You got it incorrect.Your proficiency level has gone down to:" + str(confidence_level)
                flash(incorrect_msg)
                return render_template("afterstudyset.html", msg = msg, termordef=termordef, firstdef=firstdef, firstterm=firstterm, starttime = starttime, max_confidence_level = max_confidence_level)
        elif termordef == "term":
            if user_answer1 == firstterm:
                if diff1 <=10:
                    confidence_level = confidence_level + 1
                    correct_terms = correct_terms + 1
                    correct_msg_under10 = "You got it correct under 10 seconds.Your proficiency level is:" + str(confidence_level) 
                    flash(correct_msg_under10)
                elif diff1>10 and diff1<=20:
                     confidence_level = confidence_level - 1
                     correct_terms = correct_terms + 1
                     #by under 20 we mean between 10 and 20 
                     correct_msg_under20 = "You got it correct between 10 and 20 seconds.Your proficiency level has gone down to:" + str(confidence_level)
                     flash(correct_msg_under20)
                     return render_template("afterstudyset.html", msg = msg, termordef=termordef, firstdef=firstdef, firstterm=firstterm, starttime = starttime, max_confidence_level = max_confidence_level)
                else:
                    confidence_level = confidence_level - 1
                    correct_terms = correct_terms + 1
                    correct_msg_above20 = "You got it correct but time has run out!Your proficiency level has gone down to:" + str(confidence_level)
                    flash(correct_msg_above20)
                    return render_template("afterstudyset.html", msg = msg, termordef=termordef, firstdef=firstdef, firstterm=firstterm, starttime = starttime, max_confidence_level = max_confidence_level)
            else:
               #else if they get it wrong...
                confidence_level = confidence_level - 1
                correct_terms = correct_terms - 1 
                incorrect_msg = "You got it incorrect.Your proficiency level has gone down to:" + str(confidence_level)
                flash(incorrect_msg)
                return render_template("afterstudyset.html", msg = msg, termordef=termordef, firstdef=firstdef, firstterm=firstterm, starttime = starttime, max_confidence_level = max_confidence_level)
    return render_template("newpage1.html", termordef = termordef, confidence_level = confidence_level, correct_terms = correct_terms)

@app.route("/studyingsecondtime", methods=["POST"])
def study_second_time():
    #list of variables that i would pass in: confidence level, term or def
    #query the database for the following: max confidence level, second term, second def
    if request.method == 'POST':
        termordef = request.form['hiddenfield1']  
        confidence_level = request.form['hiddenfield5']
        correct_terms = request.form['hiddenfield6']
        databaseconn = getdatabaseconn('database.db', True);
        conn = databaseconn.getDatabaseConnection()
        cur = databaseconn.getDatabaseCursor()
        cur.execute(
            "select term, definition from studysets"
        )
        #length of the list is the number of rows 
        rows = cur.fetchall()
        length = len(rows)
        max_confidence_level = length
        #length is the number of rows, which gives the number of terms and definitions (each)
        #loop through the first two rows
        #ignore where index is 0 aka the first row 
        for index in range(2):
            if index == 1:
                secondrow = rows[index]
            #this gets the first value that we want 
                seconddef = secondrow["definition"]
                secondterm = secondrow["term"]
        if termordef == "term":
            msg = seconddef
        #we need an else to show that we are now providing the term to the user and they have to write the definition
        #now we are going to check the definition
        if termordef == "definition":
            msg = secondterm
        #then they hit submit
        #now we are doing the confidence level stuff
        #start timing so get the current time
        starttime = time.time()
        #end = time.time()
        #elapsed_time = end - start         
    return render_template("studyingsecondtime.html", msg = msg, termordef=termordef, seconddef=seconddef, secondterm=secondterm, starttime = starttime, confidence_level = confidence_level,correct_terms = correct_terms)

@app.route("/answersecondtime", methods=["POST"])
def answer_second_time():
    #get confidence level and correct terms from the hidden field so it is the update value, not 0
    #now we are checking if the second time answer is correct or not
    starttime = request.form['hiddenfield4']
    endtime = time.time()
    diff1 = endtime - float(starttime)
    user_answer2 = request.form['thefirstterm']
    termordef = request.form['hiddenfield1']
    seconddef = request.form['hiddenfield3']
    secondterm = request.form['hiddenfield2']
    if termordef == "term":
        msg = seconddef
    elif termordef == "definition":
        msg = secondterm
    confidence_level = int(request.form['hiddenfield5'])
    correct_terms = int(request.form['hiddenfield6'])
    if termordef == "definition":
            #if they got the answer correct after choosing definition
            if user_answer2 == seconddef:
                 if diff1 <=10:
                     confidence_level = confidence_level + 1
                     correct_terms = correct_terms + 1 
                     correct_msg_under10 = "You got it correct under 10 seconds.Your proficiency level is:" + str(confidence_level) 
                     flash(correct_msg_under10)
                 elif diff1>10 and diff1<=20:
                     confidence_level = confidence_level - 1
                     correct_terms = correct_terms + 1
                     #by under 20 we mean between 10 and 20 
                     correct_msg_under20 = "You got it correct between 10 and 20 seconds. Your proficiency level has gone down to:" + str(confidence_level)
                     flash(correct_msg_under20)
                     return render_template("studyingsecondtime.html", msg = msg, termordef=termordef, seconddef=seconddef, secondterm=secondterm, starttime = time.time(), confidence_level = confidence_level,correct_terms = correct_terms)
                 else:
                     confidence_level = confidence_level - 1
                     correct_terms = correct_terms - 1
                     correct_msg_above20 = "You got it correct but time has run out! Your proficiency level has gone down to:" + str(confidence_level)
                     flash(correct_msg_above20)
                     return render_template("studyingsecondtime.html", msg = msg, termordef=termordef, seconddef=seconddef, secondterm=secondterm, starttime = time.time(), confidence_level = confidence_level,correct_terms = correct_terms)

            else:
                #else if they get it wrong...
                confidence_level = confidence_level - 1
                correct_terms = correct_terms - 1
                incorrect_msg = "You got it incorrect.Your proficiency level has gone down to:" + str(confidence_level)
                flash(incorrect_msg)
                return render_template("studyingsecondtime.html", msg = msg, termordef=termordef, seconddef=seconddef, secondterm=secondterm, starttime = time.time(), confidence_level = confidence_level,correct_terms = correct_terms)
    elif termordef == "term":
            if user_answer2 == secondterm:
                if diff1 <=10:
                    confidence_level = confidence_level + 1
                    correct_terms = correct_terms + 1
                    correct_msg_under10 = "You got it correct under 10 seconds. Your proficiency level is:" + str(confidence_level) 
                    flash(correct_msg_under10)
                elif diff1>10 and diff1<=20:
                     confidence_level = confidence_level - 1
                     correct_terms = correct_terms - 1
                     #by under 20 we mean between 10 and 20 
                     correct_msg_under20 = "You got it correct between 10 and 20 seconds.Your proficiency level has gone down to:" + str(confidence_level)
                     flash(correct_msg_under20)
                     return render_template("studyingsecondtime.html", msg = msg, termordef=termordef, seconddef=seconddef, secondterm=secondterm, starttime = time.time(), confidence_level = confidence_level,correct_terms = correct_terms)
                else:
                    confidence_level = confidence_level - 1
                    correct_terms = correct_terms + 1
                    correct_msg_above20 = "You got it correct but time has run out!Your proficiency level has gone down to:" + str(confidence_level)
                    flash(correct_msg_above20)
                    return render_template("studyingsecondtime.html", msg = msg, termordef=termordef, seconddef=seconddef, secondterm=secondterm, starttime = time.time(), confidence_level = confidence_level,correct_terms = correct_terms)
            else:
               #else if they get it wrong...
                confidence_level = confidence_level - 1
                correct_terms = correct_terms - 1 
                incorrect_msg = "You got it incorrect. Your proficiency level has gone down to:"  + str(confidence_level)
                flash(incorrect_msg)
                return render_template("studyingsecondtime.html", msg = msg, termordef=termordef, seconddef=seconddef, secondterm=secondterm, starttime = time.time(), confidence_level = confidence_level,correct_terms = correct_terms)
    return render_template("newpage2.html", termordef = termordef, confidence_level = confidence_level, correct_terms = correct_terms)

@app.route("/studyingthirdtime", methods=["POST"])
def study_third_time():
    #list of variables that i would pass in: confidence level, term or def
    #query the database for the following: max confidence level, second term, second def
    if request.method == 'POST':
        termordef = request.form['hiddenfield1']  
        confidence_level = request.form['hiddenfield5']
        correct_terms = request.form['hiddenfield6']
        databaseconn = getdatabaseconn('database.db', True);
        conn = databaseconn.getDatabaseConnection()
        cur = databaseconn.getDatabaseCursor()
        cur.execute(
            "select term, definition from studysets"
        )
        #length of the list is the number of rows 
        rows = cur.fetchall()
        length = len(rows)
        max_confidence_level = length
        #length is the number of rows, which gives the number of terms and definitions (each)
        #loop through the first two rows
        #ignore where index is 0 aka the first row 
        for index in range(3):
            if index == 2:
                thirdrow = rows[index]
            #this gets the first value that we want 
                thirddef = thirdrow["definition"]
                thirdterm = thirdrow["term"]
        if termordef == "term":
            msg = thirddef
        #we need an else to show that we are now providing the term to the user and they have to write the definition
        #now we are going to check the definition
        if termordef == "definition":
            msg = thirdterm
        #then they hit submit
        #now we are doing the confidence level stuff
        #start timing so get the current time
        starttime = time.time()
        #end = time.time()
        #elapsed_time = end - start         
    return render_template("studyingthirdtime.html", msg = msg, termordef=termordef, thirddef=thirddef, thirdterm=thirdterm, starttime = starttime, confidence_level = confidence_level,correct_terms = correct_terms)


@app.route("/answerthirdtime", methods=["POST"])
def answer_third_time():
    #get confidence level and correct terms from the hidden field so it is the update value, not 0
    #now we are checking if the second time answer is correct or not
    starttime = request.form['hiddenfield4']
    endtime = time.time()
    diff1 = endtime - float(starttime)
    user_answer3 = request.form['thefirstterm']
    termordef = request.form['hiddenfield1']
    thirddef = request.form['hiddenfield3']
    thirdterm = request.form['hiddenfield2']
    if termordef == "term":
        msg = thirddef
    elif termordef == "definition":
        msg = thirdterm
    confidence_level = int(request.form['hiddenfield5'])
    correct_terms = int(request.form['hiddenfield6'])
    if termordef == "definition":
            #if they got the answer correct after choosing definition
            if user_answer3 == str(thirddef):
                 if diff1 <=10:
                     confidence_level = confidence_level + 1
                     correct_terms = correct_terms + 1 
                     correct_msg_under10 = "You got it correct under 10 seconds.Your proficiency level is:" + str(confidence_level) 
                     flash(correct_msg_under10)
                 elif diff1>10 and diff1<=20:
                     confidence_level = confidence_level - 1
                     correct_terms = correct_terms + 1
                     #by under 20 we mean between 10 and 20 
                     correct_msg_under20 = "You got it correct between 10 and 20 seconds. Your proficiency level has gone down to:" + str(confidence_level)
                     flash(correct_msg_under20)
                     return render_template("studyingthirdtime.html", msg = msg, termordef=termordef, thirddef=thirddef, thirdterm=thirdterm, starttime = time.time(), confidence_level = confidence_level,correct_terms = correct_terms)
                 else:
                     confidence_level = confidence_level - 1
                     correct_terms = correct_terms - 1
                     correct_msg_above20 = "You got it correct but time has run out! Your proficiency level has gone down to:" + str(confidence_level)
                     flash(correct_msg_above20)
                     return render_template("studyingthirdtime.html", msg = msg, termordef=termordef, thirddef=thirddef, thirdterm=thirdterm, starttime = time.time(), confidence_level = confidence_level,correct_terms = correct_terms)

            else:
                #else if they get it wrong...
                confidence_level = confidence_level - 1
                correct_terms = correct_terms - 1
                incorrect_msg = "You got it incorrect.Your proficiency level has gone down to:" + str(confidence_level)
                flash(incorrect_msg)
                return render_template("studyingthirdtime.html", msg = msg, termordef=termordef, thirddef=thirddef, thirdterm=thirdterm, starttime = time.time(), confidence_level = confidence_level,correct_terms = correct_terms)
    elif termordef == "term":
            if user_answer3 == str(thirdterm):
                if diff1 <=10:
                    confidence_level = confidence_level + 1
                    correct_terms = correct_terms + 1
                    correct_msg_under10 = "You got it correct under 10 seconds.Your proficiency level is:" + str(confidence_level) 
                    flash(correct_msg_under10)
                elif diff1>10 and diff1<=20:
                     confidence_level = confidence_level - 1
                     correct_terms = correct_terms - 1
                     #by under 20 we mean between 10 and 20 
                     correct_msg_under20 = "You got it correct between 10 and 20 seconds.Your proficiency level has gone down to:" + str(confidence_level)
                     flash(correct_msg_under20)
                     return render_template("studyingthirdtime.html", msg = msg, termordef=termordef, thirddef=thirddef, thirdterm=thirdterm, starttime = time.time(), confidence_level = confidence_level,correct_terms = correct_terms)
                else:
                    confidence_level = confidence_level - 1
                    correct_terms = correct_terms + 1
                    correct_msg_above20 = "You got it correct but time has run out! Your proficiency level has gone down to:" + str(confidence_level)
                    flash(correct_msg_above20)
                    return render_template("studyingthirdtime.html", msg = msg, termordef=termordef, thirddef=thirddef, thirdterm=thirdterm, starttime = time.time(), confidence_level = confidence_level,correct_terms = correct_terms)
            else:
               #else if they get it wrong...
                confidence_level = confidence_level - 1
                correct_terms = correct_terms - 1 
                incorrect_msg = "You got it incorrect.Your proficiency level has gone down to:" + str(confidence_level)
                flash(incorrect_msg)
                return render_template("studyingthirdtime.html", msg = msg, termordef=termordef, thirddef=thirddef, thirdterm=thirdterm, starttime = time.time(), confidence_level = confidence_level,correct_terms = correct_terms)
    return render_template("newpage3.html", termordef = termordef, confidence_level = confidence_level, correct_terms = correct_terms)

@app.route("/studyingfourthtime", methods=["POST"])
def study_fourth_time():
    #list of variables that i would pass in: confidence level, term or def
    #query the database for the following: max confidence level, second term, second def
    if request.method == 'POST':
        termordef = request.form['hiddenfield1']  
        confidence_level = request.form['hiddenfield5']
        correct_terms = request.form['hiddenfield6']
        databaseconn = getdatabaseconn('database.db', True);
        conn = databaseconn.getDatabaseConnection()
        cur = databaseconn.getDatabaseCursor()
        cur.execute(
            "select term, definition from studysets"
        )
        #length of the list is the number of rows 
        rows = cur.fetchall()
        length = len(rows)
        max_confidence_level = length
        #length is the number of rows, which gives the number of terms and definitions (each)
        #loop through the first two rows
        #ignore where index is 0 aka the first row 
        for index in range(4):
            if index == 3:
                fourthrow = rows[index]
            #this gets the first value that we want 
                fourthdef = fourthrow["definition"]
                fourthterm = fourthrow["term"]
        if termordef == "term":
            msg = fourthdef
        #we need an else to show that we are now providing the term to the user and they have to write the definition
        #now we are going to check the definition
        if termordef == "definition":
            msg = fourthterm
        #then they hit submit
        #now we are doing the confidence level stuff
        #start timing so get the current time
        starttime = time.time()
        #end = time.time()
        #elapsed_time = end - start         
    return render_template("studyingfourthtime.html", msg = msg, termordef=termordef, fourthdef=fourthdef, fourthterm=fourthterm, starttime = starttime, confidence_level = confidence_level,correct_terms = correct_terms)

@app.route("/answerfourthtime", methods=["POST"])
def answer_fourth_time():
    #get confidence level and correct terms from the hidden field so it is the update value, not 0
    #now we are checking if the second time answer is correct or not
    starttime = request.form['hiddenfield4']
    endtime = time.time()
    diff1 = endtime - float(starttime)
    user_answer4 = request.form['thefirstterm']
    termordef = request.form['hiddenfield1']
    fourthdef = request.form['hiddenfield3']
    fourthterm = request.form['hiddenfield2']
    if termordef == "term":
        msg = fourthdef
    elif termordef == "definition":
        msg = fourthterm
    confidence_level = int(request.form['hiddenfield5'])
    correct_terms = int(request.form['hiddenfield6'])
    if termordef == "definition":
            #if they got the answer correct after choosing definition
            if user_answer4 == str(fourthdef):
                 if diff1 <=10:
                     confidence_level = confidence_level + 1
                     correct_terms = correct_terms + 1 
                     correct_msg_under10 = "You got it correct under 10 seconds. Your proficiency level is:" + str(confidence_level) 
                     flash(correct_msg_under10)
                 elif diff1>10 and diff1<=20:
                     confidence_level = confidence_level - 1
                     correct_terms = correct_terms + 1
                     #by under 20 we mean between 10 and 20 
                     correct_msg_under20 = "You got it correct between 10 and 20 seconds. Your proficiency level has gone down to:" + str(confidence_level)
                     flash(correct_msg_under20)
                     return render_template("studyingfourthtime.html", msg = msg, termordef=termordef, fourthdef=fourthdef, fourthterm=fourthterm, starttime = time.time(), confidence_level = confidence_level,correct_terms = correct_terms)
                 else:
                     confidence_level = confidence_level - 1
                     correct_terms = correct_terms - 1
                     correct_msg_above20 = "You got it correct but time has run out!Your proficiency level has gone down to:" + str(confidence_level)
                     flash(correct_msg_above20)
                     return render_template("studyingfourthtime.html", msg = msg, termordef=termordef, fourthdef=fourthdef, fourthterm=fourthterm, starttime = time.time(), confidence_level = confidence_level,correct_terms = correct_terms)

            else:
                #else if they get it wrong...
                confidence_level = confidence_level - 1
                correct_terms = correct_terms - 1
                incorrect_msg = "You got it incorrect" + str(confidence_level)
                flash(incorrect_msg)
                return render_template("studyingfourthtime.html", msg = msg, termordef=termordef, fourthdef=fourthdef, fourthterm=fourthterm, starttime = time.time(), confidence_level = confidence_level,correct_terms = correct_terms)
    elif termordef == "term":
            if user_answer4 == str(fourthterm):
                if diff1 <=10:
                    confidence_level = confidence_level + 1
                    correct_terms = correct_terms + 1
                    correct_msg_under10 = "You got it correct under 10 seconds. Your proficiency level is:" + str(confidence_level) 
                    flash(correct_msg_under10)
                elif diff1>10 and diff1<=20:
                     confidence_level = confidence_level + 1
                     correct_terms = correct_terms - 1
                     #by under 20 we mean between 10 and 20 
                     correct_msg_under20 = "You got it correct between 10 and 20 seconds. Your proficiency level has gone down to:" + str(confidence_level)
                     flash(correct_msg_under20)
                     return render_template("studyingfourthtime.html", msg = msg, termordef=termordef, fourthdef=fourthdef, fourthterm=fourthterm, starttime = time.time(), confidence_level = confidence_level,correct_terms = correct_terms)
                else:
                    confidence_level = confidence_level - 1
                    correct_terms = correct_terms + 1
                    correct_msg_above20 = "You got it correct but time has run out! Your proficiency level has gone down to:" + str(confidence_level)
                    flash(correct_msg_above20)
                    return render_template("studyingfourthtime.html", msg = msg, termordef=termordef, fourthdef=fourthdef, fourthterm=fourthterm, starttime = time.time(), confidence_level = confidence_level,correct_terms = correct_terms)
            else:
               #else if they get it wrong...
                confidence_level = confidence_level - 1
                correct_terms = correct_terms - 1 
                incorrect_msg = "You got it incorrect, your proficiency level is" + str(confidence_level)
                flash(incorrect_msg)
                return render_template("studyingfourthtime.html", msg = msg, termordef=termordef, fourthdef=fourthdef, fourthterm=fourthterm, starttime = time.time(), confidence_level = confidence_level,correct_terms = correct_terms)
    return render_template("newpage4.html", termordef = termordef, confidence_level = confidence_level, correct_terms = correct_terms)

@app.route("/studyingfifthtime", methods=["POST"])
def study_fifth_time():
    #list of variables that i would pass in: confidence level, term or def
    #query the database for the following: max confidence level, second term, second def
    if request.method == 'POST':
        termordef = request.form['hiddenfield1']  
        confidence_level = request.form['hiddenfield5']
        correct_terms = request.form['hiddenfield6']
        databaseconn = getdatabaseconn('database.db', True);
        conn = databaseconn.getDatabaseConnection()
        cur = databaseconn.getDatabaseCursor()
        cur.execute(
            "select term, definition from studysets"
        )
        #length of the list is the number of rows 
        rows = cur.fetchall()
        length = len(rows)
        max_confidence_level = length
        #length is the number of rows, which gives the number of terms and definitions (each)
        #loop through the first two rows
        #ignore where index is 0 aka the first row 
        for index in range(5):
            if index == 4:
                fifthrow = rows[index]
            #this gets the first value that we want 
                fifthdef = fifthrow["definition"]
                fifthterm = fifthrow["term"]
        if termordef == "term":
            msg = fifthdef
        #we need an else to show that we are now providing the term to the user and they have to write the definition
        #now we are going to check the definition
        if termordef == "definition":
            msg = fifthterm
        #then they hit submit
        #now we are doing the confidence level stuff
        #start timing so get the current time
        starttime = time.time()
        #end = time.time()
        #elapsed_time = end - start         
    return render_template("studyingfifthtime.html", msg = msg, termordef=termordef, fifthdef=fifthdef, fifthterm=fifthterm, starttime = starttime, confidence_level = confidence_level,correct_terms = correct_terms)


@app.route("/answerfifthtime", methods=["POST"])
def answer_fifth_time():
    #get confidence level and correct terms from the hidden field so it is the update value, not 0
    #now we are checking if the second time answer is correct or not
    starttime = request.form['hiddenfield4']
    endtime = time.time()
    diff1 = endtime - float(starttime)
    user_answer5 = request.form['thefirstterm']
    termordef = request.form['hiddenfield1']
    fifthdef = request.form['hiddenfield3']
    fifthterm = request.form['hiddenfield2']
    if termordef == "term":
        msg = fifthdef
    elif termordef == "definition":
        msg = fifthterm
    confidence_level = int(request.form['hiddenfield5'])
    correct_terms = int(request.form['hiddenfield6'])
    if termordef == "definition":
        #if they got the answer correct after choosing definition
        if user_answer5 == str(fifthdef):
            if diff1 <=10:
                confidence_level = confidence_level + 1
                correct_terms = correct_terms + 1 
                correct_msg_under10 = "You got it correct under 10 seconds.Your proficiency level is:" + str(confidence_level) 
                flash(correct_msg_under10)
            elif diff1>10 and diff1<=20:
                confidence_level = confidence_level - 1
                correct_terms = correct_terms + 1
                #by under 20 we mean between 10 and 20 
                correct_msg_under20 = "You got it correct between 10 and 20 seconds. Your proficiency level has gone down to:" + str(confidence_level)
                flash(correct_msg_under20)
                return render_template("studyingfifthtime.html", msg = msg, termordef=termordef, fifthdef=fifthdef, fifthterm=fifthterm, starttime = time.time(), confidence_level = confidence_level,correct_terms = correct_terms)
            else:
                confidence_level = confidence_level - 1
                correct_terms = correct_terms - 1
                correct_msg_above20 = "You got it correct but time has run out!Your proficiency level has gone down to:" + str(confidence_level)
                flash(correct_msg_above20)
                return render_template("studyingfifthtime.html", msg = msg, termordef=termordef, fifthdef=fifthdef, fifthterm=fifthterm, starttime = time.time(), confidence_level = confidence_level,correct_terms = correct_terms)

        elif user_answer5 != str(fifthdef):
            #else if they get it wrong...
            confidence_level = confidence_level - 1
            correct_terms = correct_terms - 1
            incorrect_msg = "You got it incorrect.Your proficiency level has gone down to:"+ str(confidence_level)
            flash(incorrect_msg)
            return render_template("studyingfifthtime.html", msg = msg, termordef=termordef, fifthdef=fifthdef, fifthterm=fifthterm, starttime = time.time(), confidence_level = confidence_level,correct_terms = correct_terms)
    elif termordef == "term":
    #all three of the cases should be correct
        if user_answer5 == 'propensity':
            if diff1 <=10:
                    confidence_level = confidence_level + 1
                    correct_terms = correct_terms + 1
                    correct_msg_under10 = "You got it correct under 10 seconds. Your proficiency level is:" + str(confidence_level) 
                    flash(correct_msg_under10)
            elif diff1>10 and diff1<=20:
                     confidence_level = confidence_level - 1
                     correct_terms = correct_terms - 1
                     #by under 20 we mean between 10 and 20 
                     correct_msg_under20 = "You got it correct between 10 and 20 seconds.Your proficiency level has gone down to:" + str(confidence_level)
                     flash(correct_msg_under20)
                     return render_template("studyingfifthtime.html", msg = msg, termordef=termordef, fifthdef=fifthdef, fifthterm=fifthterm, starttime = time.time(), confidence_level = confidence_level,correct_terms = correct_terms)
            else:
                    confidence_level = confidence_level - 1
                    correct_terms = correct_terms + 1
                    correct_msg_above20 = "You got it correct but time has run out!Your proficiency level has gone down to:" + str(confidence_level)
                    flash(correct_msg_above20)
                    return render_template("studyingfifthtime.html", msg = msg, termordef=termordef, fifthdef=fifthdef, fifthterm=fifthterm, starttime = time.time(), confidence_level = confidence_level,correct_terms = correct_terms)
        elif user_answer5 != str(fifthdef):
            #else if they get it wrong...
            confidence_level = confidence_level - 1
            correct_terms = correct_terms - 1 
            incorrect_msg = "You got it incorrect.Your proficiency level has gone down to:" + str(confidence_level)
            flash(incorrect_msg)
            return render_template("studyingfifthtime.html", msg = msg, termordef=termordef, fifthdef=fifthdef, fifthterm=fifthterm, starttime = time.time(), confidence_level = confidence_level,correct_terms = correct_terms)
    return render_template("newpage5.html", termordef = termordef, confidence_level = confidence_level, correct_terms = correct_terms)

@app.route("/createstudyset")
def create_set():
    return render_template("createstudyset.html")

@app.route("/viewstudyset")
def view_set():
    databaseconn = getdatabaseconn('database.db', True);
    conn = databaseconn.getDatabaseConnection()
    cur = databaseconn.getDatabaseCursor()
    cur.execute(
        "select term, definition from studysets"
    )
    rows = cur.fetchall()
    return render_template("viewstudyset.html", rows=rows)
   

@app.route("/savestudyset", methods=["POST", "GET"])
def save_set():
    #this is after you hit the submit button
    #get the values of all of the terms and definitions
    firstterm = request.form["firstterm"]
    firsttermdef = request.form["firsttermdef"]
    secondterm = request.form["secondterm"]
    secondtermdef = request.form["secondtermdef"]
    thirdterm = request.form["thirdterm"]
    thirdtermdef = request.form["thirdtermdef"]
    fourthterm = request.form["fourthterm"]
    fourthtermdef = request.form["fourthtermdef"]
    fifthterm = request.form["fifthterm"]
    fifthtermdef = request.form["fifthtermdef"]
    if 'username' in session:
        username = session['username']
    conn = sql.connect("database.db")
    cur = conn.cursor()
    #cur.execute is for each row in the database, for us, definition and term is in one row
    #first row
    cur.execute(
            "INSERT INTO studysets (username, term, definition) VALUES (?, ?, ?)",
            (username, firstterm, firsttermdef,)
        )
    cur.execute(
            "INSERT INTO studysets (username, term, definition) VALUES (?, ?, ?)",
            (username, secondterm, secondtermdef,)
        )
    cur.execute(
            "INSERT INTO studysets (username, term, definition) VALUES (?, ?, ?)",
            (username, thirdterm, thirdtermdef,)
        )
    cur.execute(
            "INSERT INTO studysets (username, term, definition) VALUES (?, ?, ?)",
            (username, fourthterm, fourthtermdef,)
        )
    cur.execute(
            "INSERT INTO studysets (username, term, definition) VALUES (?, ?, ?)",
            (username, fifthterm, fifthtermdef,)
        )
    conn.commit()
    msg = ( "You have successfully created a study set.")
    return render_template("savestudyset.html", msg=msg)

@app.route("/login")
def login():
    
    conn = sql.connect("database.db")
    conn.execute(
        "CREATE TABLE IF NOT EXISTS tennisreviews (username TEXT, name TEXT, userreview TEXT)"
    )
    conn.execute(
        "CREATE TABLE IF NOT EXISTS users (name TEXT,username TEXT, useremail TEXT, password TEXT)"
    )
    conn.close()
    
    return render_template("login.html")

@app.route("/afterlogin", methods=["POST", "GET"])
def check_user_credentials():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        #storing the username as a session object, which lives until you log out 
        session['username'] = request.form['username']
        password = request.form['password']
        #get database connection
        databaseconn = getdatabaseconn('database.db', True)
        cur = databaseconn.getDatabaseCursor();
        #searching for data in the database
        cur.execute(" SELECT * FROM users WHERE username  = ? and password= ? ", [username, password])
        rows = cur.fetchall()
        if len(rows) == 0:
            error = 'Invalid Credentials. Please try again.'
        else:
            return redirect(url_for('home'))
    return render_template('login.html', error=error)

@app.route("/createaccount")
def createaccount():
    return render_template("createaccount.html")

@app.route("/saveaccount", methods=["POST"])
def saveaccount():
    name = request.form['name']
    username = request.form['username']
    emailaddress  = request.form['emailaddress']
    password = request.form['password']
    databaseconn = getdatabaseconn('database.db', True);
    cur = databaseconn.getDatabaseCursor();
    conn = databaseconn.getDatabaseConnection();
    #in the next line of code we check to see if someone's username or useremail already matches an existing username or useremail
    cur.execute("select * from users where username= ? or useremail= ?",[username, emailaddress])
    rows = cur.fetchall()
    if len(rows) != 0:
        error = 'Sorry, this username or email is already in use. Please enter a different username.'
    else:
        #let them pass and put these in the database
        cur.execute("INSERT INTO users (name, username, useremail, password) VALUES (?, ?, ? ,?)",(name, username, emailaddress, password,))
        conn.commit()
        return render_template("login.html")
    return render_template("createaccount.html", error=error)

@app.route('/logout')
def logout():
   # remove the username from the session object
   session.pop('username', None)
   return redirect(url_for('login'))



@app.route("/")
def home():
    conn = sql.connect("database.db")
    conn.execute(
        "CREATE TABLE IF NOT EXISTS reviews (reviews TEXT)"
        )
    conn.execute(
        "CREATE TABLE IF NOT EXISTS users (name TEXT,username TEXT, useremail TEXT, password TEXT)"
    )
    conn.execute(
        "CREATE TABLE IF NOT EXISTS studysets (username TEXT, term TEXT, definition TEXT)"
    )
    conn.commit()
    conn.close()
  
    if 'username' in session:
      username = session['username']
      msg = ("You are logged in as:" + username)
      return render_template("home.html", msg=msg)
    
    return render_template("login.html") 


@app.route("/reviews")
def view_reviews():
    return render_template("reviews.html")


@app.route('/savereviews', methods = ["POST"])
def save_reviews():
    if request.method == "POST":
        user_review = request.form["theuserreview"]
        conn = sql.connect("database.db")
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO reviews (reviews) VALUES (?)",
            (user_review,)
        )
        conn.commit()
        flash(
            "Thank you for submitting your review! Enjoy the app.")
        return render_template("reviews.html")



if __name__ == "__main__":
    app.run(debug=True)

