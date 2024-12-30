from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from requests.exceptions import ConnectionError, Timeout, JSONDecodeError
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from urllib.parse import unquote_plus
from pathlib import Path
from datetime import timedelta, datetime
from bs4 import BeautifulSoup

import os, time, requests, json
import logging
import os

# 定义一个空列表用于存储Cookies
cookiesList = []


# 检查用户密码是否正确
def checkLoginData(loginName, password):
    """
    检查登录信息的函数。

    此函数用于向指定的URL发送POST请求，以检查提供的登录名和密码是否有效。

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
        print('正在检查登录信息...')
        # 发送POST请求，包含参数和设置超时时间为20秒
        response = requests.get('https://courseapi.ulearning.cn/users/check', params=params, timeout=20)
        # 处理返回响应的JSON数据判断登录是否成功
        response_json = response.json()
        result = response_json.get('result')
        
        if result == 0:
            print('登录失败,请检查账户密码')
            return False
        elif result == 1:
            print('账户密码正确')
            return True
        elif result == 3:
            print('您已经连续输错账户密码多次，3分钟后重试')
            return False
        else:
            print('未知错误，请稍后再试')
            return False
    except ConnectionError:
        print('连接失败，请检查网络链接')
        return False
    except Timeout:
        print('请求超时，请检查网络链接')
        return False
    except JSONDecodeError:
        print('服务器返回无效的JSON数据')
        return False
    except Exception as e:
        print(f'发生未知错误: {e}')
        return False
# 配置日志记录
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

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
def get_cookies_detail(cookies_list):
    """
    将返回的Cookies处理成字典格式详细信息，方便后续操作和管理。

    参数:
    cookies_list -- 包含Cookies信息的列表，每个元素是一个字典。

    返回:
    一个字典，其中键是Cookies的名称，值是包含Cookies其他信息的字典。
    """

    # 输入验证
    if not isinstance(cookies_list, list):
        raise TypeError("参数必须是一个列表")
    
    if not cookies_list:
        return {}

    # 设置Cookies字典
    cookies_details_dict = {}
    
    for cookie in cookies_list:
        if not isinstance(cookie, dict) or 'name' not in cookie:
            raise ValueError("每个Cookies元素必须是一个包含'name'键的字典")
        
        cookie_name = cookie['name']
        if cookie_name in cookies_details_dict:
            # 根据业务需求选择如何处理重复键
            raise ValueError(f"发现重复的Cookie名称: {cookie_name}")
        
        cookies_details_dict[cookie_name] = cookie
    
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


# 通过cookies获取个人信息并保存
def saveUSERINFO(cookies_path='cookies.json', userinfo_path='userinfo.json'):
    """
    从cookies文件中获取用户信息，并将其解码后保存到userinfo.json文件中。

    参数:
    cookies_path - 包含cookies信息的JSON文件路径，默认为 'cookies.json'。
    userinfo_path - 保存解码后用户信息的JSON文件路径，默认为 'userinfo.json'。

    返回值:
    无直接返回值，但会将解码后的用户信息保存到文件中。
    """
    try:
        # 打开并读取cookies.json文件，获取cookies信息
        with open(cookies_path, 'r', encoding='utf-8') as f:
            cookies = json.load(f)

        # 从cookies中获取编码后的用户信息字符串
        encodingStr = cookies.get('USERINFO', {}).get('value')
        if not encodingStr:
            raise ValueError("USERINFO value not found in cookies")

        # 解码URL并解码Unicode，得到原始用户信息字符串
        decodingStr = decodeUnicode(decodeURL(encodingStr))

        # 将解码后的用户信息字符串转换为字典格式
        data_dict = json.loads(decodingStr)

        # 检查文件写入权限
        if not os.access(os.path.dirname(userinfo_path), os.W_OK):
            raise PermissionError("No write permission for the target directory")

        # 打开userinfo.json文件，准备写入解码后的用户信息
        with open(userinfo_path, 'w', encoding='utf-8') as w:
            # 将用户信息字典写入文件，确保ASCII字符正确显示，并格式化输出
            json.dump(data_dict, w, ensure_ascii=False, indent=4)

    except FileNotFoundError as e:
        print(f"Error: {e.strerror}, file: {e.filename}")
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
    except ValueError as e:
        print(f"Value error: {e}")
    except PermissionError as e:
        print(f"Permission error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

# 返回字典userinfo
def get_user_info(file_path='userinfo.json'):
    """
    读取并返回用户信息。

    此函数打开指定路径的JSON文件，该文件编码为utf-8。
    使用with语句确保文件被正确读取并关闭，防止资源泄露。
    通过json.load()函数将JSON格式的数据文件内容解析为字典，并返回。

    Args:
        file_path (str): JSON文件的路径，默认为 'userinfo.json'。

    Returns:
        dict: 包含用户信息的字典。如果文件读取失败，则返回空字典。

    Raises:
        FileNotFoundError: 如果文件不存在。
        PermissionError: 如果没有权限读取文件。
        json.JSONDecodeError: 如果文件内容不是有效的JSON格式。
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            userinfo = json.load(f)
            return userinfo
    except FileNotFoundError:
        print(f"Error: 文件 '{file_path}' 未找到")
        return {}
    except PermissionError:
        print(f"Error: 无权访问文件 '{file_path}'")
        return {}
    except json.JSONDecodeError:
        print(f"Error: 文件 '{file_path}' 内容不是有效的JSON格式")
        return {}

# 配置日志记录
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 从环境变量中获取授权信息
AUTHORIZATION = os.getenv('AUTHORIZATION')

# 配置文件路径
CONFIG_PATH = 'config.json'

# # 读取配置文件
# with open(CONFIG_PATH, 'r', encoding='utf-8') as config_file:
#     config = json.load(config_file)

# 获取保存课程列表
def save_courses_list(AUTHORIZATION):
    """
    获取课程列表并保存到JSON文件中。

    发起一个GET请求到课程API，获取学生的课程列表，然后将响应的JSON数据
    以格式化的形式保存到'coursesList.json'文件中。

    返回:
    - str: 格式化后的JSON字符串，包含课程列表信息。
    """

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

    try:
        # 发起GET请求，获取课程列表数据
        response = requests.get('https://courseapi.ulearning.cn/courses/students', params=params, headers=headers)
        response.raise_for_status()  # 检查请求是否成功

        # 解析响应内容为JSON
        data = response.json()

        # 打开文件，准备写入格式化后的JSON数据
        with open('coursesList.json', 'w', encoding='utf-8') as f:
            # 将响应的JSON数据格式化并写入文件
            json.dump(data, f, indent=4, sort_keys=True, ensure_ascii=False)

        # 打印消息，确认文件已保存
        logging.info("课程列表已保存到coursesList.json")

        # 返回格式化后的JSON字符串
        return json.dumps(data, indent=4, sort_keys=True, ensure_ascii=False)

    except requests.exceptions.RequestException as e:
        logging.error(f"请求失败: {e}")
        return None
    except json.JSONDecodeError as e:
        logging.error(f"解析JSON失败: {e}")
        return None
    except IOError as e:
        logging.error(f"文件操作失败: {e}")
        return None

from dataclasses import dataclass

@dataclass
class Course:
    """
    课程类，用于存储课程的详细信息。
    """
    classId: str
    className: str
    classUserId: str
    courseCode: str
    cover: str
    creatorOrgId: str
    creatorOrgName: str
    id: str
    learnProgress: float
    name: str
    publishStatus: str
    status: str
    teacherName: str
    totalDuration: int
    type: str

# 读取课程列表JSON返回课程对象字典
def getCoursesObjDict():
    """
    从JSON文件中读取课程列表，并创建课程对象字典。

    Returns:
        dict: 包含课程对象的字典，每个课程对象包含详细的课程信息。
    """
    try:
        # 打开并读取课程列表JSON文件
        with open('coursesList.json', 'r', encoding='utf-8') as f:
            coursesListJSON = json.loads(f.read()).get('courseList', [])

        # 初始化课程列表字典
        coursesObjDict = {}

        # 遍历JSON数据中的每个课程项，创建课程对象，并将其添加到课程列表字典中
        for course in coursesListJSON:
            try:
                coursesObjDict[f'course_{course.get("id", "")}'] = Course(
                    **{key: course.get(key, None) for key in Course.__annotations__}
                )
            except Exception as e:
                print(f"Error creating Course object for {course.get('id', '')}: {e}")

        # 返回包含所有课程对象的字典
        return coursesObjDict

    except FileNotFoundError:
        print("Error: The file 'coursesList.json' was not found.")
        return {}
    except json.JSONDecodeError:
        print("Error: Failed to decode JSON from 'coursesList.json'.")
        return {}


# 获取课程id列表
def getCoursesIdList(coursesDict):
    """
    获取课程字典中所有课程的ID列表。

    参数:
    coursesDict (dict): 包含课程对象的字典，键为课程名称或其他标识符，值为课程对象。

    返回:
    list: 包含所有课程ID的列表。
    """
    if not isinstance(coursesDict, dict):
        raise TypeError("输入参数必须是字典类型")

    coursesIdList = []
    for course in coursesDict.values():
        try:
            coursesIdList.append(course.id)
        except AttributeError:
            print(f"警告: 课程对象 {course} 没有 'id' 属性，已跳过")

    return coursesIdList

# 保存作业列表到HomeworkList文件夹
def saveCourseHomeworkList(AUTHORIZATION, courseId, name, folder='Homework'):
    """
    保存课程作业列表

    该函数通过发送HTTP请求获取课程作业列表，并将其保存为JSON文件

    参数:
    - AUTHORIZATION: 请求的授权信息
    - courseId: 课程ID
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
        'ps': '100',  # 增加每页大小以减少请求数量
        'lang': 'zh',
    }

    # 获取当前脚本所在的目录
    project_root = Path(__file__).parent  # 当前脚本所在的目录
    # 定义目标文件夹 'HomeworkList'
    target_folder = project_root / folder
    # 创建 'HomeworkList' 文件夹，如果它不存在
    target_folder.mkdir(parents=True, exist_ok=True)

    # 定义要写入的文件名和完整路径
    file_name = f"{courseId}_HomeworkList.json"
    file_path = target_folder / file_name

    try:
        # 发送GET请求获取作业列表数据
        response = requests.get('https://courseapi.ulearning.cn/homeworks/student/v2', params=params, headers=headers)
        response.raise_for_status()  # 检查请求是否成功
        data = response.json()

        if not data.get('total'):
            print(f'\t{name} 作业列表为空')
            return

        total = data['total']
        if total > int(params['ps']):
            params['ps'] = str(total)
            response = requests.get('https://courseapi.ulearning.cn/homeworks/student/v2', params=params, headers=headers)
            response.raise_for_status()
            data = response.json()

        # 打开文件准备写入作业列表数据
        with open(file_path, 'w', encoding='utf-8') as f:
            # 将格式化后的数据写入文件
            json.dump(data, f, indent=4, sort_keys=True, ensure_ascii=False)

        # 打印保存成功的消息
        print(f'\t{name} 作业列表已保存到 {file_path}')
    except requests.exceptions.RequestException as e:
        print(f'\t请求失败: {e}')
    except json.JSONDecodeError as e:
        print(f'\tJSON解析失败: {e}')

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

    # 验证 courseId 是否合法
    if not isinstance(courseId, str) or not courseId.strip():
        raise ValueError("Invalid courseId")

    # 使用配置文件或环境变量管理文件路径
    base_path = os.getenv('HOMEWORK_LIST_PATH', 'HomeworkList')
    path = os.path.join(base_path, f"{courseId}_HomeworkList.json")

    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"File not found: {path}")
        return {}
    except json.JSONDecodeError:
        print(f"Failed to decode JSON from file: {path}")
        return {}

    total = data.get('total', 0)
    HomeworkListObjDict = {}

    if total > 0:
        homework_list = data.get('homeworkList', [])
        for homework in homework_list:
            homework_id = homework.get('id')
            if homework_id:
                HomeworkListObjDict[f'homework_{homework_id}'] = Homework(
                    homework.get('endTime'),
                    homework.get('homeworkTitle'),
                    homework_id,
                    homework.get('personStatus'),
                    homework.get('publisher'),
                    homework.get('showLevel'),
                    homework.get('startTime'),
                    homework.get('state'),
                    homework.get('status'),
                    homework.get('teacherId'),
                    homework.get('timeStatus'),
                    homework.get('type')
                )

    return HomeworkListObjDict



# 获取作业列表ID列表
def getHomeworkIdList(courseId):
    try:
        HomeworkListObjDict = getHomeworkListObjDict(courseId)
        if not HomeworkListObjDict:
            logging.info("No homework found for courseId: %s", courseId)
            return []

        homeworkIdList = [homework.id for homework in HomeworkListObjDict.values()]
        for homework_id in homeworkIdList:
            logging.debug('homeworkId = %s', homework_id)

        return homeworkIdList

    except Exception as e:
        logging.error("Error occurred while fetching homework list for courseId: %s, Error: %s", courseId, str(e))
        return []

# 格式化时间戳
def format_timestamp_ms(timestamp_ms, format_str='%Y年%m月%d日 %p%I时'):
    """
    将13位毫秒级时间戳转换为指定格式的日期字符串。

    参数:
    timestamp_ms (int): 毫秒级时间戳
    format_str (str): 格式化字符串，默认为 '%Y年%m月%d日 %p%I时'

    返回:
    str: 格式化后的日期字符串
    """
    try:
        # 确保时间戳是整数
        if not isinstance(timestamp_ms, (int, float)):
            raise TypeError("timestamp_ms 必须是整数或浮点数")

        # 将13位时间戳转换为秒级别，并去掉小数部分
        timestamp_s = int(timestamp_ms // 1000)
        dt = datetime.fromtimestamp(timestamp_s)
        return dt.strftime(format_str)
    except (TypeError, OSError) as e:
        # 处理异常情况
        print(f"发生错误: {e}")
        return None

# 计算剩余时间
def format_remaining_time(start_ms, end_ms, format_str='{days}天{hours}小时{minutes}分钟{seconds}秒'):
    # 输入验证
    if not isinstance(start_ms, (int, float)) or not isinstance(end_ms, (int, float)):
        raise ValueError("start_ms 和 end_ms 必须是数字类型")

    # 将13位时间戳转换为秒级别
    start_s = start_ms / 1000
    end_s = end_ms / 1000

    try:
        # 计算当前时间和结束时间之间的时间差
        current_time_s = datetime.now().timestamp()
        remaining_time_delta = timedelta(seconds=end_s - current_time_s)

        if remaining_time_delta.total_seconds() <= 0:
            return "已过期"

        # 分解时间差
        total_seconds = remaining_time_delta.total_seconds()
        days, remainder = divmod(total_seconds, 86400)  # 一天有86400秒
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

    except Exception as e:
        # 异常处理
        print(f"发生异常: {e}")
        return "计算失败"

# 获取并打印作业详细内容
def get_formatted_time(timestamp_ms):
    timestamp = timestamp_ms / 1000
    return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')

def get_remaining_time(start_time_ms, end_time_ms):
    now = datetime.now()
    start_time = datetime.fromtimestamp(start_time_ms / 1000)
    end_time = datetime.fromtimestamp(end_time_ms / 1000)
    if now < start_time:
        return "尚未开始"
    elif now > end_time:
        return "已结束"
    else:
        remaining = end_time - now
        return str(remaining)

def extract_files(file_upload_str):
    if not file_upload_str:
        return []
    files = json.loads(file_upload_str)
    return [{
        'fileName': file_info.get('fileName', ''),
        'fileSize': file_info.get('fileSize', 0),
        'filePath': file_info.get('filePath', '')
    } for file_info in files]

def print_homework_detail(AUTHORIZATION, homeworkId, userId, courseId):
    """
    根据作业ID、用户ID和课程ID获取作业详细信息，并打印出来。

    参数:
    AUTHORIZATION (str): 认证信息。
    homeworkId (str): 作业ID。
    userId (str): 用户ID。
    courseId (str): 课程ID。
    """
    headers = {
        'Authorization': AUTHORIZATION,
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

    try:
        response = requests.get(url=url, headers=headers)
        response.raise_for_status()
        data = response.json()

        # 提取学生信息
        student_name = data.get('result', {}).get('user', {}).get('name', '未知')
        student_email = data.get('result', {}).get('user', {}).get('mail', '未知')

        # 提取作业信息
        homework_title = data.get('result', {}).get('activityHomework', {}).get('homeworkTitle', '未知')
        homework_grade = data.get('result', {}).get('activityHomework', {}).get('grade', '未知')
        homework_request = BeautifulSoup(data.get('result', {}).get('activityHomework', {}).get('homeworkRequest', ''), 'html.parser').get_text().strip()
        homework_startTime = get_formatted_time(data.get('result', {}).get('activityHomework', {}).get('startTime', 0))
        homework_endTime = get_formatted_time(data.get('result', {}).get('activityHomework', {}).get('endTime', 0))
        homework_remainingTime = get_remaining_time(
            data.get('result', {}).get('activityHomework', {}).get('startTime', 0),
            data.get('result', {}).get('activityHomework', {}).get('endTime', 0)
        )

        # 提取教师上传文件信息（如果有）
        teacher_file_uploads = extract_files(data.get('result', {}).get('activityHomework', {}).get('fileUpload'))

        # 提取学生提交的信息
        student_submission_files = extract_files(data.get('result', {}).get('studentHomework', {}).get('fileUpload'))

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
                print(
                    f"文件名: {file_info['fileName']}, 文件大小: {file_info['fileSize']} bytes, 文件路径: {file_info['filePath']}")

    except requests.exceptions.RequestException as e:
        print(f"请求失败: {e}")
    except json.JSONDecodeError as e:
        print(f"JSON解析失败: {e}")
    except KeyError as e:
        print(f"键错误: {e}")
