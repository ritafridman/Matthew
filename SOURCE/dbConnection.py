import mysql.connector, json
import pandas as pd
from algorithm import Algorithm
from mysql.connector import errorcode

class DBconnection:

# connection to data base
    def __init__(self):
        self._connection = mysql.connector.connect(user='mathew', password='mathew2020',port=3306,
                                                   database='mathew')
        self._user_id = None

# get number of teachers in the system
    def getTeacherNUm(self):
        res_data = self._connection.cursor()
        res_data.execute("SELECT count(*) FROM users WHERE role=%(R)s;" , {'R' : 't'})
        res = res_data.fetchall()
        return res[0][0]

# get students number in the system
    def getStudentNUm(self):
        res_data = self._connection.cursor()
        res_data.execute("SELECT count(*) FROM users WHERE role=%(R)s;", {'R': 's'})
        res = res_data.fetchall()
        return res[0][0]

# get user id
    def getUser(self,username, password ,role):
        res_data = self._connection.cursor()
        res_data.execute("SELECT * FROM users")
        res = res_data.fetchall()
        for account in res:
            dic = {"id":None, "user":None, "passw":None}
            dic["id"] = account[0]
            dic["user"] = account[1]
            dic["passw"] = account[2]
            dic["role"] = account[5]
            res = tuple(res)
            for user in res:
                self._userid = user[0]
                usernam = user[1]
                passw = user[2]
                userRole = user[5]
                if usernam == username and passw == password and userRole == role:
                    return userRole

# get user name
    def getUserName(self,id):
        res_data = self._connection.cursor()
        res_data.execute("SELECT first_name,last_name FROM users WHERE userid = %(ID)s;" , {'ID': id})
        res = res_data.fetchall()
        return res

# get data on class
    def getClassData(self, id):
        res_data = self._connection.cursor()
        res_data.execute("SELECT class_name FROM class WHERE teacher_id = %(ID)s;" , {'ID': id} )
        res = res_data.fetchall()
        return res

# get class of a specific teacher
    def getClassNum(self, id):
        res_data = self._connection.cursor()
        res_data.execute("SELECT count(*) FROM class WHERE teacher_id = %(ID)s;", {'ID': id})
        res = res_data.fetchall()
        return res

# get student information
    def getStudentsD(self, className):
        res_data = self._connection.cursor()
        res_data.execute("SELECT userid , first_name , last_name FROM users WHERE (SELECT count(*) FROM students_in_class WHERE userid=student_id AND class_name=%(CN)s) > 0 ;" , {'CN': className})
        res = res_data.fetchall()
        return res

# get number of students in class
    def getStudentsNum(self, className):
        res_data = self._connection.cursor()
        res_data.execute("SELECT students_num FROM class WHERE class_name=%(CN)s;" , {'CN': className})
        res = res_data.fetchall()
        return res

# get user id
    def userid(self):
        self._user_id = self._userid
        return self._user_id

# create new user
    def createUser(self,id,fn,ln, username, password , role):
        res_data = self._connection.cursor()
        res_data.execute("SELECT * FROM users")
        users = res_data.fetchall()
        sql = "INSERT INTO users (userid, first_name, last_name, username, password, role) VALUES (%s, %s, %s, %s , %s , %s)"
        val = (id, fn, ln, username, password, role)
        res_data.execute(sql, val)
        self._connection.commit()

# create new class
    def createClass(self, className, studentsNum):
        res_data = self._connection.cursor()
        sql = "INSERT INTO class (class_name, students_num, teacher_id) VALUES (%s, %s, %s)"
        val = (className, studentsNum, self._user_id)
        res_data.execute(sql, val)
        self._connection.commit()

#connect between class and students
    def conectStudent(self , studentId , className):
        res_data = self._connection.cursor()
        sql = "INSERT INTO students_in_class (class_name, student_id) VALUES (%(className)s, %(ID)s);"
        val = {'className' : className, 'ID' : studentId}
        res_data.execute(sql, val)
        self._connection.commit()

#create new exercise
    def createExercise(self , file , eqNum , exName , className):
        res_data = self._connection.cursor()
        teacher_ans_list=[]
        eq_list=[]

        res_data.execute("SELECT Count(*) FROM exercise WHERE exercise_name=%(EN)s;",{'EN': exName})
        res = res_data.fetchall()

        if res[0][0] == 0:

            data = pd.read_excel(file)

            sql = "INSERT INTO exercise (equation_num, exercise_name) VALUES (%s, %s)"
            val = (eqNum, exName)
            res_data.execute(sql, val)
            self._connection.commit()

        res_data.execute("SELECT exercise_code FROM exercise WHERE exercise_name=%(EXN)s;" , {'EXN': exName} )
        res1 = res_data.fetchall()


        sql = "INSERT INTO tasks (class_name, teacher_id , exercise_code) VALUES (%s, %s , %s)"
        val = (className, self._user_id , res1[0][0])
        res_data.execute(sql, val)
        self._connection.commit()

        if res[0][0] == 0:
            y = Algorithm()

            for i in range(eqNum):
                val = data.values[i][0]
                eq_list.append(val)


            teacher_ans_list = y.calcAns(eq_list)

            for item in range(eqNum):
                res_data.execute("SELECT count(*) FROM equations WHERE content=%(CONT)s;",
                                 {'CONT': data.values[item][0]})
                res3 = res_data.fetchall()

                if res3[0][0] == 0:

                    sql = "INSERT INTO equations (content , correct_answer) VALUES (%s , %s)"
                    val = (data.values[item][0] , teacher_ans_list[item])
                    res_data.execute(sql, val)
                    self._connection.commit()

                res_data.execute("SELECT equation_code FROM equations WHERE content=%(CONT)s;",
                                 {'CONT': data.values[item][0]})
                res2 = res_data.fetchall()

                sql = "INSERT INTO exercise_equations (exercise_code, equation_code) VALUES (%s, %s)"
                val = (res1[0][0], res2[0][0])
                res_data.execute(sql, val)
                self._connection.commit()

# get number of exercises by name
    def getExerciseNum(self , className):
        res_data = self._connection.cursor()
        res_data.execute("SELECT count(*) FROM tasks WHERE class_name=%(CN)s;",{'CN': className})
        res = res_data.fetchall()
        return res

# get list of exercises of a specipic class
    def getExList(self , className):
        res_data = self._connection.cursor()
        res_data.execute("SELECT E.exercise_name FROM exercise E WHERE (SELECT count(*) FROM tasks T WHERE E.exercise_code=T.exercise_code AND T.class_name=%(CN)s) > 0 ;" , {'CN': className})
        res = res_data.fetchall()
        return res

# get number of equations in exercise
    def getEqNum(self , exName):
        res_data = self._connection.cursor()
        res_data.execute("SELECT equation_num FROM exercise WHERE exercise_name=%(EN)s;",{'EN': exName})
        res = res_data.fetchall()
        return res

# get list of equations in a specipic exercise
    def getEqList(self , exName):
        res_data = self._connection.cursor()
        res_data.execute("SELECT EE.content , EE.correct_answer FROM equations EE inner join exercise EX on EX.exercise_name=%(EN)s WHERE (SELECT count(*) FROM exercise_equations EXEQ WHERE EXEQ.exercise_code=EX.exercise_code And EXEQ.equation_code = EE.equation_code) > 0;" ,{'EN': exName})
        res = res_data.fetchall()
        return res

#get class name by user id
    def getClassName(self , id):
        res_data = self._connection.cursor()
        res_data.execute("SELECT class_name FROM students_in_class WHERE student_id=%(ID)s;", {'ID': id})
        res = res_data.fetchall()
        return res

# insert student solution
    def insertSolution(self ,id,processed_solution, exercise , eq_no , eqCode):
        res_data = self._connection.cursor()

        res_data.execute("SELECT Count(*) FROM student_answer WHERE student_id=%(ID)s AND equation_code=%(EC)s;", {'ID': id , 'EC':eqCode[int(eq_no)-1][0] })
        res = res_data.fetchall()


        if res[0][0] == 0:
            sql = "INSERT INTO student_answer (equation_code, student_id , student_solution) VALUES (%s, %s , %s)"
            val = (eqCode[int(eq_no)-1][0],id, processed_solution)
            res_data.execute(sql, val)
            self._connection.commit()

        else:
            res_data.execute ("UPDATE student_answer SET student_solution=%(SS)s WHERE student_id=%(ID)s AND equation_code=%(EC)s;", {'ID': id,'EC' : eqCode[int(eq_no)-1][0] , 'SS' : processed_solution})
            self._connection.commit()

        return eqCode[int(eq_no)-1][0]

#get equation by equation code
    def getEquation(self, eq_code):
        res_data = self._connection.cursor()

        res_data.execute("SELECT content FROM equations WHERE equation_code=%(EC)s ;",{'EC': eq_code})
        res = res_data.fetchall()
        return res[0][0]

#insert teacher answer to equation at student answer table
    def insertTeacherAns(self , eqNum ,eqCode,id):
        res_data = self._connection.cursor()

        for i in range(eqNum):
            res_data.execute("UPDATE student_answer SA SET SA.teacher_answer=(SELECT E.correct_answer FROM equations E WHERE E.equation_code=%(EC)s) WHERE SA.student_id=%(ID)s AND SA.equation_code=%(EC)s;",{'ID': id, 'EC': eqCode[i][0]})
        self._connection.commit()

#get equation code by exercise
    def getEqCode(self , exercise):
        res_data = self._connection.cursor()

        res_data.execute("SELECT equation_code FROM exercise_equations EE inner join exercise E on exercise_name=%(EN)s WHERE EE.exercise_code=E.exercise_code;",{'EN': exercise})
        eqCode = res_data.fetchall()
        return eqCode

#get teacher answer
    def getTeacherA(self , eq_code):
        res_data = self._connection.cursor()

        tA_list = []

        for i in range(len(eq_code)):
            res_data.execute("SELECT correct_answer FROM equations WHERE equation_code=%(EC)s;",{'EC': eq_code[i][0]})
            teacherA = res_data.fetchall()
            tA_list.append(teacherA)
        return tA_list

#update student answer
    def updateStudentAns(self, id,solution,eC):
        res_data = self._connection.cursor()

        tmp=[]

        y = Algorithm()
        sol_after_split = y.split_student_Sol(solution)
        tmp.append(sol_after_split[len(sol_after_split)-1])
        studentA = y.calcAns(tmp)

        res_data.execute("UPDATE student_answer SA SET SA.student_final_answer=%(AN)s WHERE SA.student_id=%(ID)s AND SA.equation_code=%(EC)s;",
            {'ID': id, 'EC': eC , 'AN' : studentA[0]})
        self._connection.commit()

#get student answer
    def getStudentAns(self,id,exercise ,eq_code):
        res_data = self._connection.cursor()
        studentANSL=[]

        for i in range(len(eq_code)):
            res_data.execute("SELECT student_final_answer FROM student_answer WHERE student_id=%(ID)s AND equation_code=%(EC)s;" ,{'ID' : id , 'EC' : eq_code[i][0]})
            student_ans = res_data.fetchall()
            studentANSL.append(student_ans)

        return studentANSL

#update student answer feedbak
    def updateFeedback(self,id, eC, reply):
        res_data = self._connection.cursor()

        res_data.execute("UPDATE student_answer SA SET SA.error_code=%(ERR)s , SA.feedback=%(F)s , SA.error_row=%(EROW)s WHERE SA.student_id=%(ID)s AND SA.equation_code=%(EC)s;",{'ID': id, 'EC': eC , 'ERR' : reply[0] , 'F' : reply[1] , 'EROW' : reply[2]})
        self._connection.commit()

#get student feedback
    def getStudentFeedback(self,id,exercise ,eq_code):
        res_data = self._connection.cursor()
        studentfeedL=[]

        for i in range(len(eq_code)):
            res_data.execute("SELECT error_row, student_solution, feedback FROM student_answer WHERE student_id=%(ID)s AND equation_code=%(EC)s;" ,{'ID' : id , 'EC' : eq_code[i][0]})
            student_f = res_data.fetchall()
            studentfeedL.append(student_f)

        return studentfeedL

#get student details and feedback details
    def getStudentCardDetails(self , studentid):
        res_data = self._connection.cursor()

        res_data.execute("SELECT E.content , SA.error_code , SA.feedback FROM student_answer SA inner join equations E on SA.equation_code=E.equation_code WHERE SA.student_id=%(ID)s;",{'ID': studentid})
        student_card = res_data.fetchall()

        return student_card

#get true answer of specipic equation
    def getTrueAns(self , class_name , content):
        res_data = self._connection.cursor()
        trueList = []

        for i in range(len(content)):
            res_data.execute("SELECT count(*) FROM student_answer SA inner join students_in_class SIC on SIC.student_id=SA.student_id and SIC.class_name=%(CN)s inner join equations E on E.content=%(C)s WHERE SA.error_code=9 and SA.equation_code=E.equation_code;",{'CN': class_name , 'C':content[i][0]})
            countTrueAns = res_data.fetchall()
            trueList.append(countTrueAns)

        return trueList

#get number of false answer of a specific equation
    def getFalseAns(self, class_name, content):
        res_data = self._connection.cursor()
        falseList = []

        for i in range(len(content)):
            res_data.execute(
                "SELECT count(*) FROM student_answer SA inner join students_in_class SIC on SIC.student_id=SA.student_id and SIC.class_name=%(CN)s inner join equations E on E.content=%(C)s WHERE SA.error_code<>9 and SA.equation_code=E.equation_code;",
                {'CN': class_name, 'C': content[i][0]})
            countFalseAns = res_data.fetchall()
            falseList.append(countFalseAns)

        return falseList

#get most freaquent error message
    def getFrequentErr(self , className, eqList):
        res_data = self._connection.cursor()
        fList = []

        for i in range(len(eqList)):
            res_data.execute(
                "SELECT SA.error_code FROM student_answer SA inner join students_in_class SIC on SIC.student_id=SA.student_id and SIC.class_name=%(CN)s inner join equations E on E.content=%(C)s WHERE SA.error_code<>9 and SA.equation_code=E.equation_code GROUP BY SA.error_code ORDER BY SA.error_code DESC;",
                {'CN': className, 'C': eqList[i][0]})
            countfeAns = res_data.fetchall()
            if countfeAns:
                fList.append(countfeAns[0][0])
            else:
                fList.append(" ")

        return fList

#get equation code list
    def getEqListCode(self, eqList):
        res_data = self._connection.cursor()
        eqCodeList = []

        for i in range(len(eqList)):
            res_data.execute("SELECT equation_code FROM equations WHERE content=%(C)s;",
            {'C': eqList[i][0]})
            eqCode = res_data.fetchall()
            eqCodeList.append(eqCode[0])

        return eqCodeList

#get data by equation
    def getEquationData(self, teacherId , eqCode):
        res_data = self._connection.cursor()

        res_data.execute("SELECT SA.student_id, U.first_name, U.last_name, SA.error_code, SA.feedback FROM student_answer SA inner join class CL on CL.teacher_id = %(ID)s inner join students_in_class SC on SC.class_name = CL.class_name and SC.student_id = SA.student_id inner join users U on U.userid = SA.student_id where SA.equation_code = %(EC)s;",
                         {'EC': eqCode , 'ID' : teacherId})
        eqDataList = res_data.fetchall()

        return eqDataList

#get equation content
    def getEquation(self , eqCode):
        res_data = self._connection.cursor()

        res_data.execute(
            "SELECT content FROM equations WHERE equation_code = %(EC)s;",
            {'EC': eqCode})
        equation = res_data.fetchall()

        return equation

#get list of error code
    def getErrorCodeLst(self , studentId , exName):
        res_data = self._connection.cursor()

        res_data.execute(
            "SELECT NVL(SA.error_code,0), EE.equation_code FROM exercise_equations EE LEFT join student_answer SA on SA.student_id =%(SID)s and SA.equation_code = EE.equation_code inner join exercise EXS on EXS.exercise_name =%(EXN)s where EE.exercise_code = EXS.exercise_code;",
            {'SID': studentId , 'EXN' : exName })
        errLst = res_data.fetchall()

        return errLst




