import subprocess

from flask import Flask, redirect, url_for, render_template, request, session,jsonify
import pandas as pd
from dbConnection import DBconnection
from algorithm import Algorithm
from streamlit import caching
import threading,secrets, time
from flask_caching import Cache


cache = Cache(config={"CACHE_TYPE": "simple"})

app = Flask(__name__)
cache.init_app(app)
app.config['JSON_SORT_KEYS'] = False
secretKey = secrets.token_urlsafe(16)
app.config['SECRET_KEY'] = secretKey

## index page
@app.route("/")
def home():
    caching.clear_cache()
    teacher_num = x.getTeacherNUm()
    studen_num = x.getStudentNUm()
    return render_template("index.html" , teacher_num=teacher_num , studen_num=studen_num)


# @app.errorhandler(Exception)
# def handle_exception(error):
#     responsesData = 'יש לבחור מורה / תלמיד'
#     return render_template("login.html", responsesData=responsesData)

#login page
@app.route("/login" , methods=['GET', 'POST'])
def login():
    response = None
    cache = Cache(config={"CACHE_TYPE": "simple"})
    if request.method == 'POST':
        cache = Cache(config={"CACHE_TYPE": "simple"})
        name = request.form['username']
        password = request.form['pass']
        role = request.form['option']
        response = x.getUser(name,password,role)
        time.sleep(5)
        if response:
        #try:
            userID = x.userid()
            session['userID'] = userID
            id = session['userID']
            if response == 't':
                result = x.getUserName(id)
                classData = x.getClassData(id)
                classNum = x.getClassNum(id)
                render_template("teacherWorkEnvironment.html", result=result , data=classData , classNum=int(classNum[0][0]))
                return redirect('teacherWorkEnvironment')
            else:
                id = session['userID']
                result = x.getUserName(id)
                className = x.getClassName(id)
                exNum = x.getExerciseNum(str(className[0][0]))
                exList = x.getExList(str(className[0][0]))
                render_template("studentEnvironment.html", result=result , className=className[0][0] , exNum=int(exNum[0][0]) , exList=exList)
                return redirect('studentEnvironment')
                #except Exception as e:
               #handle_exception()
    return render_template("login.html", responsesData='')

# signon page
@app.route("/signin", methods=['GET', 'POST'])
def signin():
    cache = Cache(config={"CACHE_TYPE": "simple"})
    if request.method == 'POST':
        caching.clear_cache()
        id = request.form['id']
        fn = request.form['fn']
        ln = request.form['ln']
        un = request.form['username']
        password = request.form['pass']
        userRole = request.form['options']
        x.createUser(id,fn,ln,un,password,userRole)
        return render_template("index.html")
    return render_template("signin.html")

#teacher work environment page
@app.route("/teacherWorkEnvironment")
def teacherWorkEnvironment():
    id = session['userID']
    result = x.getUserName(id)
    classData = x.getClassData(id)
    classNum = x.getClassNum(id)
    return render_template("teacherWorkEnvironment.html" , result = result , data=classData , classNum=int(classNum[0][0]))

# add class to teacher page
@app.route("/addClass" , methods=['GET', 'POST'])
def addClass():
    id = session['userID']
    if request.method == 'POST':
        classN = request.form['className']
        num = request.form['studentsNum']
        num = int(num)
        file = request.form['upload-file']
        data = pd.read_excel(file)
        for key in range(num):
            x.conectStudent(int(data.values[key][0]),classN)
        x.createClass(classN, num)
        return redirect('teacherWorkEnvironment')
    return render_template("addClass.html")

# show class details page
@app.route("/classDetails/<className>" , methods=['GET', 'POST'])
def classDetails(className):
    id = session['userID']
    result = x.getUserName(id)
    studentsD = x.getStudentsD(className)
    studentsNum = x.getStudentsNum(className)
    return render_template("classDetails.html" , result = result , className=className , studentsD=studentsD , studentsNum=int(studentsNum[0][0]))

# show student card page
@app.route("/studentCard/<student_id>" )
def studentCard(student_id):
    id = session['userID']
    result = x.getUserName(id)
    studentName = x.getUserName(student_id)
    className = x.getClassName(student_id)
    studentCard = x.getStudentCardDetails(student_id)
    card_len = len(studentCard)
    return render_template("studentCard.html" , result = result , studentName=studentName , className=className[0][0] , studentCard=studentCard , card_len=card_len)

# show equation information page
@app.route("/equationInfo/<exercise>/<eqCode>" , methods=['GET', 'POST'])
def equationInfo(exercise, eqCode):
    id = session['userID']
    result = x.getUserName(id)
    equationData = x.getEquationData(id , eqCode)
    eqNum = len(equationData)
    equation = x.getEquation(eqCode)
    return render_template("equationInfo.html" , result = result , equation=equation[0][0] , equationData=equationData , eqNum=eqNum )

# add exercise page
@app.route("/addExercise" , methods=['GET', 'POST'])
def addExercise():
    id = session['userID']
    if request.method == 'POST':
        className = request.form['className']
        exercise = request.form['exName']
        num = request.form['eqNum']
        num = int(num)
        file = request.form['upload-file']
        x.createExercise(file, num , exercise , className)
        result = x.getUserName(id)
        studentsD = x.getStudentsD(className)
        studentsNum = x.getStudentsNum(className)
        redirect('classDetails/<className>')
        return render_template("classDetails.html", result=result, className=className, studentsD=studentsD,
                               studentsNum=int(studentsNum[0][0]))
    return render_template("addExercise.html")

# show exercises in class page
@app.route("/showExercises/<className>" , methods=['GET', 'POST'])
def showExercises(className):
    id = session['userID']
    result = x.getUserName(id)
    studentsD = x.getStudentsD(className)
    studentsNum = x.getStudentsNum(className)
    exNum = x.getExerciseNum(className)
    exList = x.getExList(className)
    return render_template("showExercises.html" , result = result , className=className , studentsD=studentsD , studentsNum=int(studentsNum[0][0]) , exNum=int(exNum[0][0]) , exList=exList)

# show feedback to exercise
@app.route("/teacherFeedback/<className>/<exercise>" , methods=['GET', 'POST'])
def teacherFeedback(className,exercise):
    id = session['userID']
    result = x.getUserName(id)
    studentsD = x.getStudentsD(className)
    studentsNum = x.getStudentsNum(className)
    exNum = x.getExerciseNum(className)
    exList = x.getExList(className)
    eqNum = x.getEqNum(exercise)
    eqList = x.getEqList(exercise)
    trueAns = x.getTrueAns(className , eqList)
    falseAns = x.getFalseAns(className, eqList)
    frequentErr = x.getFrequentErr(className, eqList)
    eqCodeList = x.getEqListCode(eqList)
    return render_template("teacherFeedback.html" , result = result ,exercise=exercise, eqList=eqList, eqNum=int(eqNum[0][0]), className=className , studentsD=studentsD , studentsNum=int(studentsNum[0][0]) , exNum=int(exNum[0][0]) , exList=exList , trueAns=trueAns , falseAns=falseAns , frequentErr=frequentErr , eqCodeList=eqCodeList)

# student environment page
@app.route("/studentEnvironment")
def studentEnvironment():
    id = session['userID']
    result = x.getUserName(id)
    className = x.getClassName(id)
    exNum = x.getExerciseNum(str(className[0][0]))
    exList = x.getExList(str(className[0][0]))
    return render_template("studentEnvironment.html" , result = result ,className=className[0][0] , exNum=int(exNum[0][0]) , exList=exList)

# show exercise equation information
@app.route("/exerciseDetails/<exercise>/<index>", methods=['GET', 'POST'])
def exerciseDetails(exercise , index):
    id = session['userID']
    result = x.getUserName(id)
    eqNum = x.getEqNum(exercise)
    className = x.getClassName(id)
    exNum = x.getExerciseNum(str(className[0][0]))
    eqList = x.getEqList(exercise)
    errorCodeLst = x.getErrorCodeLst(id, exercise)
    eq_code = x.getEqCode(exercise)
    studentFeedback = x.getStudentFeedback(id, exercise, eq_code)
    if request.method == 'POST':
        eq_no = index
        solution = request.form['solution']
        eq_code=x.getEqCode(exercise)
        eC = x.insertSolution(id,solution , exercise , eq_no , eq_code)
        equation = x.getEquation(eC)
        reply=y.getConclusion(solution , equation[0][0])
        x.updateFeedback(id,eC,reply)
        x.updateStudentAns(id, solution, eC)
        x.insertTeacherAns(int(eqNum[0][0]), eq_code, id)
        teacherA = x.getTeacherA(eq_code)
        studentAns = x.getStudentAns(id, exercise, eq_code)
        studentFeedback = x.getStudentFeedback(id, exercise, eq_code)
        errorCodeLst = x.getErrorCodeLst(id, exercise)
        return render_template("exerciseDetails.html", result=result, className=className[0][0], exNum=int(exNum[0][0]), eqList=eqList, exName=exercise, eqNum=int(eqNum[0][0]) , errorCodeLst=errorCodeLst , studentFeedback=studentFeedback , index=int(index))
    return render_template("exerciseDetails.html" , result = result ,className=className[0][0] , exNum=int(exNum[0][0]) , eqList=eqList , exName=exercise , eqNum=int(eqNum[0][0]) , errorCodeLst=errorCodeLst , studentFeedback=studentFeedback , index=int(index))

#show feedback
@app.route("/reply/<exercise>/<eqCode>", methods=['GET', 'POST'])
def reply(exercise,eqCode):
    id = session['userID']
    result = x.getUserName(id)
    eqNum = x.getEqNum(exercise)
    className = x.getClassName(id)
    exNum = x.getExerciseNum(str(className[0][0]))
    eqList = x.getEqList(exercise)
    errorCodeLst = x.getErrorCodeLst(id, exercise)
    eq_code = x.getEqCode(exercise)
    studentFeedback = x.getStudentFeedback(id, exercise, eq_code)
    if request.method == 'POST':
        eq_no = request.form['eqNum']
        solution = request.form['solution']
        eq_code=x.getEqCode(exercise)
        eC = x.insertSolution(id,solution , exercise , eq_no , eq_code)
        equation = x.getEquation(eC)
        reply=y.getConclusion(solution , equation[0][0])
        x.updateFeedback(id,eC,reply)
        x.updateStudentAns(id, solution, eC)
        x.insertTeacherAns(int(eqNum[0][0]), eq_code, id)
        teacherA = x.getTeacherA(eq_code)
        studentAns = x.getStudentAns(id, exercise, eq_code)
        studentFeedback = x.getStudentFeedback(id, exercise, eq_code)
        errorCodeLst = x.getErrorCodeLst(id, exercise)
        return render_template("reply.html", result=result, className=className[0][0], exNum=int(exNum[0][0]), eqList=eqList, exName=exercise, eqNum=int(eqNum[0][0]) , errorCodeLst=errorCodeLst , studentFeedback=studentFeedback , eqCode=eqCode)
    return render_template("reply.html" , result = result ,className=className[0][0] , exNum=int(exNum[0][0]) , eqList=eqList , exName=exercise , eqNum=int(eqNum[0][0]) , errorCodeLst=errorCodeLst , studentFeedback=studentFeedback , eqCode=eqCode)

# student solve equation page
@app.route("/solveEquation/<exercise>/<eqCode>", methods=['GET', 'POST'])
def solveEquation(exercise,eqCode):
    id = session['userID']
    result = x.getUserName(id)
    eqNum = x.getEqNum(exercise)
    className = x.getClassName(id)
    exNum = x.getExerciseNum(str(className[0][0]))
    eqList = x.getEqList(exercise)
    if request.method == 'POST':
        eq_no = eqCode
        solution = request.form['solution']
        eq_code=x.getEqCode(exercise)
        eC = x.insertSolution(id,solution , exercise , eq_no , eq_code)
        equation = x.getEquation(eC)
        reply=y.getConclusion(solution , equation)
        x.updateFeedback(id,eC,reply)
        x.updateStudentAns(id, solution, eC)
        errorCodeLst = x.getErrorCodeLst(id, exercise)
        return render_template("exerciseDetails.html", result=result, className=className[0][0], exNum=int(exNum[0][0]), eqList=eqList, exName=exercise, eqNum=int(eqNum[0][0]) , errorCodeLst=errorCodeLst)
    return render_template("solveEquation.html" , result = result ,className=className[0][0] , exNum=int(exNum[0][0]) , eqList=eqList , exName=exercise , eqNum=int(eqNum[0][0]) , eqCode=int(eqCode))

# feedback page
@app.route("/feedback/<exercise>", methods=['GET', 'POST'])
def feedback(exercise):
    id = session['userID']
    result = x.getUserName(id)
    eqNum = x.getEqNum(exercise)
    className = x.getClassName(id)
    exNum = x.getExerciseNum(str(className[0][0]))
    eqList = x.getEqList(exercise)
    eq_code = x.getEqCode(exercise)
    x.insertTeacherAns(int(eqNum[0][0]) ,eq_code , id)
    teacherA=x.getTeacherA(eq_code)
    studentAns = x.getStudentAns(id, exercise , eq_code)
    studentFeedback=x.getStudentFeedback(id,exercise,eq_code)
    return render_template("feedback.html" , result = result ,className=className[0][0] , exNum=int(exNum[0][0]) , eqList=eqList , exName=exercise , eqNum=int(eqNum[0][0]) , teacherA=teacherA, studentAns=studentAns , studentFeedback=studentFeedback)

#logout page
@app.route("/logout")
def logout():
    app.config['SECRET_KEY'] = 'logout'
    session.pop('userId' , None)
    cache = Cache(config={"CACHE_TYPE": "simple"})
    print(f'cashe clean {cache}')
    caching.clear_cache()
    render_template("index.html")
    return redirect("/")

# server conections
if __name__ == "__main__":
    x = DBconnection()
    y = Algorithm()
    threading.Thread(app.run(debug=True))