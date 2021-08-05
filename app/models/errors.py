class MyError():
    WEB_SOURCE_NULL = 1
    MYSQL_CREATE_FAIL = 2
    ES_CREATE_FAIL = 3

    def display(loc, issue, msg=""):
        print(loc + ": error_id " + str(issue) + "detail: " + msg)