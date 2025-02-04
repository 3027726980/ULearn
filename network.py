from selenium import webdriver
from selenium.common import TimeoutException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from requests.exceptions import ConnectionError, Timeout
from pathlib import Path
from function import decodeURL ,decodeUnicode

import os, time, requests, json

# 定义一个空列表用于存储Cookies
cookiesList = []


# 检查登录信息
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
        # 打印登录名和密码，以便用户确认
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


# 保存cookies
def saveCookies(loginName, password):
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
    chrome_driver_path = r'chromedriver-win64/chromedriver.exe'  # 使用原始字符串

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
    password_input = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'ul-input__inner')))[
        1]  # 假设第二个是密码输入框
    username_input.send_keys(loginName)
    password_input.send_keys(password)

    # 显式等待登录按钮出现并可点击
    print('正在登录...')
    login_button = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'btn-submit')))
    login_button.click()

    # 给予时间等待页面跳转
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
        # 保存cookies到JSON文件
        saveCookiesJSON(cookiesList)
        # 关闭浏览器
        driver.quit()
    except TimeoutException:
        # 关闭浏览器
        print("超时：指定的cookie未在预期时间内设置")
        driver.quit()


# 获取cookies
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


# 获取cookies详细信息
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
    # 这样做可以确保每个 cookie 的唯一性，并便于后续处理
    cookies_dict = {cookie['name']: cookie for cookie in cookiesList}

    # 定义保存 cookies 的文件路径
    # 文件名固定为 'cookies.json'，用于存储转换后的 JSON 数据
    file_path = 'cookies.json'

    # 写入 JSON 数据到文件
    # 使用 'w' 模式打开文件，准备写入
    # encoding='utf-8' 确保文件以 UTF-8 编码方式写入，支持多语言字符
    with open(file_path, 'w', encoding='utf-8') as f:
        # 使用 json.dump 将 Python 对象序列化为 JSON 格式并写入文件
        # ensure_ascii=False 确保非 ASCII 字符能够正确写入
        # indent=4 设置 JSON 数据的缩进格式，提高可读性
        json.dump(cookies_dict, f, ensure_ascii=False, indent=4)
        # 打印消息，确认 cookies 已成功保存
        print("Cookies已保存")


# 保存USERINFO
def saveUSERINFO():
    """
    从cookies文件中获取用户信息，并将其解码后保存到userinfo.json文件中。

    参数:
    cookies - 一个包含cookies信息的字典，用于获取USERINFO的value。

    返回值:
    无直接返回值，但会将解码后的用户信息打印到控制台并保存到文件中。
    """
    # 打开并读取cookies.json文件，获取cookies信息
    with open('cookies.json', 'r') as f:
        cookies = json.load(f)

    # 从cookies中获取编码后的用户信息字符串
    encodingStr = cookies['USERINFO']['value']

    # 解码URL并解码Unicode，得到原始用户信息字符串
    decodingStr = decodeUnicode(decodeURL(encodingStr))

    # 打印解码后的用户信息，用于调试
    # print(json.dumps(decodingStr,sort_keys=True,indent=4))
    # print(decodingStr)

    # 打开userinfo.json文件，准备写入解码后的用户信息
    with open('userinfo.json', 'w', encoding='utf-8') as w:
        # 将解码后的用户信息字符串转换为字典格式
        data_dict = json.loads(decodingStr)

        # 将用户信息字典写入文件，确保ASCII字符正确显示，并格式化输出
        json.dump(data_dict, w, ensure_ascii=False, indent=4)


# 获取保存的用户信息
def getUSERINFO():
    """
    读取并返回用户信息。

    此函数打开名为 'userinfo.json' 的JSON文件，该文件编码为utf-8。
    使用with语句确保文件被正确读取并关闭，防止资源泄露。
    通过json.load()函数将JSON格式的数据文件内容解析为字典，并返回。

    Returns:
        dict: 包含用户信息的字典。
    """
    with open('userinfo.json', 'r', encoding='utf-8') as f:
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


# 保存作业列表到HomeworkList文件夹
def saveCourseHomeworkList(AUTHORIZATION, courseId, name, folder='HomeworkList'):
    """
    保存课程作业列表

    该函数通过发送HTTP请求获取课程作业列表，并将其保存为JSON文件

    参数:
    - AUTHORIZATION: 请求的授权信息
    - ocId: 课程ID
    - name: 课程名称
    - folder: 保存作业列表的文件夹名称，默认为'HomeworkList'
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

# 获取作业详情并保存
def saveHomeworkDetail(AUTHORIZATION, homeworkId, userId, courseId):
    """
    参数:
    AUTHORIZATION: 用户授权信息
    homeworkId: 作业ID
    userId: 用户ID
    courseId: 课程ID
    """
    # 设置请求头，包含授权信息和其他元数据
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

    # 构造请求URL
    url = f'https://homeworkapi.ulearning.cn/stuHomework/homeworkDetail/{homeworkId}/{userId}/{courseId}'

    # 发起GET请求，获取作业详情
    response = requests.get(url=url, headers=headers)
    # 将响应数据解析为JSON格式
    # 假设 json_data 是你的 JSON 字符串
    data = json.loads(json.dumps(response.json(), indent=4, sort_keys=True, ensure_ascii=False))

    # 获取当前脚本所在的目录
    project_root = Path(__file__).parent  # 当前脚本所在的目录
    # 定义目标文件夹 'HomeworkDetail'
    target_folder = project_root / 'HomeworkDetail'
    # 创建 'HomeworkDetail' 文件夹，如果它不存在
    target_folder.mkdir(parents=True, exist_ok=True)

    # 定义保存文件的路径和名称
    savePath = f'HomeworkDetail/{courseId}_{homeworkId}_Detail.json'
    # 将解析后的数据保存到文件中
    with open(savePath, 'w', encoding='utf-8') as f:
        f.write(json.dumps(data, indent=4, sort_keys=True, ensure_ascii=False))
        # 打印保存成功的消息
        print(f'{courseId}_{homeworkId}保存成功：{savePath}')
