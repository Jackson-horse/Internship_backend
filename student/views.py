from rest_framework.decorators import permission_classes,api_view
from .permissions import IsAuthenticatedButNotAdmin
from rest_framework.response import Response

from math import sqrt
from statistics import mean
import numpy as np
import pandas as pd
import math
import pandas as pd
from sqlalchemy import create_engine

@api_view(['POST'])
@permission_classes([IsAuthenticatedButNotAdmin])
def course_recommendation(request):
        #'root'不用改，'password'改为自己mysql数据库密码，'localhost‘、'3306'不用改，’studnet‘为数据库名字
    engine = create_engine("mysql+pymysql://{}:{}@{}:{}/{}".format('root', 'mysql123', 'localhost', '3306', 'storefront2'))


    # 1506200067  1306100176
    student = 1506200067            # 要查询的学生学号
    year = 3                        # 学年
    semester = '1'                  # 学期
    num = 7                         # 需要推荐的课程数量



    #fun()函数执行的是获取该学生同专业其他学生的信息
    #所有信息拼接成的一个大表
    def fun(sid):
        sql_query = 'select majorID from student where studentID={}'.format(sid)  # 查询该学生专业号
        df_read = pd.read_sql_query(sql_query, engine)  # 通过Dataframe对象存储查询到的数据，df_read 是个DataFrame对象
        majorID = df_read.values[0][0]                  #获取学生专业号

        #sql_query 为sql查询语句
        sql_query = 'SELECT student.studentID, main_major.majorName, student.enrollSchoolYear, main_enrollment.courseName, ' \
                    'main_enrollment.credit, main_enrollment.score, main_enrollment.score2, main_enrollment.score3, ' \
                    'main_moduleinfo.moduleName, main_moduleinfo.moduleProperty ' \
                    'FROM student ' \
                    'INNER  JOIN  main_major ON student.majorID=main_major.majorID ' \
                    'INNER  JOIN  main_enrollment ON student.studentID=main_enrollment.studentID ' \
                    'INNER  JOIN  main_coursetype ON main_enrollment.courseTypeID=main_coursetype.courseTypeID ' \
                    'INNER  JOIN  main_moduleinfo ON main_coursetype.moduleID=main_moduleinfo.moduleID ' \
                    'where student.majorID={0} and student.studentID <>{1}'.format(majorID,sid)


        df_read = pd.read_sql_query(sql_query, engine)  # 执行查询操作，df_read 是个DataFrame对象

        # print(df_read.dtypes)               #用于查看df_read各列属性的类型
        #df_read(DataFrame对象)列属性名称及说明
        #studentID,  majorName,  enrollSchoolYear,  courseName,  credit
        #学生学号，    学生专业名称， 学生入学年份，       课程名称，      课程学分，
        #
        #score，     score2，     score3，           moduleName，  moduleProperty
        #百分制分数，  重修成绩，    补考成绩，           模块名称，      必修\选修

        return df_read          #返回个DateFrame对象


    #传入学号，查询该学生的成绩信息，返回一个DataFrame对象
    #该对象的内容包括
    #课程ID，      百分制分数，  重修成绩，   补考成绩，   课程类型编号，     模块ID
    #courseID,    score,      score2,    score3,    courseTypeID,   moduleID
    def getFlashmanScore(sid):
        #SQL查询语句
        sql_query = 'SELECT main_course.courseID, main_course.courseName,main_enrollment.score, main_enrollment.score2, ' \
                    'main_enrollment.score3, main_coursetype.courseTypeID,main_coursetype.moduleID ' \
                    'FROM main_enrollment ' \
                    'INNER JOIN main_coursetype ON main_enrollment.courseTypeID=main_coursetype.courseTypeID ' \
                    'INNER JOIN main_course ON main_enrollment.courseID=main_course.courseID ' \
                    'WHERE main_enrollment.studentID={}'.format(sid)

        df_read = pd.read_sql_query(sql_query, engine)  # 执行查询操作，df_read 是个DataFrame对象

        return df_read


    #传入学号，查询与该学生同专业老生的成绩信息，返回一个DataFrame对象
    #该对象的内容包括
    #学生学号，      课程ID，       百分制分数，     重修成绩，      补考成绩
    #studentID，    courseID,     score,         score2,      score3
    def getOldstudentScore(sid):
        #SQL查询语句，查询学号为sid的学生的 专业号 和 入学年份
        sql_query = 'SELECT majorID,enrollSchoolYear FROM student WHERE studentID={}'.format(sid)

        df_read = pd.read_sql_query(sql_query, engine)  # 执行查询操作，df_read 是个DataFrame对象

        majorID = df_read.values[0][0]                  #学号为sid的学生的专业号
        enrollSchoolYear = df_read.values[0][1]         #学号为sid的学生的入学年份

        #SQL查询语句，查询学号为sid的学生同专业的老生的课程信息
        sql_query = 'SELECT main_enrollment.studentID, main_enrollment.courseID, main_enrollment.courseName, main_enrollment.score ' \
                    'FROM main_enrollment ' \
                    'INNER JOIN student ON main_enrollment.studentID=student.studentID ' \
                    'INNER JOIN main_course ON main_enrollment.courseID=main_course.courseID ' \
                    'WHERE student.enrollSchoolYear<{0} and student.majorID={1} and main_enrollment.score is not NULL ' \
                    'ORDER BY main_enrollment.studentID '.format(enrollSchoolYear,majorID)

        df_read = df_read = pd.read_sql_query(sql_query, engine)  # 执行查询操作，df_read 是个DataFrame对象

        return df_read      #返回个DataFrame对象


    #传入学生学号sid，查询该学生专业所开设的所有课程的信息
    #返回一个DataFrame对象，该对象的内容包括
    #课程ID，     课程名称，        课程平均分，      学分，        课程类型编号，      模块编号
    #courseID，   courseName,     avgScore,      credit,     courseTypeID,    moduleID
    def getCourse(sid):
        # SQL查询语句，查询学号为sid的学生的 专业号 和 入学年份
        sql_query = 'SELECT majorID FROM student WHERE studentID={}'.format(sid)
        df_read = pd.read_sql_query(sql_query, engine)  # 执行查询操作，df_read 是个DataFrame对象

        majorID = df_read.values[0][0]          #学生的专业号

        #SQL查询语句，查询学号为sid的学生所在专业的所有课程信息，
        #包括课程：ID，课程名称，课程平均分，学分，课程类型编号，模块编号
        sql_query = 'SELECT main_course.courseID, main_course.courseName, course_score.avgScore, ' \
                    'main_course.credit, main_course.courseTypeID, main_coursetype.moduleID, ' \
                    'main_course.courseYear, main_course.courseSemester ' \
                    'FROM main_course ' \
                    'INNER JOIN main_coursetype ON  main_course.courseTypeID=main_coursetype.courseTypeID ' \
                    'INNER JOIN course_score ON main_course.courseID=course_score.courseID ' \
                    'WHERE main_coursetype.majorID={} '.format(majorID)

        df_read = pd.read_sql_query(sql_query, engine)  # 执行查询操作，df_read 是个DataFrame对象

        return  df_read


    #获取所有课程平均成绩
    def getALLcourseAvgScore():
        # SQL语句查询所有课程总平均分
        sql_query = 'SELECT avgScore FROM course_score WHERE courseID=0'
        df_read = pd.read_sql_query(sql_query, engine)  # 执行查询操作，df_read 是个DataFrame对象

        avgCourse = df_read.values[0][0]  # 所有课程总平均成绩

        return avgCourse

    #-------------------------------------------------------

    # 百分制成绩转五分制绩点
    def fun0(s):
        if s < 60:
            return 0.0
        else:
            return (s*1.0-50.0)/10.0

    #
    # 模块 : 用于统级模块修学情况
    #moduleCourse = {'必修课':{4:['通识类必修课程',34], 2:['学科基础课程',20], 3:['专业必修课程',28], 6:['集中性实践教学环节',29]}, '选修课':{4:['通识类选修课程',11], 5:['专业选修课',38]}}
    moduleCourse = {9:['通识类必修课程',34.0], 2:['学科基础课程',20.0], 3:['专业必修课程',28.0], 6:['集中性实践教学环节',29.0], 4:['通识类选修课程',11.0], 5:['专业选修课',38.0]}

    # 取两个老生
    k = 2

    # 所有课程总的平均成绩 u
    u = getALLcourseAvgScore()

    # 读入新生课程成绩
    # courseID   courseName  score score2 score3  courseTypeID  moduleID
    juniorStudentCourse = getFlashmanScore(student)

    # 记录新生修过的课程
    juniorStudentCourseS = set()

    # 计算新生平均分
    MeanRs0 = np.array(list(np.array(list(juniorStudentCourse.values)).T[2])).mean()

    # 读入老生信息，存data
    # studentID  courseID    courseName  score
    seniorData = getOldstudentScore(student)

    # 读入新生专业的所有课程
    # courseID   courseName  avgScore  credit  courseTypeID  moduleID  courseYear courseSemester
    coursesOfJuniorStudent = getCourse(student)

    # 每门课程与其学分 ：用于统级模块修学情况
    # 课程：学分
    courseAndCredit = dict()

    # 需要推荐的学期的课程
    courseNeeded = dict()

    # 课程平均成绩 courseNAme : avgScore
    MeanScoreOfCourses = dict()

    # 找courseNeeded 和 courseAndCredit
    # 用于后面错误检测
    courseAndCreditS = set()
    for i in range(len(coursesOfJuniorStudent)):
        # print(type(coursesOfJuniorStudent['courseSemester'][i]))
        if coursesOfJuniorStudent['moduleID'][i] == 5 and coursesOfJuniorStudent['courseYear'][i] == year and coursesOfJuniorStudent['courseSemester'][i] == semester:
            courseNeeded[coursesOfJuniorStudent['courseName'][i]] = 100
            MeanScoreOfCourses[coursesOfJuniorStudent['courseName'][i]] = coursesOfJuniorStudent['avgScore'][i]
            
        if math.isnan(coursesOfJuniorStudent['credit'][i]):
            continue
        courseAndCredit[coursesOfJuniorStudent['courseName'][i]] = coursesOfJuniorStudent['credit'][i]
        courseAndCreditS.add(coursesOfJuniorStudent['courseName'][i])


    # 在这里找 juniorStudentCourseS
    # 统级模块修学情况、计算GPA和挂科数目
    gradePoint = 0
    numberOfFailedCourse = 0
    course_13_cc = dict()
        
    for i in range(len(juniorStudentCourse)):
        if juniorStudentCourse['score'][i] <= 0:
            continue

        juniorStudentCourseS.add(juniorStudentCourse['courseName'][i])

        course_13_cc[juniorStudentCourse['courseName'][i]] = juniorStudentCourse['score'][i]

        if juniorStudentCourse['courseName'][i] in courseAndCreditS:
            moduleCourse[juniorStudentCourse['moduleID'][i]][1] -= courseAndCredit[juniorStudentCourse['courseName'][i]]
        gradePoint += fun0(juniorStudentCourse['score'][i])
        if juniorStudentCourse['score'][i] < 60:
            numberOfFailedCourse += 1
    GPA = gradePoint / len(juniorStudentCourse)

    # 存相似度与老生学号的tuple
    DictOfSIM = dict() 

    # studentID  courseID  score
    stuNum = seniorData['studentID'][0]

    # 逐个老生课程成绩
    stuCourseScord = dict()
    ii = 0
    count = 0
    while ii < len(seniorData):
        if ii < len(seniorData)-2:
            stuNum = seniorData['studentID'][ii]
        else:
            break
        stuCourseScord.clear() 

        # 逐个老生提取成绩
        while ii < len(seniorData) and seniorData['studentID'][ii] == stuNum:
            stuCourseScord[seniorData['courseName'][ii]] = seniorData['score'][ii]
            ii = ii + 1

        # 计算老生平均分
        MeanRs1 = np.array(list(stuCourseScord.values())).mean()

        # 取交集
        CourseOfBoth = set(stuCourseScord.keys()) & juniorStudentCourseS  # set一个集合
        if len(CourseOfBoth)==0:
            continue
        CourseOfBothL = list(CourseOfBoth)

        fenzi = 0.0
        fenmu0 = 0.0
        fenmu1 = 0.0
        s0 = 0.0
        s1 = 0.0

        # 算相似度
        for j in range(len(CourseOfBothL)):
            s0 = course_13_cc[CourseOfBothL[j]]*1.0 - MeanRs0 *1.0
            s1 = stuCourseScord[CourseOfBothL[j]]*1.0 - MeanRs1*1.0 
            fenzi += s0 * s1
            fenmu0 += s0 * s0
            fenmu1 += s1 * s1
        SIM = fenzi / (sqrt(fenmu0) * sqrt(fenmu1))
        # 存 老生学号：[SIM，老生平均成绩]
        DictOfSIM[stuNum]=[SIM, MeanRs1]
    # print(count)

    # studentID  courseID    courseName  score
    # 计算每门课程的预期成绩
    senior = list()
    senior0 = list()
    courseNeeded0 = dict()

    for item in courseNeeded.items():   # item 是一个tuple
        senior.clear()
        senior0.clear()

        # 在老生数据 seniorData 中找修过这门课程的老生
        for j in range(len(seniorData)):
            if seniorData['courseName'][j]==item[0]:
                senior.append([seniorData['studentID'][j],seniorData['score'][j]])

        # 存在没有老生修过的课程  
        if len(senior) == 0:
            continue
        # senior存着修过这门课的老生的  学号 老生这门课的成绩

        # SIMandMeanscore :  SIM, 老生平均成绩，老生这门课成绩
        for j in range(len(senior)):
            # 根据学生学号找 相似度及平均分
            SIMandMeanscore = list()

            # 根据学号找 [SIM, 老生平均成绩]
            SIMandMeanscore = DictOfSIM[senior[j][0]].copy()

            # 添加成 [SIM, 老生平均成绩，老生这门课的成绩]
            SIMandMeanscore.append(senior[j][1])

            senior0.append(SIMandMeanscore)
        
        senior0 = sorted(senior0, key = (lambda x: [x[0]]), reverse=True)

        Fenzi = 0
        Fenmu = 0
        # Fenzi += 相似度 * （老生这门课程的成绩 - （老生所有课程的平均成绩+这门课程平均成绩-u)
        kk = min(k,len(senior0))
        for j in range(kk):
            Fenzi += senior0[j][0] * (senior0[j][2] - (senior0[j][1] + MeanScoreOfCourses[item[0]] - u))
            Fenmu += senior0[j][0] 
        ss = MeanRs0 + MeanScoreOfCourses[item[0]] - u + Fenzi / Fenmu

        if ss <= 100:
            courseNeeded0[item[0]] = ss
        

    # 按预测分数排序
    courseNeeded0 = sorted(courseNeeded0.items(), key=lambda x: x[1], reverse=True)

    # 平均分 MeanRs0
    # 平均绩点 GPA
    # 挂科数目 numberOfFailedCourse
    # 模块未修情况 moduleCourse
    # 推荐课程 courseNeeded0 （可以从中选择几门）

    # semeter 是 str
    # 算出预测分数高于100
    # courseNeeded0 排序输出最高几个

    return_data = {}
    return_data['MeanRs0']=MeanRs0
    return_data['GPA']=GPA
    return_data['numberOfFailedCourse']=numberOfFailedCourse
    return_data['moduleCourse']=moduleCourse
    return_data['courseNeeded0']=courseNeeded0


    return Response(return_data)

