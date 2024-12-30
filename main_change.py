import json
from function_change import *
import getpass

def main():
    max_attempts = 3
    attempts = 0

    while attempts < max_attempts:
        loginName = input("请输入你的登录名：")
        password = input("请输入你的密码：")

        if checkLoginData(loginName, password):
            print("登录成功")
            break
        else:
            attempts += 1
            print(f"账户密码错误，剩余尝试次数：{max_attempts - attempts}")

    if attempts == max_attempts:
        print("尝试次数过多，程序结束")

    # 获取并保存cookies
    saveCookies(loginName, password)

    # 获取当前设置的cookies
    cookies = getCookies()
    AUTHORIZATION = cookies.get('AUTHORIZATION')

    if not AUTHORIZATION:
        print("未能获取到有效的AUTHORIZATION，程序结束")
        return

    # 获取用户信息并保存到本地
    userinfo = get_user_info()
    if not userinfo:
        print("未能获取到用户信息，程序结束")
        return

    userId = userinfo.get('userId')
    if not userId:
        print("未能获取到用户ID，程序结束")
        return

    # 获取课程列表并保存到本地
    save_courses_list(AUTHORIZATION)
    coursesObjDict = getCoursesObjDict()

    if not coursesObjDict:
        print("未能获取到课程列表，程序结束")
        return

    # 打印课程列表并获取课程作业列表
    print("课程列表:")
    for course in coursesObjDict.values():
        print(f"\t课程名称:{course.name} 教师名:{course.teacherName} 班级名:{course.className}")
        saveCourseHomeworkList(AUTHORIZATION, course.id, course.name)

    # 获取并打印课程作业详细信息
    print("课程作业列表:")
    for course in coursesObjDict.values():
        courseId = course.id
        print(f"\n课程id:{courseId}")
        homeworkIdList = getHomeworkIdList(courseId)

        if not homeworkIdList:
            print("该课程没有作业")
            continue

        print(homeworkIdList)
        for homeworkId in homeworkIdList:
            print(f"作业id:{homeworkId}")
            print_homework_detail(AUTHORIZATION, homeworkId, userId, courseId)


if __name__ == '__main__':
    main()
