from datetime import timedelta, datetime
from urllib.parse import unquote_plus
import json

# 格式化时间戳
def format_timestamp_ms(timestamp_ms, format_str='%Y年%m月%d日%H时'):
    # 将13位时间戳转换为秒级别，并去掉小数部分
    timestamp_s = timestamp_ms / 1000.0
    dt = datetime.fromtimestamp(timestamp_s)
    return dt.strftime(format_str)

# 计算剩余时间
def format_remaining_time(start_ms, end_ms, format_str='{days}天{hours}小时{minutes}分钟{seconds}秒'):
    # 将13位时间戳转换为秒级别
    start_s = start_ms / 1000
    end_s = end_ms / 1000


    # 计算当前时间和结束时间之间的时间差
    current_time_s = datetime.now().timestamp()
    remaining_time_delta = timedelta(seconds=end_s - current_time_s)

    if remaining_time_delta.total_seconds() <= 0:
        return "已过期"
    # 分解时间差
    days, remainder = divmod(remaining_time_delta.total_seconds(), 86400)  # 一天有86400秒
    hours, remainder = divmod(remainder, 3600)  # 一小时有3600秒
    minutes, seconds = divmod(remainder, 60)  # 一分钟有60秒

    # 格式化输出
    formatted_time = format_str.format(
        days=int(days),
        hours=int(hours),
        minutes=int(minutes),
        seconds=int(seconds)
    )

    return formatted_time
# 字符串Unicode解码
def decodeUnicode(inputStr):
    """
    解码包含 '%u' Unicode 转义序列的字符串。

    参数:
    inputStr -- 待解码的字符串

    返回:
    解码后的字符串的
    """
    # 检查输入字符串是否为空或不包含 '%u'，如果是，则直接返回
    if not inputStr or '%u' not in inputStr:
        return inputStr

    # 替换 '%u' 为 '\u'
    escapedString = inputStr.replace('%u', '\\u')
    # 解码 Unicode 转义序列
    decodedString = escapedString.encode('utf-8').decode('unicode_escape')
    return decodedString


# 字符串URL解码
def decodeURL(inputStr):
    """
    解码URL中的查询字符串。

    本函数使用unquote_plus函数对输入的URL查询字符串进行解码，恢复其原始形式。
    这在处理URL参数或解析用户输入的URL时非常有用。

    参数:
    inputStr (str): 一个经过URL编码的查询字符串。

    返回:
    str: 解码后的查询字符串。
    """

    # 进行URL解码
    decodedQuery = unquote_plus(inputStr)
    return decodedQuery

# 读取课程列表JSON返回课程对象字典
def getCoursesObjDict():
    """
    从JSON文件中读取课程列表，并创建课程对象字典。

    Returns:
        dict: 包含课程对象的字典，每个课程对象包含详细的课程信息。
    """
    # 打开并读取课程列表JSON文件
    with open('coursesList.json', 'r', encoding='utf-8') as f:
        coursesListJSON = json.loads(f.read())['courseList']

    # 定义课程类
    class Course:
        """
        课程类，用于存储课程的详细信息。

        Attributes:
            classId (str): 课程ID
            className (str): 课程名称
            classUserId (str): 用户ID
            courseCode (str): 课程代码
            cover (str): 课程封面图片URL
            creatorOrgId (str): 创建者组织ID
            creatorOrgName (str): 创建者组织名称
            id (str): 课程ID
            learnProgress (float): 学习进度
            name (str): 课程名称
            publishStatus (str): 发布状态
            status (str): 课程状态
            teacherName (str): 老师名称
            totalDuration (int): 总时长
            type (str): 课程类型
        """

        def __init__(self, classId, className, classUserId, courseCode, cover, creatorOrgId, creatorOrgName, id,
                     learnProgress, name, publishStatus, status, teacherName, totalDuration, type):
            self.classId = classId
            self.className = className
            self.classUserId = classUserId
            self.courseCode = courseCode
            self.cover = cover
            self.creatorOrgId = creatorOrgId
            self.creatorOrgName = creatorOrgName
            self.id = id
            self.learnProgress = learnProgress
            self.name = name
            self.publishStatus = publishStatus
            self.status = status
            self.teacherName = teacherName
            self.totalDuration = totalDuration
            self.type = type

    # 初始化课程列表字典
    coursesObjDict = {}

    # 遍历JSON数据中的每个课程项，创建课程对象，并将其添加到课程列表字典中
    for course in coursesListJSON:
        coursesObjDict[f'course_{course['id']}'] = Course(course['classId'],
                                                          course['className'],
                                                          course['classUserId'],
                                                          course['courseCode'],
                                                          course['cover'],
                                                          course['creatorOrgId'],
                                                          course['creatorOrgName'],
                                                          course['id'],
                                                          course['learnProgress'],
                                                          course['name'],
                                                          course['publishStatus'],
                                                          course['status'],
                                                          course['teacherName'],
                                                          course['totalDuration'],
                                                          course['type'])

    # 返回包含所有课程对象的字典
    return coursesObjDict

# 获取课程id列表
def getCoursesIbjList(coursesDict):
    coursesIdList = []
    for course in coursesDict.values():
        coursesIdList.append(course.id)
    return coursesIdList
# 获取作业列表的字典对象

def getHomeworkListObjDict(courseId):
    """
    根据课程ID获取作业列表的字典对象。

    此函数通过读取存储在JSON文件中的作业列表数据，为每个作业创建一个Homework对象，
    并将这些对象存储在一个字典中。每个作业的ID用作字典的键，以便于根据作业ID快速检索作业信息。

    参数:
    courseId (str): 课程ID，用于标识特定课程的作业列表。

    返回:
    dict: 包含所有作业对象的字典，键为'homework_'前缀加上作业ID。
    """

    # 定义作业类
    class Homework:
        """
        作业类，用于存储单个作业的信息。

        属性:
        endTime (str): 作业结束时间
        homeworkTitle (str): 作业标题
        id (str): 作业ID
        personStatus (str): 个人状态
        publisher (str): 发布者
        showLevel (str): 显示级别
        startTime (str): 作业开始时间
        state (str): 作业状态
        status (str): 状态
        teacherId (str): 老师ID
        timeStatus (str): 时间状态
        type (str): 作业类型
        """

        def __init__(self, endTime, homeworkTitle, id, personStatus, publisher, showLevel, startTime, state,
                     status, teacherId, timeStatus, type):
            self.endTime = endTime
            self.homeworkTitle = homeworkTitle
            self.id = id
            self.personStatus = personStatus
            self.publisher = publisher
            self.showLevel = showLevel
            self.startTime = startTime
            self.state = state
            self.status = status
            self.teacherId = teacherId
            self.timeStatus = timeStatus
            self.type = type

    # 打开并读取作业列表的JSON文件
    path = f"HomeworkList/{courseId}_HomeworkList.json"
    with open(path, 'r', encoding='utf-8') as f:
        data = f.read()
        total = json.loads(data).get('total')

        # 初始化作业列表字典
        HomeworkListObjDict = {}
        if total == 0:
            pass
        else:
            HomeworkListJSON = json.loads(data).get('homeworkList')
            # 遍历JSON数据中的每个课程项，创建课程对象，并将其添加到作业列表字典中
            for homework in HomeworkListJSON:
                HomeworkListObjDict[f'homework_{homework['id']}'] = Homework(homework['endTime'],
                                                                             homework['homeworkTitle'],
                                                                             homework['id'],
                                                                             homework['personStatus'],
                                                                             homework['publisher'],
                                                                             homework['showLevel'],
                                                                             homework['startTime'],
                                                                             homework['state'],
                                                                             homework['status'],
                                                                             homework['teacherId'],
                                                                             homework['timeStatus'],
                                                                             homework['type'])

        # if json.loads(f.read()).get('homeworkList'):
        #     HomeworkListJSON = json.loads(f.read()).get('homeworkList', defaultsHomeworkListJSON)

    # 返回包含所有作业对象的字典
    return HomeworkListObjDict

# 获取课程作业ID列表
def getHomeworkIdList(courseId):
    HomeworkListObjDict = getHomeworkListObjDict(courseId)
    homeworkIdList = []
    for homework in HomeworkListObjDict.values():
        print(f'homeworkId = {homework.id}')
        homeworkIdList.append(homework.id)
    return homeworkIdList