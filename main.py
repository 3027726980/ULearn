from function import *
from info import *
from network import *
import sys

# 搜索课程和作业
def search():
    model = 0 # 模式选择
    while True:
        print("请选择模式：")
        print("1. 搜索课程")
        print("2. 搜索作业")
        print("3. 获取所有课程")
        print("4. 通过课程ID获取所有作业")
        print("5. 退出")
        model = int(input("请输入模式编号："))
        if model == 1:
            courseID = eval(input("请输入课程ID："))
            searchCourse(courseID)
        elif model == 2:
            courseID = eval(input("请输入课程ID："))
            homeworkID = eval(input("请输入作业ID："))
            print()
            printHomeworkInformation(courseID, homeworkID)
            print()
        elif model == 3:
            getAllCourses()
        elif model == 4:
            courseID = eval(input("请输入课程ID："))
            print()
            getHomeworkList(courseID)
            print()
        elif model == 5:
            print("退出程序")
            break
        else:
            print("无效的输入，请重新输入")

# 登录联网查询
def login():
    max_attempts = 3 # 尝试登录的最大次数
    attempts = 0 # 当前尝试次数

    # 登录
    while attempts < max_attempts:
        loginName = input("请输入你的登录名：")
        password = input("请输入你的密码：")

        if checkLoginData(loginName, password):
            break
        else:
            attempts += 1
            print(f"账户密码错误，剩余尝试次数：{max_attempts - attempts}")
            if attempts == max_attempts:
                print("尝试次数过多，程序结束")
                sys.exit()

    # 传入登录名和密码获取并保存cookies
    saveCookies(loginName, password)
    
    # 获取当前设置的cookies
    cookies = getCookies()

    # 获取AUTHORIZATION
    AUTHORIZATION = cookies['AUTHORIZATION']
    # 获取用户信息保存到本地
    saveUSERINFO()
    # 获取用户id
    userId = getUSERINFO()['userId']

    #获取userinfo字典
    userinfo = getUSERINFO()

    # 获取课程列表保存到本地
    saveCoursesList(AUTHORIZATION)


    # 获取并保存课程作业列表
    # 获取课程列表对象字典
    coursesObjDict = getCoursesObjDict()
    for course in coursesObjDict.values():
        saveCourseHomeworkList(AUTHORIZATION, course.id, course.name)

    # 获取并保存作业详情
    # 获取课程id列表
    coursesIdList = getCoursesIbjList(coursesObjDict)
    for courseId in coursesIdList:
        # 获取作业id列表
        homeworkIdList = getHomeworkIdList(courseId)
        for homeworkId in homeworkIdList:
            if homeworkId:
                # 保存作业详情
                saveHomeworkDetail(AUTHORIZATION, homeworkId, userId, courseId)



if __name__ == '__main__':
    model = input('是否联网查询(y/n): ')
    if model == 'y':
        login()
        search()
    else:
        search()
