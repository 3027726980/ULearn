import json
from function import format_timestamp_ms,format_remaining_time

# 搜索课程
def searchCourse(courseID):
    if courseID == '':
        print('请输入课程ID')
        return
    else:
        # 获取课程信息
        with open('coursesList.json', 'r', encoding='utf-8') as f:
            courseList = json.load(f).get('courseList',None)
            if courseList is None:
                print('课程列表为空')
                return
            for course in courseList:
                if course['id'] == courseID:
                    print()
                    print(f'课程名称:{course['name']}')
                    print(f'课程ID:{course['id']}')
                    print(f'任课老师:{course['teacherName']}')
                    print(f'班级名称:{course['className']}')
                    print()
                    return
            print('课程不存在')
            return
    return

# 获取所有课程
def getAllCourses():
    with open('coursesList.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
        courseList = data.get('courseList', None)
        courseNum = data.get('total', 0)
        if courseList is None:
            print('课程列表为空')
            return
        for course in courseList:
            print(f'课程名称:{course['name']}')
            print(f'课程ID:{course['id']}')
            print(f'任课老师:{course['teacherName']}')
            print(f'班级名称:{course['className']}')
            print()
        print(f'共有{courseNum}门课程')
    return

# 通过课程ID获取所有作业列表
def getHomeworkList(courseId):
    path = f'HomeworkList/{courseId}_HomeworkList.json'
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        if data is None:
            print('作业列表为空')
            return
        homeworkList = data.get('homeworkList')
        if homeworkList is None:
            print('作业列表为空')
            return
        for homework in homeworkList:
            print(f'作业名称:{homework['homeworkTitle']}')
            print(f'作业ID:{homework['id']}')
            print(f'发布人:{homework['publisher']}')
            print(f'开始时间:{format_timestamp_ms(homework['startTime'])}')
            print(f'结束时间:{format_timestamp_ms(homework['endTime'])}')

            if homework['personStatus'] == 0:
                print(f'作业状态:未提交')
            elif homework['personStatus'] == 1:
                print(f'作业状态:已提交')
            else:
                print(f'作业状态:已截止')

            if homework['timeStatus'] == 0:
                print(f'时间状态:未开始')
            elif homework['timeStatus'] == 1:
                print(f'时间状态:进行中')
                print(f'剩余时间:{format_timestamp_ms(homework['endTime'] - homework['startTime'])}')
                if homework['peerStatus'] == 0:
                    print(f'互评状态:未开启')
                    print(f'互评时间:{format_timestamp_ms(homework['peerReviewTime'])}')
                elif homework['peerStatus'] == 1:
                    print(f'互评时间:{format_timestamp_ms(homework['peerReviewTime'])}')
                    print(f'互评状态:已开启')
                else:
                    print(f'互评状态:已关闭')
            else:
                print(f'时间状态:已截止')
                print(f'作业得分:{homework['score']}')
            print()
    return

# 提取作业信息
def extractHomeworkInformation(courseId, homeworkId):
    """
    提取作业信息。

    根据课程ID和作业ID从JSON文件中提取相关信息，包括学生信息、作业详情、教师上传的文件和学生提交的文件。

    参数:
    courseId (str): 课程ID。
    homeworkId (str): 作业ID。

    返回:
    dict: 包含作业相关信息的字典。
    """

    # 读取JSON文件
    with open(f'HomeworkDetail/{courseId}_{homeworkId}_Detail.json', 'r', encoding='utf-8') as f:
        data = json.loads(f.read())

    # 提取学生信息
    student_name = data['result']['user']['name']
    student_email = data['result']['user']['mail']

    # 提取作业信息
    homework_title = data['result']['activityHomework']['homeworkTitle']
    homework_grade = data['result']['activityHomework']['grade']
    homework_request = data['result']['activityHomework']['homeworkRequest'].strip('<p>').strip('</p>')  # 移除HTML标签
    homework_startTime = format_timestamp_ms(data['result']['activityHomework']['startTime'])
    homework_endTime = format_timestamp_ms(data['result']['activityHomework']['endTime'])
    homework_remainingTime = format_remaining_time(data['result']['activityHomework']['startTime'],
                                                   data['result']['activityHomework']['endTime'])

    # 提取教师上传文件信息（如果有）
    teacher_file_uploads = []
    if data['result']['activityHomework']['fileUpload']:
        teacher_files = json.loads(data['result']['activityHomework']['fileUpload'])
        for file_info in teacher_files:
            teacher_file_uploads.append({
                'fileName': file_info.get('fileName'),
                'fileSize': file_info.get('fileSize'),
                'filePath': file_info.get('filePath')
            })

    # 提取学生提交的信息
    student_submission_files = []
    if data['result']['studentHomework']:
        if data['result']['studentHomework']['fileUpload']:
            student_files = json.loads(data['result']['studentHomework']['fileUpload'])
            for file_info in student_files:
                student_submission_files.append({
                    'fileName': file_info.get('fileName'),
                    'fileSize': file_info.get('fileSize'),
                    'filePath': file_info.get('filePath')
                })

    # 创建一个字典，包含所有信息
    information = {
        'student_name': student_name,
        'student_email': student_email,
        'homework_title': homework_title,
        'homework_grade': homework_grade,
        'homework_request': homework_request,
        'homework_startTime': homework_startTime,
        'homework_endTime': homework_endTime,
        'homework_remainingTime': homework_remainingTime,
        'teacher_file_uploads': teacher_file_uploads,
        'student_submission_files': student_submission_files
    }
    return information


# 打印作业信息
def printHomeworkInformation(courseId,homeworkId):

    # 从指定课程和作业中提取作业信息
    information = extractHomeworkInformation(courseId,homeworkId)

    # 提取学生姓名
    student_name = information.get('student_name')
    # 提取学生邮箱
    student_email = information.get('student_email')
    # 提取作业标题
    homework_title = information.get('homework_title')
    # 提取作业分数
    homework_grade = information.get('homework_grade')
    # 提取作业要求
    homework_request = information.get('homework_request')
    # 提取作业开始时间
    homework_startTime = information.get('homework_startTime')
    # 提取作业结束时间
    homework_endTime = information.get('homework_endTime')
    # 提取作业剩余时间
    homework_remainingTime = information.get('homework_remainingTime')
    # 提取教师上传的文件信息
    teacher_file_uploads = information.get('teacher_file_uploads')
    # 提取学生提交的文件信息
    student_submission_files = information.get('student_submission_files')

    # 输出提取的数据
    print("\n作业详细信息:")
    print(f"学生姓名: {student_name}")
    print(f"学生邮箱: {student_email}")
    print(f"作业标题: {homework_title}")
    print(f"开始时间: {homework_startTime}")
    print(f"结束时间: {homework_endTime}")
    print(f"剩余时间: {homework_remainingTime}")
    print(f"总分: {homework_grade}")
    print(f"作业要求: {homework_request}")

    # 判断是否有教师上传的文件
    if teacher_file_uploads:
        print("教师上传的文件:")
        for file_info in teacher_file_uploads:
            print(
                f"文件名: {file_info['fileName']}, 文件大小: {file_info['fileSize']} bytes, 文件路径: {file_info['filePath']}")
    else:
        print("无教师上传的文件")

    # 判断是否有学生提交的文件
    if student_submission_files:
        print("\n学生提交的文件:")
        for file_info in student_submission_files:
            print(
                f"文件名: {file_info['fileName']}, 文件大小: {file_info['fileSize']} bytes, 文件路径: {file_info['filePath']}")
    else:
        print("无学生提交的文件")
