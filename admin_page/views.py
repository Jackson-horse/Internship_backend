from rest_framework.decorators import permission_classes,api_view
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from drf_vue_proj.settings import CSV_FILE_DIR

import os
import pandas as pd
from sqlalchemy import create_engine
import numpy as np
import pymysql


@api_view(['POST'])
@permission_classes([IsAdminUser])
def update_database(request):
    csv_file_path = os.path.join(CSV_FILE_DIR,'update_database.csv')
    if os.path.exists(csv_file_path):
        os.remove(csv_file_path)
    # receive csv file from frontend
    if request.method == 'POST':
        csv = request.FILES.get('csv_file')
        with open(csv_file_path, 'wb+') as destination:
            for content in csv.chunks():
                destination.write(content)
        # get students' number and add them into User database, password = student number

        password='mysql123'
        database_name='storefront2'
        engine = create_engine("mysql+pymysql://{}:{}@{}:{}/{}".format('root', password, 'localhost', '3306', database_name))

        #读取excel表中数据写入数据表raw_data
        def ReadExcel(csv_file):
            sidSet = set()  # student表已存在的studentID记录集合
            # SQL查询student表中已存在的studentID
            sql_query = 'select distinct studentID ' \
                        'from student '
            df_sid = pd.read_sql_query(sql_query, engine)  # 执行查询操作，df_read 是个DataFrame对象
            for i in range(len(df_sid)):
                sidSet.add(df_sid.values[i][0])

            #读excel表
            df_read = pd.read_csv(csv_file)
            #设置pd对象列属性名
            df_read.columns=['studentID','gender','major','className','year','semester',
                            'enrollID','courseName','credit','scoreRaw','score','gradePoint',
                            'score2','score3','moduleName']
            #SQL连接
            conn = pymysql.connect(host='127.0.0.1', port=3306, database='student', user='root',
                                password='tan123456', charset='utf8')
            #SQL语句清空raw_data数据表
            sql_query = 'truncate table raw_temp'
            cs1 = conn.cursor()
            cs1.execute(sql_query)
            conn.commit()
            cs1.close()
            conn.close()        #关闭连接

            #写回数据库
            df_read.to_sql(name='raw_temp', con=engine, if_exists='append', index=False)  # 更新course_score表

        #修改main_enrollment表
        def WriteToEnrollment():
            planID = 13     #培养方案名称
            #SQL查询语句，从新添加的raw_data原始数据及与现有的课程表等表拼接中获取数据(关于enrollment表的那部分)
            sql_query = 'SELECT	 main_course.courseID, main_course.courseCode, raw_temp.courseName, ' \
                        'raw_temp.credit, main_course.courseYear, main_course.courseSemester, ' \
                        'main_coursetype.courseTypeID, raw_temp.studentID, raw_temp.enrollID, ' \
                        'raw_temp.score, raw_temp.score2, raw_temp.score3  ' \
                        'FROM 		 raw_temp   ' \
                        'INNER JOIN main_major on raw_temp.major=main_major.majorName  ' \
                        'INNER JOIN main_course ON raw_temp.courseName=main_course.courseName    ' \
                        'INNER JOIN main_coursetype ON main_course.courseTypeID=main_coursetype.courseTypeID  ' \
                        'where main_coursetype.planID={} AND main_major.majorID=main_coursetype.majorID '.format(planID)

            df_read = pd.read_sql_query(sql_query, engine)  # 执行查询操作，df_read 是个DataFrame对象

            df_read.to_sql(name='enrollment_temp', con=engine, if_exists='append', index=False)  # 往enrollment表追加记录

        #修改student表
        def WriteToStudent():
            #SQL查询语句，从raw_data原始数据表及major表中读取student相关属性数据
            sql_query = 'SELECT DISTINCT raw_temp.studentID, raw_temp.gender, main_major.majorID, raw_temp.className ' \
                        'FROM raw_temp ' \
                        'INNER JOIN main_major on raw_temp.major=main_major.majorName'

            df_read = pd.read_sql_query(sql_query, engine)  # 执行查询操作，df_read 是个DataFrame对象
            gradeList = list()              #存储新添加学生的入学年信息
            MOD = 100000000
            for i in range(len(df_read)):
                grade = int(df_read.values[i][0]/MOD)+2000;
                gradeList.append(grade)
            #往df_read中添加属性列----enrollSchoolYear
            df_read.insert(loc=4,column='enrollSchoolYear',value=gradeList)
            #往df_read中添加属性列------planID,默认设为13
            df_read.loc[:, 'planID'] = 13


            sidSet = set()              #student表已存在的studentID记录集合
            #SQL查询student表中已存在的studentID
            sql_query = 'select distinct studentID ' \
                        'from student_temp '
            df_sid = pd.read_sql_query(sql_query, engine)  # 执行查询操作，df_read 是个DataFrame对象
            for i in range(len(df_sid)):
                sidSet.add(df_sid.values[i][0])

            #df_temp存储需要更新的student数据
            df_temp = df_read.iloc[:0]
            for i in range(len(df_read)):
                if df_read.values[i][0] in sidSet:              #如果表中已有记录，则跳过
                    continue
                else:                                           #student表中没有该记录表明这是个新生，需要更新student表
                    df_temp = df_temp.append(df_read.iloc[i], ignore_index=True)
                    sidSet.add(df_read.values[i][0])


            #往student表中追加记录
            df_temp.to_sql(name='student_temp', con=engine, if_exists='append', index=False)  # 往enrollment表追加记录

        #更新student表中学生的平均成绩avgScore
        def UpdateAvgScore():
            #SQL查询语句，查询所有学生的学生id和该学生所有课程的平均成绩
            sql_query = 'SELECT studentID, AVG(score) ' \
                        'FROM enrollment_temp ' \
                        'group BY studentID '

            df_read = pd.read_sql_query(sql_query, engine)  # 执行查询操作，df_read 是个DataFrame对象
            sidList = list()                    #存储学生id的列表
            avgScoreList = list()               #存储学生平均成绩的列表
            for i in range(len(df_read)):
                sidList.append(int(df_read.values[i][0]))
                avgScoreList.append(df_read.values[i][1])
            length = len(sidList)
            #mysql数据库连接
            conn = pymysql.connect(host='127.0.0.1', port=3306, database='student', user='root',
                                password='tan123456', charset='utf8')
            #更新student表中的avgScore列
            for i in range(length):
                sid = sidList[i]                    #学生学号
                avgScore = avgScoreList[i]          #学生平均成绩
                #SQL更新语句
                sql_query = 'UPDATE student_temp ' \
                            'SET avgScore={0} ' \
                            'WHERE studentID={1} '.format(avgScore,sid)
                cs1 = conn.cursor()
                cs1.execute(sql_query)
                conn.commit()
                cs1.close()
            conn.close()            #数据连接关闭

        #更新student表中学生成绩排名
        def UpdateRank():
            #SQL查询major表中的专业号
            sql_query = 'SELECT DISTINCT majorID ' \
                        'FROM main_major '
            df_read = pd.read_sql_query(sql_query, engine)  # 执行查询操作，df_read 是个DataFrame对象
            listOfmajorID = list()                          #获取专业号列表
            for i in range(len(df_read)):
                listOfmajorID.append(df_read.values[i][0])

            #SQL查询学生入学年集合
            sql_query = 'SELECT DISTINCT enrollSchoolYear ' \
                        'FROM student_temp '
            df_read = pd.read_sql_query(sql_query, engine)  # 执行查询操作，df_read 是个DataFrame对象
            listOfGrade = list()                             # 获取年级列表
            for i in range(len(df_read)):
                listOfGrade.append(df_read.values[i][0])

            #递归更新学生年级专业成绩排名
            for grade in listOfGrade:
                for majorID in listOfmajorID:
                    #SQL查询 年级为grade，专业号为majorID的所有学生
                    sql_query = 'SELECT studentID,avgScore ' \
                                'FROM student_temp ' \
                                'WHERE enrollSchoolYear={0} and majorID={1} ' \
                                'ORDER BY avgScore DESC '.format(grade, majorID)
                    df_read = pd.read_sql_query(sql_query, engine)  # 执行查询操作，df_read 是个DataFrame对象
                    sidToScore = df_read.values                     #将DateFrame对象转为numpy对象
                    length = len(sidToScore)                        #保存年级为grade、专业号为majorID的学生人数

                    #数据库连接
                    conn = pymysql.connect(host='127.0.0.1', port=3306, database='student', user='root',
                                        password='tan123456', charset='utf8')
                    #更新年级为grade、专业号为majorID所有学生的Rank排名
                    for i in range(length):
                        rank = i + 1;
                        sid = sidToScore[i][0]
                        sql_query = 'UPDATE student_temp ' \
                                    'SET majorRank={0} ' \
                                    'WHERE studentID={1} '.format(rank, sid)
                        cs1 = conn.cursor()
                        cs1.execute(sql_query)
                        conn.commit()
                        cs1.close()
                    conn.close()    #关闭数据库连接

        #更新课程平均成绩
        def CountAvgscoreOfCourse():
            #SQL查询所有课程的平均成绩
            sql_query = 'SELECT AVG(score) ' \
                        'from enrollment_temp '
            df_temp = pd.read_sql_query(sql_query, engine)  # 执行查询操作，df_read 是个DataFrame对象

            #SQL查询所有课程的总平均成绩
            sql_query = 'SELECT courseID, AVG(score) ' \
                        'FROM enrollment_temp ' \
                        'GROUP BY courseID '
            df_read = pd.read_sql_query(sql_query, engine)  # 执行查询操作，df_read 是个DataFrame对象

            #将df_read与df_temp拼接起来
            df_read.loc[len(df_read)] = [0,df_temp.values[0][0]]
            #数据处理工程中类型发生了改动，将数据类型给该回来
            df_read = df_read.astype({"courseID": int, "AVG(score)": float})
            #写回数据表course_score
            df_read.to_sql(name='course_score_temp', con=engine, if_exists='replace', index=False)  # 更新course_score表

        #获取与学号为sid同年级同专业的学生人数
        def getNumber(sid):
            #SQL查询语句，查找学号为sid的同学的专业号和年级
            sql_query = 'select majorID, enrollSchoolYear ' \
                        'from student ' \
                        'where studentID={0} '.format(sid)
            df_read = pd.read_sql_query(sql_query, engine)  # 执行查询操作，df_read 是个DataFrame对象
            majorID = df_read.values[0][0]          #获取专业号
            grade = df_read.values[0][1]             #获取年级
            #SQL查询语句，查询年级为grade、学号为majorID的学生人数
            sql_query = 'SELECT count(studentID) ' \
                        'FROM student ' \
                        'WHERE majorID={0} AND enrollSchoolYear={1} '.format(majorID,grade)
            df_read = pd.read_sql_query(sql_query, engine)  # 执行查询操作，df_read 是个DataFrame对象
            number = df_read.values[0][0]           #目标人数
            return number                   #返回待求人数

        ReadExcel(csv_file_path)
        WriteToEnrollment()
        WriteToStudent()
        UpdateAvgScore()
        UpdateRank()
        CountAvgscoreOfCourse()
                # json.dumps包装数据
    return Response("ok")