from passlib.hash import bcrypt_sha256
from datetime import date, timedelta

from app.models import Users, JobPost, MyError


# used for name and email checks in a registration process
def checkExistence(name, email):
    exist_name = Users.query.filter_by(name=name).first()
    exist_email = Users.query.filter_by(email=email).first()
    errors = []
    if exist_name:
        errors.append("Your user name has been used. Pls use a new name.")
    if exist_email:
        errors.append("Your email has been registered. Pls try a new one.")
    return errors


# used for name and password checks when trying to login in with username
def checkByName(name, password):
    user = Users.query.filter_by(name=name).first()
    errors = []
    if user is None:
        errors.append("No such user exists, pls check your inputs.")
    elif not bcrypt_sha256.verify(str(password), user.password):
        errors.append("Password does not match the given user. Pls try again.")
    return errors


# used for email and password checks when trying to login in with email
def checkByEmail(email, password):
    user = Users.query.filter_by(email=email).first()
    errors = []
    if user is None:
        errors.append("No user with this email exists, pls check your inputs.")
    elif not bcrypt_sha256.verify(str(password), user.password):
        errors.append("Password does not match the given user. Pls try again.")
    return errors


# turn a MySQL record object into a displayable post
def create_post(record):
    post = {}
    post["post_id"] = record.post_id
    post["title"] = record.title
    post["link"] = "https://" + record.link if record.link else None
    post["company"] = record.company
    post["salary_min"] = record.salary_min if record.salary_min > 0 else record.salary_max
    post["salary_max"] = record.salary_max if record.salary_max > 0 else record.salary_min
    if post["salary_min"] == 0 and post["salary_max"] == 0:
        post["salary"] = "not given"
    else:
        post["salary"] = " - ".join(["$"+str(post["salary_min"]), "$"+str(post["salary_max"])])
    post["date"] = record.date
    post["description"] = record.description

    return post


# generate a job post in ES-required format
def genESPost(post, id):
    esPost = {}
    esPost["_index"] = "index_jobposts"
    esPost["post_id"] = id
    esPost["title"] = post["title"]
    esPost["company"] = post["company"]
    esPost["description"] = post["snippet"]
    return esPost


# check if the job post with post_id "id" already exists in ES
def checkESPost(es, id):
    query = {
        "query": {
            "match_phrase": {
                "post_id": id
            }
        }
    }
    return es.search(index="index_jobposts", body=query)["hits"]["total"]["value"] > 0


# turn a MySQL user object into a displayable form
def create_userinfo(raw_user):
    user = {}
    
    user["user_id"] = raw_user.user_id
    user["name"] = raw_user.name
    user["email"] = raw_user.email
    if raw_user.role_id == 2:
        user["role"] = "Company"
    elif raw_user.role_id == 3:
        user["role"] = "Administrator"
    else:
        user["role"] = "Job Seeker"
    
    return user


# filter from a list of displayable results (format shown in function "create_post")
def filter_results(results, kw, val):
    filtered_results = []
    try:
        if val == "all":
            filtered_results = results
        elif kw == "date":
            val_num = int(val)
            if val_num == 1000:
                filtered_results = results
            else:
                today = date.today()
                for post in results:
                    delta = today - post["date"]
                    if delta.days <= val_num:
                        filtered_results.append(post)
        elif kw == "salary":
            if val == "None":
                for post in results:
                    if post["salary"] == "not given": 
                        filtered_results.append(post)
            else:
                category, thres_str = val.split("_")
                thres = int(thres_str)
                if category == "min":
                    for post in results:
                        if post["salary_min"] >= thres:
                            filtered_results.append(post)
                else:
                    for post in results:
                        if post["salary_max"] >= thres:
                            filtered_results.append(post)
        # other cases: filter by exact values (categorical data)
        else:
            if kw == "role":
                if val == "admin":
                    val = "Administrator"
                elif val == "company":
                    val = "Company"
                else:
                    val = "Job Seeker"
            for user in results:
                if user[kw] == val:
                    filtered_results.append(user)
    except Exception as e:
        MyError.display("JobFilter Error" + MyError.UI_REQUEST_UNKNOWN + "unknown keyword sent by UI.")
        print(e)
        return results

    return filtered_results


# sort a list of displayable results
def sort_results(results, kw, val):
    try:
        if kw == "salary":
            if val == "desc_min":
                sort_helper(results, lambda x : x["salary_min"])
            elif val == "desc_max":
                sort_helper(results, lambda x : x["salary_max"])
            elif val == "asc_min":
                sort_helper(results, lambda x : x["salary_min"], asc=True)
            else: 
                sort_helper(results, lambda x : x["salary_max"], asc=True)
        else:
            field = kw
            if field == "userid":
                field = "user_id"
            elif field == "postid":
                field = "post_id"
            
            if val == "asc":
                sort_helper(results, lambda x : x[field], asc=True)
            else:
                sort_helper(results, lambda x : x[field])
    except Exception as e:
        MyError.display("JobFilter Error" + MyError.UI_REQUEST_UNKNOWN + "unknown keyword sent by UI.")
        print(e)
    
    return results


# help sort the results according to keyword "key". Mergesort is applied to enable multi-keyword-sorting.
def sort_helper(posts, key, asc=False):
    length = len(posts)
    
    mergesort(posts, key, 0, length - 1)
    if asc:
        for i in range(length >> 1):
            posts[i], posts[length - 1 - i] = posts[length - 1 - i], posts[i]


# Notice: this is a destructive sorting!
def mergesort(lst, key, start, end):
    if start >= end: return

    mid = (start + end) >> 1
    mergesort(lst, key, start, mid)
    mergesort(lst, key, mid + 1, end)
    merge(lst, key, start, mid + 1, end)


def merge(lst, key, start, mid, end):
    aux = [lst[i] for i in range(start, mid)]    # save half of the space consumed
    i, j, k = 0, mid, start

    while i < mid - start and j <= end:
        if key(aux[i]) >= key(lst[j]):
            lst[k] = aux[i]
            i += 1
        else:
            lst[k] = lst[j]
            j += 1
        k += 1
    
    while i < mid - start:
        lst[k] = aux[i]
        i += 1
        k += 1


    # # not selected due to its unstability
    # def dual_pivot_quicksort(lst, start, end):
    #     if start >= end: return

    # if lst[start] < lst[end]:
    #     lst[start], lst[end] = lst[end], lst[start]
    # pivot_left = lst[start]
    # pivot_right = lst[end]

    # bound_left = start
    # bound_right = end
    # idx = start + 1
    # while idx < bound_right:
    #     if lst[idx] >= pivot_left:
    #         bound_left += 1
    #         lst[bound_left], lst[idx] = lst[idx], lst[bound_left]
    #         idx += 1
    #     elif lst[idx] < pivot_left and lst[idx] > pivot_right:
    #         idx += 1
    #     else:
    #         while bound_right > idx and lst[bound_right] <= pivot_right:
    #             bound_right -= 1
    #         lst[bound_right], lst[idx] = lst[idx], lst[bound_right]
    #         # Do not increment idx here:
    #         # the element at --bound_right might be larger than pivot_left!
    #         # Therefore, it is wiser to move bound_right other than idx.
    # lst[start], lst[bound_left] = lst[bound_left], lst[start]
    # lst[end], lst[bound_right] = lst[bound_right], lst[end]

    # dual_pivot_quicksort(lst, start, bound_left - 1)
    # dual_pivot_quicksort(lst, bound_left + 1, bound_right - 1)
    # dual_pivot_quicksort(lst, bound_right + 1, end)
