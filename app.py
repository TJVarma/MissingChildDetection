from flask import Flask,render_template,request,redirect,url_for,session,flash
import sqlite3
import os
import base64
import cv2
import numpy as np
import dlib
import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import smtplib
from email.utils import formataddr
app=Flask(__name__)
app.secretkey="fgdfgdfgfgd"
database="finalreport.db"
face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
def createtable():
    conn=sqlite3.connect(database)
    cursor=conn.cursor()
    cursor.execute("create table if not exists parents_details (id integer primary key autoincrement, name text, email text unique,phone text, password text)")
    cursor.execute("create table if not exists child_details(id integer primary key autoincrement, childname text, parentname text,phone text, email text, address text, aadhar text, imagefile1 blob,imagefile2 blob,imagefile3 blob,imagefile4 blob,imagefile5 blob)")
    cursor.execute("create table if not exists accept_table (id integer primary key autoincrement, childname text, parentname text,phone text, email text, address text, aadhar text, imagefile1 blob,imagefile2 blob,imagefile3 blob,imagefile4 blob,imagefile5 blob)")
    cursor.execute('''create table if not exists table9 (id integer primary key autoincrement ,child_id integer , childname text, parentname text,email text,phone text,  address text, aadhar text, location text,date DATE
                                      )''')
    cursor.execute('''create table if not exists table10 (id integer primary key autoincrement,child_id integer , childname text, parentname text,email text,phone text,  address text, aadhar text, location text,date DATE,missingchild blob
                                      )''')

    print("finish")
    conn.commit()
    conn.close()


createtable()   

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/parents_details',methods=["GET","POST"])
def parents_details():
    if request.method=="POST":
         name=request.form['name']
         phone=request.form['phone']
         email=request.form['email']
         password=request.form['password']
         con=sqlite3.connect(database)
         cur=con.cursor()
         cur.execute("insert into parents_details(name, phone, email, password)values(?,?,?,?)",(name, phone, email, password))
         con.commit()
         return render_template('index.html')
    return render_template('parents_details.html')


@app.route('/parent_login',methods = ["GET","POST"])
def parent_login():
    if request.method=="POST":
        email=request.form['email']
        password=request.form['password']
        con=sqlite3.connect(database)
        cur=con.cursor()
        cur.execute("select * from parents_details where email=? and password=?",(email,password))
        data=cur.fetchone()
        if data is None:
                return "failed"        
        else:
             return render_template('child_details.html')
    return render_template('parent_login.html')



@app.route('/child_details',methods=["GET","POST"])
def child_details():
    if request.method=="POST":
         childname=request.form['childname']
         parentname=request.form['parentname']
         phone=request.form['phone']
         email=request.form['email']
         address=request.form['address']
         aadhar=request.form['aadhar']
         imagefile1= request.files['image1']
         blobdata1= imagefile1.read()
         imagefile2= request.files['image2']
         blobdata2= imagefile2.read()
         imagefile3= request.files['image3']
         blobdata3= imagefile3.read()
         imagefile4= request.files['image4']
         blobdata4= imagefile4.read()
         imagefile5= request.files['image5']
         blobdata5= imagefile5.read()
         con=sqlite3.connect(database)
         cur=con.cursor()
         cur.execute("insert into child_details(childname, parentname, email, phone, address, aadhar, imagefile1,imagefile2,imagefile3,imagefile4,imagefile5)values(?,?,?,?,?,?,?,?,?,?,?)",(childname, parentname, email, phone, address, aadhar, blobdata1,blobdata2,blobdata3,blobdata4,blobdata5))
         con.commit()
         return render_template('index.html')
    return render_template('child_details.html')



ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'admin'

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            return redirect('/details')
    return render_template('admin.html')



@app.route('/details',methods=['GET', 'POST'])
def details():
    if request.method == 'POST':
        print("details")
    return render_template('details.html')

@app.route('/view_pa', methods=["GET","POST"])
def view_pa():
    con=sqlite3.connect(database)
    cur=con.cursor()
    cur.execute("select * from child_details")
    results = cur.fetchall()
    con.commit()
    return render_template('view_pa.html', results=results)

@app.template_filter('b64encode')
def base64_encode(data):
    return base64.b64encode(data).decode('utf-8')


@app.route('/accept_child', methods=["GET","POST"])
def accept_child():
    if request.method == "POST":
        try:
            child_id = request.form['number']
            print("Received child ID:", child_id)  # Add this line
            if not child_id:
                raise Exception("Child ID is missing")

            conn = sqlite3.connect(database)
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM child_details WHERE id = ?', (child_id,))
            child_data = cursor.fetchone()
            cursor.execute('INSERT INTO accept_table VALUES (?, ?, ?, ?, ?, ?, ?, ?,?,?,?,?)',child_data)
            if not child_data:
                raise Exception("Child data not found")
            cursor.execute("SELECT imagefile1,imagefile2,imagefile3,imagefile4  FROM child_details WHERE id = ?", (child_id,))
            image_file_names = cursor.fetchone()
            print(len(image_file_names))
            folder_path = os.path.join('image_folder', child_id)
            os.makedirs(folder_path, exist_ok=True)
            print(folder_path)
            for i, image_file_data in enumerate(image_file_names):
                if image_file_data:
                    image_path = os.path.join(folder_path, f'{child_id}_{i + 1}.jpg')
                    with open(image_path, 'wb') as image_file:
                        image_file.write(image_file_data)
                        print("success")
            cursor.execute('DELETE FROM child_details WHERE id = ?', (child_id,))
            conn.commit()
            conn.close()
                    
            return render_template('details.html')
        except Exception as e:           
           print("Error:", str(e))  
           return jsonify({"success": False, "error": str(e)})

    return render_template('admin.html')



@app.route('/accept_table', methods=["GET","POST"])
def accept_table():
    con=sqlite3.connect(database)
    cur=con.cursor()
    cur.execute("select * from accept_table")
    results = cur.fetchall()
    con.commit()
    return render_template('accept_table.html', results=results)

a=[]



def recognize_faces():
    detector = dlib.get_frontal_face_detector()
    training_data_folder = 'image_folder'
    predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")
    face_recognizer = dlib.face_recognition_model_v1("dlib_face_recognition_resnet_model_v1.dat")
    face_encodings = []
    labels = []
    for person_name in os.listdir(training_data_folder):
        person_folder = os.path.join(training_data_folder, person_name)
        if os.path.isdir(person_folder):
            person_id = int(person_name.replace('person', ''))  
            for filename in os.listdir(person_folder):
                if filename.endswith(('.jpg', '.jpeg', '.png')):
                    image_path = os.path.join(person_folder, filename)
                    image = cv2.imread(image_path)
                    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                    faces = detector(gray)

                    for face in faces:
                        shape = predictor(gray, face)
                        face_encoding = face_recognizer.compute_face_descriptor(image, shape)
                        face_encodings.append(face_encoding)
                        labels.append(person_id)
    labels = np.array(labels)
    face_encodings = np.array(face_encodings)

    print("train")

    cap = cv2.VideoCapture(0)
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = detector(gray)
        print("finish")

        for face in faces:
            shape = predictor(gray, face)
            face_encoding = face_recognizer.compute_face_descriptor(frame, shape)
            distances = np.linalg.norm(face_encodings - face_encoding, axis=1)
            min_distance_idx = np.argmin(distances)
            min_distance = distances[min_distance_idx]
            print(min_distance)

            if min_distance < 0.5:
                label = labels[min_distance_idx]
                #print(label)
                imagefolder=f"new/{label}.jpg"
                image = cv2.imwrite(imagefolder, frame)
            else:
                label = "Unknown"

            x, y, w, h = face.left(), face.top(), face.width(), face.height()
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(frame, f'Person {label}', (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
            con=sqlite3.connect(database)
            cursor=con.cursor()
            cursor.execute("SELECT id  FROM accept_table ")
            data=cursor.fetchall()
            print(data,label)
            if label in data:
                print("success")
                label1=int(label)
                a.append(label1)
                print("labl==",a)
                cursor.execute("SELECT id,childname, parentname, email, phone, address, aadhar  FROM accept_table where id = ?",( label1,))
                data1=cursor.fetchone()
                print(data1,"data")
                location="chennai"
                currentdate =datetime.datetime.now()
                print(currentdate)
                data_to_insert = data1 + (location , currentdate,)
                cursor.execute('INSERT  INTO table9 (child_id, childname, parentname,  email, phone,address, aadhar, location,date)  VALUES (?,?, ?, ?, ?, ?, ?, ?,?)',data_to_insert)
                con.commit()
                cursor.close()
                con.close()
        cv2.imshow('Face Recognition', frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
             print("q")
             con=sqlite3.connect(database)
             cursor=con.cursor()
             cursor.execute("SELECT * FROM table9 WHERE child_id = ? ORDER BY id DESC LIMIT 1", (a[-1],))
             data1 = cursor.fetchone()
             print(len(data1))
             print(data1)
             image_folder=f"new/{data1[1]}.jpg"
             image_data = cv2.imread(image_folder)
             image_bytes = cv2.imencode(f'{data1[1]}.jpg', image_data)[1].tobytes()
             data_to_insert1 = data1 + (image_bytes,)
             cursor.execute('INSERT  INTO table10 (id, child_id, childname, parentname, email, phone, address, aadhar, location,date,missingchild)  VALUES (?,?, ?, ?, ?, ?, ?, ?,?,?,?)',data_to_insert1)
             print(data1[4],"email")
             email=data1[4]
             smtp_server = 'smtp.example.com'
             smtp_port = 587
             sender_email = 'diwa.2801@gmail.com'
             sender_password = 'furgqbokcooqfjkf'
             receiver_email =email
             host = "smtp.gmail.com"
             mmail = "diwa.2801@gmail.com"        
             hmail = email
             sender_name= "admin"
             receiver_name=data1[3]
             msg = MIMEMultipart()
             subject = "found your child"
             text =f"We found one missing  child in {data1[8]} at {data1[9]}, \nchildname:{data1[2]}, \nparentname:{data1[3]},\nparentaddress:{data1[6]},\nparentmobileno{data1[5]}"
##             msg = MIMEText(text, 'plain')
             msg.attach(MIMEText(text, 'plain'))
             image_attachment = MIMEImage(image_bytes, name=f'{data1[1]}.jpg')
             msg.attach(image_attachment)
             msg['To'] = formataddr((receiver_name, hmail))
             msg['From'] = formataddr((sender_name, mmail))
             msg['Subject'] = 'Respected sir/mam  ' 
             server = smtplib.SMTP(host, 587)
             server.ehlo()
             server.starttls()
             password = " furgqbokcooqfjkf"
             server.login(mmail, password)
             server.sendmail(mmail, [hmail], msg.as_string())
             server.quit()
             send="send"
             print(send)
             con.commit()
             cursor.close()
             con.close()
             break

    cap.release()
    cv2.destroyAllWindows()


@app.route('/track', methods=['GET'])
def track():
    return render_template('track.html')

@app.route('/tracking', methods=['POST'])
def tracking():
    if request.method == 'POST':       
            recognize_faces()
            return render_template('index.html')
    return render_template('track.html')



@app.route('/update', methods=["GET","POST"])
def update():
    con=sqlite3.connect(database)
    cursor=con.cursor()
    cursor.execute("SELECT * FROM table10")
    data = cursor.fetchall()
    for  i in data:
        print(i)
##    print(data)
    return render_template('update.html', result=data)











if __name__=="__main__":
    app.run(port=800,debug=False)





