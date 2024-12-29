import json
from function import *


def main():
    loginName = input("请输入你的登录名：")
    password = input("请输入你的密码：")
    # loginName = "13500034933"
    # password = "Yxy123456"
    #账户密码错误退出程序
    if not checkLoginData(loginName,password):
        print("程序结束")
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

    # 获取课程列表对象字典
    coursesObjDict = getCoursesObjDict()

    # 打印课程列表
    print("课程列表:")
    for course in coursesObjDict.values():
        print(f"\t课程名称:{course.name} 教师名:{course.teacherName} 班级名:{course.className}")

    # 获取并保存课程作业列表
    print("课程作业列表:")
    for course in coursesObjDict.values():
        saveCourseHomeworkList(AUTHORIZATION, course.id, course.name)

    # 获取课程id列表
    coursesIdList = getCoursesIbjList(coursesObjDict)
    for courseId in coursesIdList:
        print(f"\n课程id:{courseId}")
        # 获取作业id列表
        homeworkIdList = getHomeworkIdList(courseId)
        print(homeworkIdList)
        if homeworkIdList:
            for homeworkId in homeworkIdList:
                print(f"作业id:{homeworkId}")
                printHomeworkDetail(AUTHORIZATION, homeworkId, userId, courseId)
        else:
            print("该课程没有作业")

if __name__ == '__main__':
    main()