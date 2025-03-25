from flask import Flask,render_template,request,redirect,url_for,session,flash
import sqlite3
import os
import base64
import cv2
import numpy as np
import shutil
import joblib
import glob
from flask import jsonify
from PIL import Image




app=Flask(__name__)
app.secretkey="fgdfgdfgfgd"
database="12.jpgdb"
face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
def createtable():
    conn=sqlite3.connect(database)
    cursor=conn.cursor()
    cursor.execute("create table if not exists parents_details (id integer primary key autoincrement, name text, email text unique,phone text, password text)")
    cursor.execute("create table if not exists volunteer_details (id integer primary key autoincrement, name text, email text unique,phone text, password text)")
    cursor.execute("create table if not exists child_details(id integer primary key autoincrement, childname text, parentname text,phone text, email text, address text, aadhar text, imagefile1 blob,imagefile2 blob,imagefile3 blob,imagefile4 blob)")
    cursor.execute("create table if not exists accept_table (id integer primary key autoincrement, childname text, parentname text,phone text, email text, address text, aadhar text, imagefile1 blob,imagefile2 blob,imagefile3 blob,imagefile4 blob)")

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
         return "Details Submitted Successfully"
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
         basepath = os.path.dirname(__file__)
         file_path = os.path.join(basepath,"uploads/missedchild1.jpg")
         imagefile1.save("uploads/missedchild.jpg")
         imagefile2= request.files['image2']
         blobdata2= imagefile2.read()
         basepath = os.path.dirname(__file__)
         file_path = os.path.join(basepath,"uploads/missedchild2.jpg")
         imagefile2.save("uploads/missedchild1.jpg")
         imagefile3= request.files['image3']
         blobdata3= imagefile3.read()
         basepath = os.path.dirname(__file__)
         file_path = os.path.join(basepath,"uploads/missedchild3.jpg")
         imagefile3.save("uploads/missedchild3.jpg")
         imagefile4= request.files['image4']
         blobdata4= imagefile4.read()
         basepath = os.path.dirname(__file__)
         file_path = os.path.join(basepath,"uploads/missedchild4.jpg")
         imagefile4.save("uploads/missedchild4.jpg")
         con=sqlite3.connect(database)
         cur=con.cursor()
         cur.execute("insert into child_details(childname, parentname, email, phone, address, aadhar, imagefile1,imagefile2,imagefile3,imagefile4)values(?,?,?,?,?,?,?,?,?,?)",(childname, parentname, email, phone, address, aadhar, blobdata1,blobdata2,blobdata3,blobdata4))
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





@app.route("/accept_child", methods=["POST"])
def accept_child():
    if request.method=="POST":
        try:
            child_id = request.form['number']
            print("Received child ID:", child_id)  # Add this line
            if not child_id:
                raise Exception("Child ID is missing")
            conn = sqlite3.connect(database)
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM child_details WHERE id = ?', (child_id,))
            child_data = cursor.fetchone()
            print("1")
            destination_folder = "training_data_folder"
            if not child_data:
                raise Exception("Child data not found")
            cursor.execute('INSERT INTO accept_table VALUES (?, ?, ?, ?, ?, ?, ?, ?,?,?,?)',child_data)
            for i in range(1, 5):  
                cursor.execute(f'SELECT imagefile{i} FROM child_details WHERE id = ?', (child_id,))
                result = cursor.fetchone()
                print(i)
                if result:
                    image_path = result[0]
                    print(image_path)
                    if image_path:
                        destination_path = os.path.join(destination_folder,f'{child_id}_{i}.jpg')
                        print(destination_path)
                        print("not valid path")
                    try:
                        shutil.copy(image_path, destination_path)
                        print(f'Image{i} copied to {destination_path}')
                    except Exception as e:
                        print("Error copying image:", str(e))
            cursor.execute('DELETE FROM child_details WHERE id = ?', (child_id,))
            conn.commit()
            conn.close()
            return render_template('details.html')
        except Exception as e:           
           print("Error:", str(e))  # Add this line
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

@app.template_filter('b64encode')
def base64_encode(data):
    return base64.b64encode(data).decode('utf-8')




def track_image():
    detector = dlib.get_frontal_face_detector()
    training_data_folder = 'training_data_folder'
    predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")
    face_recognizer = dlib.face_recognition_model_v1("dlib_face_recognition_resnet_model_v1.dat")
    face_encodings = []
    labels = []
    for person_name in os.listdir(training_data_folder):
        person_folder = os.path.join(training_data_folder, person_name)
        if os.path.isdir(person_folder):
            person_id = int(person_name.replace('person', ''))  # Extract the person's ID
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

    cap = cv2.VideoCapture(0)

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = detector(gray)

        for face in faces:
            shape = predictor(gray, face)
            face_encoding = face_recognizer.compute_face_descriptor(frame, shape)
            distances = np.linalg.norm(face_encodings - face_encoding, axis=1)
            min_distance_idx = np.argmin(distances)
            min_distance = distances[min_distance_idx]
            print(min_distance_idx)

            if min_distance < 0.5:
                label = labels[min_distance_idx]
            else:
                label = "Unknown"

            x, y, w, h = face.left(), face.top(), face.width(), face.height()
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(frame, f'Person {label}', (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

        cv2.imshow('Face Recognition', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()



@app.route('/track', methods=['GET'])
def track():
    return render_template('track.html')

@app.route('/tracking', methods=['POST'])
def tracking():
    if request.method == 'POST':       
            track_image()
            return render_template('index.html')
    return render_template('track.html')






if __name__=="__main__":
    app.run(port=900,debug=False)





