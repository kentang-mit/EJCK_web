from flask import Flask, redirect, url_for, session, request, jsonify
from flask_oauthlib.client import OAuth
from flask_cors import *
from functools import wraps
from flask import make_response
import base64
from dbconnection import *
import json

app = Flask(__name__)
CORS(app, supports_credentials=True)
app.debug = True
app.secret_key = 'development'
oauth = OAuth(app)

sjtu = oauth.remote_app(
    'sjtu',
    consumer_key='SEE_QQ_GROUP',
    consumer_secret='SEE_QQ_GROUP',
    request_token_params={'scope': ['essential','lessons']},
    base_url='https://jaccount.sjtu.edu.cn/',
    request_token_url=None,
    access_token_method='POST',
    access_token_url='/oauth2/token',
    authorize_url='/oauth2/authorize'
)

dbObject = dbHandle()
cursor = dbObject.cursor()

class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o,'Decimal'):
            return str(o)
        return json.JSONEncoder.default(self,o)

app.json_encoder = JSONEncoder
@app.route('/api')
def index():
    if 'token' in session:
        me = sjtu.get('https://api.sjtu.edu.cn/v1/me/profile')
        data = jsonify(me.data)
        response = make_response(redirect('http://101.132.153.104'))
        response.set_cookie('data', data)
        return response
    return redirect(url_for('login'))


@app.route('/login')
def login():
    print("login")
    #modified
    return sjtu.authorize(callback=url_for('authorized', _external=True))


@app.route('/logout')
def logout():
    session.pop('sjtu_token', None)
    return redirect(url_for('index'))


@app.route('/login/authorized')
def authorized():
    resp = sjtu.authorized_response()
    if resp is None or resp.get('access_token') is None:
        return 'Access denied: reason=%s error=%s resp=%s' % (
            request.args['error'],
            request.args['error_description'],
            resp
        )
    session['sjtu_token'] = (resp['access_token'], '')
    me = sjtu.get('https://api.sjtu.edu.cn/v1/me/profile')
    #data = jsonify(me.data)
    data = me.data
    response = make_response(redirect('http://101.132.153.104'))
    curname = data['entities'][0]['name']
    curname_array = bytes(curname, encoding='utf8')
    curname_encoded = base64.b64encode(curname_array)
    curcode = data['entities'][0]['code']
    curacademy = data['entities'][0]['organize']['id']
    curJAccount = data['entities'][0]['account']
    sql = 'INSERT IGNORE INTO Student(stuId, jAccount, name, schoolid) values(%s,%s,%s,%s)'    
    cursor.execute(sql,(curcode, curJAccount, curname, curacademy))
    dbObject.commit()
    response.set_cookie('name', curname_encoded)
    response.set_cookie('stuId', curcode)
    response.set_cookie('academy', curacademy)
    
    #response = make_response(jsonify(data))
    #response.set_cookie('name',data['entities'][0]['name'])
    return response

@sjtu.tokengetter
def get_github_oauth_token():
    return session.get('sjtu_token')


@app.route('/login/teacher_authorized')
def teacher_authorized():
    resp = sjtu.authorized_response()
    if resp is None or resp.get('access_token') is None:
        return 'Access denied: reason=%s error=%s resp=%s' % (
            request.args['error'],
            request.args['error_description'],
            resp
        )

    session['sjtu_token'] = (resp['access_token'], '')
    me = sjtu.get('https://api.sjtu.edu.cn/v1/me/profile')
    #data = jsonify(me.data)
    data = me.data
    curname = data['entities'][0]['name']
    curname_array = bytes(curname, encoding='utf8')
    curname_encoded = base64.b64encode(curname_array)
    curcode = data['entities'][0]['code']
    curacademy = data['entities'][0]['organize']['id']
    sql = 'INSERT IGNORE INTO Teacher(workId, name, schoolid) values(%s,%s,%s)'    
    cursor.execute(sql,(curcode, curname, curacademy))
    dbObject.commit()


    me = sjtu.get('https://api.sjtu.edu.cn/v1/me/lessons?access_token='+resp['access_token'])
    data = me.data['entities']
    sql = 'INSERT IGNORE INTO Course(bsid,name,code) values'
    course_tup = []
    for x in data:
        sql += "(%s,%s,%s),"
        cur_bsid = x['bsid']
        cur_code = x['course']['code']
        cur_name = x['course']['name']
        course_tup.append(cur_bsid)
        course_tup.append(cur_name)
        course_tup.append(cur_code)
    sql = sql[:-1]
    cursor.execute(sql, course_tup)
    dbObject.commit()

    sql = 'SELECT * from CourseTeacher where teacherid=%s'
    cursor.execute(sql,curcode)
    dic = cursor.fetchall()
    if len(dic) != 0:
        sql = 'UPDATE CourseTeacher SET courseid=%s where teacherid=%s'
    else:
        sql = 'REPLACE INTO CourseTeacher(courseid, teacherid) values'    
        course_teacher_tup = []
        for x in data:
            sql += "(%s,%s),"
            cur_course = x['bsid']
            course_teacher_tup.append(cur_course)
            course_teacher_tup.append(curcode)
        sql = sql[:-1]  
        course_teacher_tup = tuple(course_teacher_tup)
        cursor.execute(sql, course_teacher_tup)
        dbObject.commit()
    return str(data)

@app.route('/api/get_student_books')
def get_student_books():
    sql = 'SELECT b.id as bid, b.name, b.edition, b.publisher, c.name as course, b.price, b.detailInformation, ' +\
    'GROUP_CONCAT(ba.author) as authors ' +\
    'from Book as b ' +\
    'JOIN BookAuthor as ba ' +\
    'JOIN CourseBook as cb ' +\
    'JOIN Course as c on ' +\
    'b.id=ba.bookid and b.id=cb.bookid and c.bsid=cb.courseid ' +\
    'GROUP BY b.id,c.name;'
    cursor.execute(sql)
    dic = cursor.fetchall()
    for i in range(len(dic)):
        dic[i]['price'] = str(dic[i]['price'])
        dic[i]['author'] = dic[i]['authors'].split(',')[0]
    return jsonify(dic)

@app.route('/api/get_class_books')
def get_class_books():
    curclassId = request.args.get('class')
    sql = 'SELECT bookid, SUM(num) as num from StudentBook WHERE classid=%s GROUP BY bookid;'

    #f = open('log.txt','w')
    #f.write(str(request.data))
    #f.close()

    cursor.execute(sql,curclassId)
    dic = cursor.fetchall()

    sql = 'SELECT b.id as bid, b.name, b.edition, b.publisher, c.name as course, b.price, b.detailInformation,'+\
    'GROUP_CONCAT(ba.author) as authors '+\
    'from Book as b '+\
    'JOIN BookAuthor as ba '+\
    'JOIN CourseBook as cb '+\
    'JOIN Course as c on b.id=ba.bookid '+\
    'and b.id=cb.bookid and c.bsid=cb.courseid '+\
    'WHERE b.id in ('
    tup_bid = []
    tup_num = []
    for x in dic:
        sql += '%s,'
        tup_bid.append(x['bookid'])
        tup_num.append(x['num'])
    sql = sql[:-1]
    sql += ') GROUP BY bid,c.name;'

    f = open('log.txt','w')
    f.write(sql)
    f.close()

    tup_bid = tuple(tup_bid)

    cursor.execute(sql, tup_bid)
    inf_dic = cursor.fetchall()
    for i in range(len(inf_dic)):
        inf_dic[i]['price'] = str(inf_dic[i]['price'])
        inf_dic[i]['author'] = inf_dic[i]['authors'].split(',')[0]
        inf_dic[i]['num'] = int(dic[i]['num'])
    return jsonify(inf_dic)

@app.route('/api/update_student_information',methods=['POST'])
def update_student_information():
    data = json.loads(str(request.data,'utf8'))
    curstuId = data['stuId']
    curclassId = data['class']
    sql = 'SELECT * from StudentClass where studentid=%s'
    cursor.execute(sql,curstuId)
    dic = cursor.fetchall()
    if len(dic) != 0:
        sql = 'UPDATE StudentClass SET classid=%s where studentid=%s'
    else:
        sql = 'INSERT IGNORE INTO StudentClass(classid, studentid) values(%s,%s)'    
    cursor.execute(sql, (curclassId, curstuId))
    dbObject.commit()
    return jsonify({'code':200,'message':'success'})

@app.route('/api/save_student_books', methods=['POST'])
def save_student_books():
    data = json.loads(str(request.data,'utf8'))
    if len(data) == 0:
        return
    sql = 'SELECT * from StudentBook where studentid=%s'
    cursor.execute(sql, data[0]['stuId'])
    dic = cursor.fetchone()
    if dic is not None:
        sql = 'DELETE from StudentBook where studentid=%s'
        cursor.execute(sql, data[0]['stuId'])
        dbObject.commit()
    sql = 'INSERT INTO StudentBook(bookid,studentid,num,classid) values'
    tup = []
    for x in data:
        sql += '(%s,%s,%s,%s),'
        tup.append(x['bookid'])
        tup.append(x['stuId'])
        tup.append(x['num'])
        tup.append(x['class'])
    sql = sql[:-1]
    tup = tuple(tup)
    cursor.execute(sql, tup)
    dbObject.commit()
    return jsonify({'code':200,'message':'success'})

@app.route('/api/save_course_books', methods=['POST'])
def save_course_books():
    data = json.loads(str(request.data,'utf8'))
    book = data['book']
    courseid = data['courseid']

    if book['edition'] == '':
        book['edition'] = 1

    
    sql = 'INSERT INTO Book(name,publisher,edition,detailInformation) values(%s,%s,%s,%s)'
    cursor.execute(sql, (book['name'],book['publisher'],book['edition'],book['detailInformation']))
    dbObject.commit();
    
    #TBD: should be REPLACED for efficiency concerns.
    sql = 'SELECT id FROM Book where name=%s and publisher=%s and edition=%s';
    cursor.execute(sql,(book['name'],book['publisher'],book['edition']))
    ans = cursor.fetchone()
    bookid = ans['id']

    book['authors'] = book['authors'].split(',')
    sql = 'INSERT INTO BookAuthor(bookid,author) values'
    author_tup = []
    for author in book['authors']:
        sql += '(%s,%s),'
        author_tup.append(bookid)
        author_tup.append(author)
    author_tup = tuple(author_tup)
    sql = sql[:-1]
    cursor.execute(sql,author_tup)
    dbObject.commit()

    sql = 'INSERT INTO CourseBook(bookid,courseid) values(%s,%s)'
    cursor.execute(sql,(bookid, courseid))
    dbObject.commit()

    return jsonify(ans)

@app.route('/api/update_course_books', methods=['POST'])
def update_course_books():
    data = json.loads(str(request.data,'utf8'))
    sql = 'UPDATE Book SET name=%s,publisher=%s,edition=%s,detailInformation=%s WHERE id=%s;'
    book = data
    if book['edition'] == '':
        book['edition'] = 1
    cursor.execute(sql,(book['name'],book['publisher'],book['edition'],book['detailInformation'],book['id']))
    dbObject.commit()

    sql = 'DELETE FROM BookAuthor WHERE bookid=%s;'
    cursor.execute(sql,book['id'])
    dbObject.commit()

    book['authors'] = book['authors'].split(',')
    sql = 'INSERT INTO BookAuthor(bookid,author) values'
    author_tup = []
    for author in book['authors']:
        sql += '(%s,%s),'
        author_tup.append(book['id'])
        author_tup.append(author)
    author_tup = tuple(author_tup)
    sql = sql[:-1]
    cursor.execute(sql,author_tup)
    dbObject.commit()
    return jsonify({'code':'200', 'msg': 'success'})

@app.route('/api/delete_course_books', methods=['POST'])
def delete_course_books():
    data = json.loads(str(request.data,'utf8'))
    sql = 'DELETE FROM BookAuthor WHERE bookid=%s;'
    cursor.execute(sql,data['bookid'])
    dbObject.commit()
    sql = 'DELETE FROM CourseBook WHERE bookid=%s;'
    cursor.execute(sql,data['bookid'])
    dbObject.commit()
    sql = 'DELETE FROM Book WHERE id=%s;'
    cursor.execute(sql,data['bookid'])
    dbObject.commit()
    return 'ok'

@app.route('/api/get_teacher_information')
def get_teacher_information():
    curteacherId = request.args.get('teacherId')
    sql = 'SELECT c.bsid,c.code,c.name from CourseTeacher JOIN Course as c on c.bsid=courseid where teacherid=%s'
    cursor.execute(sql,curteacherId)
    dic = cursor.fetchall()
    for i in range(len(dic)):
        bsid = dic[i]['bsid']
        sql = 'SELECT b.id,b.name,b.publisher,b.edition,b.price,b.detailInformation,' + \
            'GROUP_CONCAT(ba.author) as authors from CourseBook as cb JOIN Book as b '+\
            'JOIN BookAuthor as ba on cb.bookid=b.id and ba.bookid=b.id and cb.courseid=%s '+\
            'GROUP BY b.id,b.name,b.publisher,b.edition,b.price,b.detailInformation'
        cursor.execute(sql,bsid)
        books = cursor.fetchall()
        for k in range(len(books)):
            books[k]['price'] = str(books[k]['price'])
        dic[i]['books'] = list(books)
    f = open('log.txt','w')
    f.write(str(dic))
    f.close()
    return jsonify(dic)
if __name__ == '__main__':
    app.run(host='0.0.0.0',port=8888)
