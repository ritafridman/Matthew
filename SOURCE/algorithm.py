import operator

from sympy import Eq, Symbol, solve, sympify
import re
from  builtins import any as b_any






class Algorithm:

#calculate answer of an equation
    def calcAns(self , eqList):

        teacher_ans_list=[]
        for i in range(len(eqList)):
            try:

                ans = self.calcAnswer(eqList[i])

                teacher_ans_list.append(ans)
            except:
                teacher_ans_list.append(0)

        return teacher_ans_list


#get diffrence between two lists
    def list_diff(self, list1, list2):
        return (list(set(list1) - set(list2)))


#check if student input is valid
    def checkInput(self , solution_lines):
        lstErr = []

        if len(solution_lines) == 0:
            lstErr.append('0')
            lstErr.append(" ")
            lstErr.append('0')
            return lstErr

        error_code = 0
        massage_error = ''


        for j in range(len(solution_lines)):
            strForCheck = solution_lines[j]

            newStr = ''
            isChange = 0
            newInd = 0

            for i in range(len(strForCheck)):
                if strForCheck[i] == ' ':
                    isChange = 1
                    continue

                if newInd == 0:
                    newStr = newStr + strForCheck[i]
                    newInd = newInd + 1
                    continue


                if (newStr[newInd - 1] == 'x'
                        and ((strForCheck[i] >= '0'
                              and strForCheck[i] <= '9')
                             or strForCheck[i] == '(')):
                    newStr = newStr + '*'
                    isChange = 1
                    newInd = newInd + 1

                if (strForCheck[i] == 'x'
                        and ((newStr[newInd - 1] >= '0'
                              and newStr[i - 1] <= '9')
                             or newStr[newInd - 1] == ')')):
                    newStr = newStr + '*'
                    isChange = 1
                    newInd = newInd + 1

                if (newStr[newInd - 1] == ')'
                        and (strForCheck[i] >= '0'
                              and strForCheck[i] <= '9')):
                    newStr = newStr + '*'
                    isChange = 1
                    newInd = newInd + 1

                if (strForCheck[i] == '('
                        and (newStr[newInd - 1] >= '0'
                              and newStr[i - 1] <= '9')):
                    newStr = newStr + '*'
                    isChange = 1
                    newInd = newInd + 1

                newStr = newStr + strForCheck[i]
                newInd = newInd + 1

            if isChange == 1:
                solution_lines[j] = newStr
                strForCheck = newStr


            for k in range(len(strForCheck)):
                if not (strForCheck[k] == '+'
                        or strForCheck[k] == '-'
                        or strForCheck[k] == ')'
                        or strForCheck[k] == '('
                        or strForCheck[k] == '*'
                        or strForCheck[k] == '/'
                        or strForCheck[k] == '='
                        or strForCheck[k] == 'x'
                        or (strForCheck[k] >= '0'
                            and strForCheck[k] <= '9')):
                    error_code=8
                    massage_error="שגיאה בהעתקה: " + "\r\n" +"שים לב לתו : "
                    massage_error= massage_error + strForCheck[k]
                    lstErr.append(error_code)
                    lstErr.append(massage_error)
                    lstErr.append(j + 1)
                    return lstErr

                if k > 0:
                    if ((strForCheck[k] == '*'
                         or strForCheck[k] == '+'
                         or strForCheck[k] == '-'
                         or strForCheck[k] == '/')
                            and (not ((strForCheck[k-1] <= '9'
                                       and strForCheck[k-1] >= '0')
                                      or strForCheck[k-1] == 'x'
                                      or strForCheck[k-1] == '='
                                      or strForCheck[k-1] == ')'))):
                        error_code = 8;
                        massage_error="שגיאה בהעתקה: " + "\r\n" +"שים לב לתווים : "
                        massage_error = massage_error + strForCheck[k-1:k]
                        lstErr.append(error_code)
                        lstErr.append(massage_error)
                        lstErr.append(j + 1)
                        return lstErr


            if strForCheck.count('(') != strForCheck.count(')'):
                error_code = 8;
                massage_error = "שגיאה בהעתקה: " + "\r\n" + "אין התאמה בסימנים: '()' "
                lstErr.append(error_code)
                lstErr.append(massage_error)
                lstErr.append(j + 1)
                return lstErr


            if strForCheck.count('=') > 1:
                error_code = 8;
                massage_error = "שגיאה בהעתקה: " + "\r\n" + "יש סימן מיותר: '=' "
                lstErr.append(error_code)
                lstErr.append(massage_error)
                lstErr.append(j + 1)
                return lstErr


        lastStrForCheck = solution_lines[(len(solution_lines))-1]

        if (lastStrForCheck.rfind('*') >= 0 or
                lastStrForCheck.rfind('+') >= 0 or
                lastStrForCheck.rfind('(') >= 0 or
                lastStrForCheck.rfind(')') >= 0):
            error_code  =7
        elif (lastStrForCheck[1:]).rfind('-') > 0:
            if not(lastStrForCheck[0:3] == 'x=-'):
                   error_code = 7
            elif (lastStrForCheck[3:]).rfind('-') >= 0:
                error_code = 7

        elif lastStrForCheck[0] == '-':
            if (lastStrForCheck[1:]).rfind >= 0:
                error_code = 7

        if error_code == 7:
            massage_error = "משוואה לא פתורה עד הסוף"
            lstErr.append(error_code)
            lstErr.append(massage_error)
            lstErr.append((len(solution_lines)-1))
            return lstErr

        lstErr.append('0')
        lstErr.append(" ")
        lstErr.append('0')
        return lstErr


# get conclution about stident solution
    def getConclusion(self, solution, equation):

        answer = self.calcAnswer(equation)
        sol_after_split = self.split_student_Sol(solution)
        wrong_lines = []
        mistake = []
        newM = ''
        iserr = 0

        list_error = self.checkInput(sol_after_split)
        if int(list_error[0]) > 0:
            return list_error

        last_answer = self.calcAnswer(sol_after_split[(len(sol_after_split))-1])
        for item in range(len(sol_after_split)):
            i_answer = self.calcAnswer(sol_after_split[item])
            if answer == i_answer:
                continue
            else:
                if item == 0:
                    wrong_lines.append(equation)
                else:
                    wrong_lines.append(sol_after_split[item - 1])

                wrong_lines.append(sol_after_split[item])
                mistake = self.explore_mistake(wrong_lines[0], wrong_lines[1])
                mistake.append(item+1)

                if last_answer == answer:
                    mistake[0] = 10
                    newM = "התשובה הסופית תקינה אבל בדרך הפתרון יש שגיאה:" + "\r\n"
                    newM = newM + mistake[1]
                    mistake[1] = newM
                    mistake[2] = item+1
                    iserr=1
                return mistake
                break

        if iserr == 0:
            trueL=['9' ,'תשובה נכונה!' , '0']
            return trueL


#split student solution to rows
    def split_student_Sol(self, solution):

        sol_after_split = solution.splitlines()
        return sol_after_split


#calculate the answer of a specipic equation
    def calcAnswer(self, equation):
        ans_after_split = equation.split(sep='=', maxsplit=2)
        x = Symbol('x')
        eqn = Eq(sympify(ans_after_split[0]), sympify(ans_after_split[1]))
        final_ans = solve(eqn)
        return sympify(float(final_ans[0]))


#split string to elements
    def split_sting(self, str_L):
        flagB = 0
        flagC = 0
        flagE = 0
        flagCstart = 0
        temp = ''
        finalL = []
        tmps = ''

        newStr = str(str_L)


        for i in range(len(newStr)):
            if newStr[i] == ' ':
                continue

            tmps = newStr[i]

            if flagCstart == 1:
                flagCstart = 0
                if tmps != '-':
                    temp = temp + '-'
                else:
                    continue



            if flagC == 1 and flagB == 0:
                if tmps == '+':
                    tmps = '-'
                elif tmps == '-':
                    tmps = '+'

            if tmps == '(':
                flagB = 1

            if tmps == '=':
                flagC = 1
                flagCstart = 1
                flagE = 1

            if tmps == '+' or tmps == '-':
                if flagB == 0:
                    flagE = 1

            if tmps == ')':
                flagB = 0

            if flagE == 1:
                if temp:
                    finalL.append(temp)
                temp = ''
                flagE = 0

                if tmps == '-':
                    temp = '-'
            else:
                temp = temp + tmps

        finalL.append(temp)
        return finalL


#routine that check if their is mistake in the solution
    def explore_mistake(self , truLine , wrongLine):

        bFlag_i=0
        bFlag_w=0
        p=' '
        s=''

        wrong=self.split_sting(wrongLine)
        indication = self.split_sting(truLine)



        fWrong=self.list_diff(wrong,indication)
        fIndication=self.list_diff(indication,wrong)


        finalList = self.checkMethod(fIndication , fWrong)


        return finalList


#change existing list into list of absolute values
    def absoluteVal(self, checkList):
        tmpList = []
        tmpStr = ''

        for i in range(len(checkList)):
            tmpStr = str(checkList[i])
            if tmpStr[0] == '-':
                tmpStr = tmpStr[1:]
            tmpList.append(tmpStr)
        return tmpList


#find wing transfare error
    def wingsTransfer(self, indicationLine, wrongLine):
        errorCode = 0
        msgError = ''
        lstError = []

        if len(indicationLine) == len(wrongLine):
            tmpList_i = ''
            tmpList_w = ''
            tmpList_i = self.absoluteVal(indicationLine)
            tmpList_w = self.absoluteVal(wrongLine)

            tmpDef = self.list_diff(tmpList_i,tmpList_w)
            if not tmpDef:
                errorCode = 1
                msgError = "שים לב להעברת אגפים "
                lstError.append(errorCode)
                lstError.append(msgError)
                return lstError

        lstError.append(errorCode)
        lstError.append(msgError)
        return lstError


#calc specific operator in a phrase
    def manageList(self, tmpList , codeT , codeS):
        tmpStr = ''
        listT = []
        tmpCh = ''

        if codeT == 1:
            tmpCh = '*'

        if codeT ==2:
            tmpCh = '/'

        if codeT ==3:
            tmpCh = '('

        for i in range(len(tmpList)):
            if str(tmpList[i]).rfind('(') >= 0 :
                if codeS == 0:
                    listT.append(tmpList[i])
                    continue

            elif str(tmpList[i]).rfind(tmpCh) < 0:
                listT.append(tmpList[i])
                continue

            tmpStr = sympify(tmpList[i])
            listT.append(tmpStr)

        return listT


#find barcket error
    def barCheck(self, listIndication , listWrong):
        error_code = 0
        massageErr = ''
        lstErr = []
        msg = ''
        countErr = 0


        for i in range(len(listIndication)):
            if str(listIndication[i]).rfind('(') < 0:
                continue

            tmpS = sympify(listIndication[i])
            tmpLst = self.split_sting(tmpS)



            for j in range(len(tmpLst)):
                isE = 1

                for k in range(len(listWrong)):
                    if tmpLst[j] == listWrong[k]:
                        isE = 0
                        break

                if isE == 1:
                    countErr +=1
                    error_code=3

                    if countErr > 1:
                        msg = msg + '|'

                    msg = msg+str(listIndication[i])


        if error_code == 3:
            massageErr = "שים לב לפתיחת סוגריים "

            if countErr > 1:
                massageErr = " טעויות בפתיחת סוגריים " + countErr + "יש "

            massageErr = massageErr + msg

        lstErr.append(error_code)
        lstErr.append(massageErr)
        return lstErr


#find multiplication or divition error
    def mulCheck(self, listIndication , listWrong):
        error_code = 0
        massageErr = ''
        lstErr = []
        msg = ''
        countErr = 0
        isM = 0
        isD = 0

        for i in range(len(listIndication)):
            countM = 0
            countD = 0

            if str(listIndication[i]).rfind('(') >= 0:
                continue

            if str(listIndication[i]).count('*') > 0:
                isM = 1
                countM = 1

            if str(listIndication[i]).count('/') > 0:
                isD = 1
                countD = 1

            if countD == 0 and countM == 0:
                continue


            tmpS = sympify(listIndication[i])
            isE = 1

            for j in range(len(listWrong)):
                if listWrong[j] == tmpS:
                    isE = 0
                    break

            if isE ==1:
                countErr +=1
                error_code = 2

                if countErr > 1:
                    msg = msg + '|'

                msg = msg + str(listIndication[i])

        msg2 = ''
        if isM == 1 and isD == 1:
            msg2 = "כפל וחילוק "

        elif isM == 0:
            msg2 = "חילוק "

        else:
            msg2 = "כפל "


        if error_code == 2:
            massageErr = msg2 + "שים לב ל"

            if countErr > 1:
                massageErr = msg2 + " טעויות ב" + str(countErr) + "יש "

            massageErr = massageErr + msg


        lstErr.append(error_code)
        lstErr.append(massageErr)
        return lstErr


#fins plus or Subtraction error
    def checkPlusSub(self , listIndication , listWrong):
        lstErr = []

        massageErr = "שים לב לחיבור/חיסור "
        error_code = 4

        lstErr.append(error_code)
        lstErr.append(massageErr)
        return lstErr


#calculate the number of operators
    def countOp(self , lst):

        checkStr = ''
        lstF = []

        for i in range(len(lst)):
            checkStr = checkStr+str(lst[i])


        lstF.append(checkStr.count('*'))
        lstF.append(checkStr.count('/'))
        lstF.append(checkStr.count('('))

        countP = checkStr.count('+')
        countS = checkStr.count('-')
        psSum = countP+countS

        lstF.append(psSum)

        return lstF


#manage the search of the error
    def checkMethod(self , listIndication , listWrong):

        lai = self.countOp(listIndication)
        actionsMI = lai[0]
        actionsDI = lai[1]
        actionsSI = lai[2]
        actionsAI = lai[3]

        lai = self.countOp(listWrong)
        actionsMW = lai[0]
        actionsDW = lai[1]
        actionsSW = lai[2]
        actionsAW = lai[3]


        if actionsMI > actionsMW:
            wrongT = self.manageList(listWrong,1,0)
            lstEM = self.mulCheck(listIndication , wrongT)

            if lstEM[0] > 0:
                return lstEM

        else:
            wrongT = listWrong

        indicationT = self.manageList(listIndication,1,0)
        wrong2=self.list_diff(wrongT,indicationT)
        indication2 = self.list_diff(indicationT,wrongT)

        if actionsSI > actionsSW:
            wrongTS = self.manageList(wrong2,3,1)
            lstES=self.barCheck(indication2,wrongTS)

            if lstES[0] > 0:
                return lstES

        else:
            wrongTS = wrong2

        indicationTS = self.manageList(indication2,3,1)
        wrong3 = self.list_diff(wrongTS,indicationTS)
        indiciation3 = self.list_diff(indicationTS,wrongTS)

        lstEA = self.wingsTransfer(indiciation3 , wrong3)

        if lstEA[0] > 0:
            return lstEA


        countOp = 0
        msg = "שגיאה בנסיון לשלב מספר פעולות בפתרון "
        if actionsMI > actionsMW:
            msg = msg + " כפל "
            countOp = countOp + 1

        if actionsDI > actionsDW:
            msg = msg + "חילוק "
            countOp = countOp + 1

        if actionsSI > actionsSW:
            msg = msg + "פתיחת סוגריים"
            countOp = countOp +1

        if actionsAI > actionsAW:
            msg = msg + "חיבור חיסור "
            countOp = countOp + 1

        msg = msg + "יש לפתור מפורט יותר "

        if countOp > 1:
            listError = ('5' , msg)
            return listError



        lstEC = self.checkPlusSub(indiciation3,wrong3)

        if lstEC[0] > 0:
            return lstEC

        errC = 6
        msgC= "לא ניתן לסמן שגיאה"

        lstEW=[]

        lstEW.append(errC)
        lstEW.append(msgC)
        return lstEW






















