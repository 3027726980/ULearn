from selenium import webdriver
from selenium.common import TimeoutException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from requests.exceptions import ConnectionError, Timeout
from urllib.parse import unquote_plus
from pathlib import Path
from datetime import datetime
from datetime import timedelta, datetime

import os,time,requests,json

# 定义一个空列表用于存储Cookies
cookiesList = []
#检查用户密码是否正确
def checkLoginData(loginName, password):
    """
    检查登录信息的函数。

    此函数用于向指定的URL发送GET请求，以检查提供的登录名和密码是否有效。

    参数:
    - loginName: 用户提供的登录名。
    - password: 用户提供的密码。

    返回:
    - 如果账户密码正确，返回True,否则返回False。
    """
    # 定义请求参数登录名和密码
    params = {
        'loginName': loginName,
        'password': password,
    }

    try:
        print(f'账户:{loginName}')
        print(f'密码:{password}')
        print('正在检查登录信息...')
        # 发送GET请求，包含参数和设置超时时间为20秒
        response = requests.get('https://courseapi.ulearning.cn/users/check', params=params, timeout=20)
        # 处理返回响应的JSON数据判断登录是否成功
        if response.json()['result'] == 0:
            print('登录失败,请检查账户密码')
            return False
        elif response.json()['result'] == 1:
            print('账户密码正确')
            return True
        elif response.json()['result'] == 3:
            print('您已经连续输错账户密码多次，3分钟后重试')
            return False
    except ConnectionError:
        # 发生连接错误时打印错误信息并返回错误代码1
        print('链接失败请检查网络链接')
    except Timeout:
        # 请求超时时打印错误信息并返回错误代码2
        print('请求超时请检查网络链接')

# 以列表形式返回Cookies
def saveCookies(loginName,password):
    """
    通过 Selenium 使用 Chrome 浏览器自动化登录过程，以获取登录后的 cookies。

    参数:
    loginName (str): 用户登录名
    password (str): 用户密码

    返回:
    dict: 登录后的 cookies 字典列表

    保存:
    将cookies以JSON格式保存
    """

    # 定义一个函数判断某个cookies是否设定
    def checkCookiesName(cookie_name):
        cookie = driver.get_cookie(cookie_name)
        return cookie is not None and 'value' in cookie and cookie['value']

    # 设置Chrome选项
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # 无头模式
    options.add_argument('--disable-gpu')  # 禁用GPU加速（在某些系统上可能需要）
    options.add_argument('--window-size=1920x1080')  # 设置窗口大小

    # 指定ChromeDriver的路径
    chrome_driver_path = r'D:\PythonLearning\PythonProject_crawler\SourceCode\chromedriver.exe'  # 使用原始字符串

    # 检查文件是否存在
    if not os.path.isfile(chrome_driver_path):
        raise FileNotFoundError(f"Chromedriver not found at: {chrome_driver_path}")

    # 创建Service对象
    service = Service(chrome_driver_path)

    # 创建WebDriver实例
    driver = webdriver.Chrome(service=service, options=options)

    # 打开登录页面
    driver.get('https://umooc.ulearning.cn/pc.html#/login')

    # 显式等待页面加载
    wait = WebDriverWait(driver, timeout=20, poll_frequency=0.5)  # 最多等待20秒,每0.5秒检测一次

    # 定位用户名和密码输入框，并输入信息
    username_input = wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'ul-input__inner')))
    password_input = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'ul-input__inner')))[1]  # 假设第二个是密码输入框
    username_input.send_keys(loginName)
    password_input.send_keys(password)

    # 显式等待登录按钮出现并可点击
    print('正在登录...')
    login_button = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'btn-submit')))
    login_button.click()

    #给予时间等待页面跳转
    time.sleep(5)

    # 显示等待获取cookies
    try:
        # 使用WebDriverWait结合自定义条件进行等待
        wait.until(lambda d: checkCookiesName('USERINFO'))  # 等待名为'USERINFO'的cookie被设置
        wait.until(lambda d: checkCookiesName('USER_INFO'))  # 等待名为'USERINFO'的cookie被设置
        wait.until(lambda d: checkCookiesName('token'))  # 等待名为'USERINFO'的cookie被设置
        print("登录成功")
        print('正在等待cookies...')
        # 获取Cookies
        global cookiesList
        cookiesList = driver.get_cookies()
        print("Cookie已设置")
        saveCookiesJSON(cookiesList)
        # 关闭浏览器
        driver.quit()
    except TimeoutException:
        # 关闭浏览器
        print("超时：指定的cookie未在预期时间内设置")
        driver.quit()

# 读取cookiesList,返回以cookies的name为键,value为键值的字典
def getCookies():
    """
    将返回的Cookies处理成字典格式，可以直接作为requests的cookies携带。

    参数:
    传入selenium返回的cookies列表。

    返回:
    一个字典，其中键是Cookies的名称，值是包含Cookies其他信息的字典。
    """

    # 初始化一个空字典来存储处理后的Cookies
    cookies = {}
    # 遍历Cookies列表，将其转换为字典格式
    for i in cookiesList:
        # 将Cookies的名称作为键，Cookies的值作为值存入字典
        cookies[i.get('name')] = i.get('value')
    # 返回处理后的Cookies字典
    return cookies

# 传入 loginName,password 返回以cookies的name为键,其余属性为键值对组成的字典
def getCookiesDetail(cookiesList):
    """
    将返回的Cookies处理成字典格式详细信息，方便后续操作和管理。

    参数:
    cookies -- 未使用，保留参数占位，为后续可能的扩展留下接口。

    返回:
    一个字典，其中键是Cookies的名称，值是包含Cookies其他信息的字典。
    """

    # 设置Cookies字典
    cookies_details_dict = {}
    # 处理返回的Cookies,键是Cookies的名称，值是包含Cookies其他信息的字典
    for i in cookiesList:
        cookies_details_dict[i.get('name')] = i
    return cookies_details_dict

# 将cookies保存为JSON格式
def saveCookiesJSON(cookiesList):
    """
    将 cookies 列表转换为 JSON 格式，并保存到文件中。

    参数:
    cookiesList (list): 包含多个 cookie 字典的列表。

    返回:
    无
    """

    # 将 cookies 列表转换为字典格式，以 cookie 的 'name' 属性作为键
    cookies_dict = {cookie['name']: cookie for cookie in cookiesList}

    # 定义保存 cookies 的文件路径
    file_path = 'cookies.json'

    # 写入 JSON 数据到文件
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(cookies_dict, f, ensure_ascii=False, indent=4)
        print("Cookies已保存")

#字符串Unicode解码
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

#字符串URL解码
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

# 通过cookies获取个人信息并保存
def saveUSERINFO():
    """
    从cookies文件中获取用户信息，并将其解码后保存到userinfo.json文件中。
    
    参数:
    cookies - 一个包含cookies信息的字典，用于获取USERINFO的value。
    
    返回值:
    无直接返回值，但会将解码后的用户信息打印到控制台并保存到文件中。
    """
    # 打开并读取cookies.json文件，获取cookies信息
    with open('cookies.json','r') as f:
        cookies = json.load(f)
    
    # 从cookies中获取编码后的用户信息字符串
    encodingStr = cookies['USERINFO']['value']
    
    # 解码URL并解码Unicode，得到原始用户信息字符串
    decodingStr = decodeUnicode(decodeURL(encodingStr))
    
    # 打印解码后的用户信息，用于调试
    # print(json.dumps(decodingStr,sort_keys=True,indent=4))
    # print(decodingStr)

    # 打开userinfo.json文件，准备写入解码后的用户信息
    with open('userinfo.json','w',encoding='utf-8') as w:
        # 将解码后的用户信息字符串转换为字典格式
        data_dict = json.loads(decodingStr)
        
        # 将用户信息字典写入文件，确保ASCII字符正确显示，并格式化输出
        json.dump(data_dict,w,ensure_ascii=False,indent=4)
        
        # 打印处理后的用户信息字典，移除任何反斜杠字符
        # print(json.dumps(data_dict,ensure_ascii=False,indent=4).replace('\\',''))

#返回字典userinfo
def getUSERINFO():
    """
    读取并返回用户信息。

    此函数打开名为 'userinfo.json' 的JSON文件，该文件编码为utf-8。
    使用with语句确保文件被正确读取并关闭，防止资源泄露。
    通过json.load()函数将JSON格式的数据文件内容解析为字典，并返回。

    Returns:
        dict: 包含用户信息的字典。
    """
    with open('userinfo.json','r',encoding='utf-8') as f:
        userinfo = json.load(f)
        return userinfo

# 获取保存课程列表
def saveCoursesList(AUTHORIZATION):
    """
    获取课程列表并保存到JSON文件中。

    发起一个GET请求到课程API，获取学生的课程列表，然后将响应的JSON数据
    以格式化的形式保存到'coursesList.json'文件中。

    参数:
    - AUTHORIZATION (str): 用户的授权信息，用于请求头中。

    返回:
    - str: 格式化后的JSON字符串，包含课程列表信息。
    """
    # 设置请求头，包含授权信息和其他元数据
    headers = {
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Authorization': AUTHORIZATION,
        'Connection': 'keep-alive',
        'Content-Type': 'application/json',
        'Origin': 'https://courseweb.ulearning.cn',
        'Referer': 'https://courseweb.ulearning.cn/',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-site',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
        'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
    }

    # 设置请求参数，用于指定查询条件
    params = {
        'keyword': '',
        'publishStatus': '1',
        'type': '1',
        'pn': '1',
        'ps': '15',
        'lang': 'zh',
    }

    # 发起GET请求，获取课程列表数据
    response = requests.get('https://courseapi.ulearning.cn/courses/students', params=params, headers=headers)

    # 打开文件，准备写入格式化后的JSON数据
    with open('coursesList.json', 'w', encoding='utf-8') as f:
        # 将响应的JSON数据格式化并写入文件
        f.write(json.dumps(response.json(), indent=4, sort_keys=True, ensure_ascii=False))

    # 打印消息，确认文件已保存
    print("课程列表已保存到coursesList.json")

    # 返回格式化后的JSON字符串
    return json.dumps(response.json(), indent=4, sort_keys=True, ensure_ascii=False)

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

#获取课程id列表
def getCoursesIbjList(coursesDict):
    coursesIdList = []
    for course in coursesDict.values():
        coursesIdList.append(course.id)
    return coursesIdList

# 保存作业列表到HomeworkList文件夹
def saveCourseHomeworkList(AUTHORIZATION, courseId, name, folder = 'Homework'):
    """
    保存课程作业列表

    该函数通过发送HTTP请求获取课程作业列表，并将其保存为JSON文件

    参数:
    - AUTHORIZATION: 请求的授权信息
    - ocId: 课程ID
    - name: 课程名称
    - folder: 保存作业列表的文件夹名称，默认为'Homework'
    """
    # 设置请求头，包含授权信息和其他元数据
    headers = {
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Authorization': AUTHORIZATION,
        'Connection': 'keep-alive',
        'Content-Type': 'application/json',
        'Origin': 'https://courseweb.ulearning.cn',
        'Referer': 'https://courseweb.ulearning.cn/',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-site',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
        'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
    }

    # 设置请求参数，包括课程ID、页码、每页大小和语言
    params = {
        'ocId': courseId,
        'pn': '1',
        'ps': '10',
        'lang': 'zh',
    }

    # 获取当前脚本所在的目录
    project_root = Path(__file__).parent  # 当前脚本所在的目录
    # 定义目标文件夹 'HomeworkList'
    target_folder = project_root / folder
    # 创建 'HomeworkList' 文件夹，如果它不存在
    target_folder.mkdir(parents=True, exist_ok=True)

    # 定义要写入的文件名和完整路径
    file_name = f"{courseId}_Homework.json"
    file_path = target_folder / file_name

    # 发送GET请求获取作业列表数据
    response = requests.get('https://courseapi.ulearning.cn/homeworks/student/v2', params=params, headers=headers)

    total = response.json()['total']
    ps = params['ps']

    if response.json()['total'] > response.json()['ps']:
        params = {
            'ocId': courseId,
            'pn': '1',
            'ps': total,
            'lang': 'zh',
        }
        # 发送GET请求获取作业列表数据
        response = requests.get('https://courseapi.ulearning.cn/homeworks/student/v2', params=params, headers=headers)

    # 打开文件准备写入作业列表数据
    with open(f"HomeworkList/{courseId}_HomeworkList.json", 'w', encoding='utf-8') as f:
        # 将格式化后的数据写入文件
        f.write(json.dumps(response.json(), indent=4, sort_keys=True, ensure_ascii=False))

    # 打印保存成功的消息
    print(f'\t{name} 作业列表已保存到course_id : {courseId}_HomeworkList.json')

# 获取作业列表对象字典
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

# 获取作业列表ID列表
def getHomeworkIdList(courseId):
    HomeworkListObjDict = getHomeworkListObjDict(courseId)
    homeworkIdList = []
    for homework in HomeworkListObjDict.values():
        print(f'homeworkId = {homework.id}')
        homeworkIdList.append(homework.id)
    return homeworkIdList

# 格式化时间戳
def format_timestamp_ms(timestamp_ms, format_str='%Y年%m月%d日%H小时'):
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

# 获取并打印作业详细内容
def printHomeworkDetail(AUTHORIZATION, homeworkId, userId, courseId):
    """
    根据作业ID、用户ID和课程ID获取作业详细信息，并打印出来。

    参数:
    AUTHORIZATION (str): 认证信息。
    homeworkId (str): 作业ID。
    userId (str): 用户ID。
    courseId (str): 课程ID。
    """
    headers = {
        'AUTHORIZATION': AUTHORIZATION,
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'zh',
        'Connection': 'keep-alive',
        'Origin': 'https://homework.ulearning.cn',
        'Referer': 'https://homework.ulearning.cn/',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-site',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
        'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
    }

    url = f'https://homeworkapi.ulearning.cn/stuHomework/homeworkDetail/{homeworkId}/{userId}/{courseId}'

    response = requests.get(url=url, headers=headers)
    tmp = response.json()

    # 假设 json_data 是你的 JSON 字符串
    data = json.loads(json.dumps(response.json(), indent=4, sort_keys=True, ensure_ascii=False))

    # 提取学生信息
    student_name = data['result']['user']['name']
    student_email = data['result']['user']['mail']

    # 提取作业信息
    homework_title = data['result']['activityHomework']['homeworkTitle']
    homework_grade = data['result']['activityHomework']['grade']
    homework_request = data['result']['activityHomework']['homeworkRequest'].strip('<p>').strip('</p>')  # 移除HTML标签
    homework_startTime  = format_timestamp_ms(data['result']['activityHomework']['startTime'])
    homework_endTime = format_timestamp_ms(data['result']['activityHomework']['endTime'])
    homework_remainingTime = format_remaining_time(data['result']['activityHomework']['startTime'], data['result']['activityHomework']['endTime'])

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

    # 输出提取的数据
    print("\n作业详细信息:")
    print(f"作业ID: {homeworkId}")
    print(f"学生姓名: {student_name}")
    print(f"学生邮箱: {student_email}")
    print(f"作业标题: {homework_title}")
    print(f"开始时间: {homework_startTime}")
    print(f"结束时间: {homework_endTime}")
    print(f"剩余时间: {homework_remainingTime}")
    print(f"总分: {homework_grade}")
    print(f"作业要求: {homework_request}")

    if teacher_file_uploads:
        print("教师上传的文件:")
        for file_info in teacher_file_uploads:
            print(
                f"文件名: {file_info['fileName']}, 文件大小: {file_info['fileSize']} bytes, 文件路径: {file_info['filePath']}")

    if student_submission_files:
        print("\n学生提交的文件:")
        for file_info in student_submission_files:
            print(f"文件名: {file_info['fileName']}, 文件大小: {file_info['fileSize']} bytes, 文件路径: {file_info['filePath']}")