from flask import Flask, redirect, url_for, render_template, request, session,flash
from werkzeug.security import check_password_hash, generate_password_hash   
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re

app = Flask(__name__)
# Enter your database connection details below
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'admin'
app.config['MYSQL_DB'] = 'trivtime'

# Intialize MySQL
mysql = MySQL(app)
# Change the value of SECRET_KEY to a long random string.
app.secret_key = 'isasdasdsl'
@app.route('/')
def home():
     # Check if user is loggedin
    if 'loggedin' in session:
        # User is loggedin show them the home page
        return render_template('home.html')
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    username = ''
    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        # Get the data submitted by user in the form, and store in relevant variables
        username = request.form['username']
        password = request.form['password']
        # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM USER WHERE username = %s',(username,))
        account = cursor.fetchone() 
        print(account)
        cursor.close()
        
        if not account:
            flash('Incorrect username')
            return render_template('login.html')
        
        # If account exists
        if check_password_hash(account['Password'], password):
            # If account exists, create session data, we can access this data in other routes
            session['loggedin'] = True
            session['id'] = account['USERID']
            session['username'] = account['UserName']
            session['email'] = account['EMAIL']
            session["LVL"] = account['LVL']
            session['elo'] = account['Elo']
            session['room'] = 0
            # redirect user to home page for successful login
            return redirect(url_for('home'))
        else:
            # Account does not exist or username/password incorrect, flash error message
            flash('Incorrect password!')
    #some error in logging in. Redirect back to login page with error message
    return render_template('login.html')
 
@app.route('/logout')
def logout():
   # Remove session data, this will log the user out
   session.clear()
   # Redirect to login page
   return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    # Check if "username", "password" and "email" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM USER WHERE username = %s', (username,))
        account = cursor.fetchone()
        # If account exists show error and validation checks
        if account:
            #Use flash function to flash error message
            flash('Account already exists!')
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            #checking email format at server side. This is slightly more 'rigourous' than the client side validation.
            #for example a@a will pass the client side email validation, but will fail the server side validation below.
            flash('Invalid email address!')
        elif not re.match(r'[A-Za-z0-9]+', username):
            #ensures username only contains alphabets and digits.
            flash('Username must contaxin only characters and numbers!')
        else:

            cursor.execute('SELECT MAX(USERID) FROM USER')
            numbers = cursor.fetchone()
            print(int(numbers['MAX(USERID)'])+1)
            
            # Account does not exists and the form data is valid, now insert new account into accounts table
            cursor.execute('INSERT INTO USER VALUES (%s, %s, %s, %s,%s,%s,%s,%s,%s)', ((int(int(numbers['MAX(USERID)'])+1)),username,int( 1000) ,int( 0) , int(1) , int(1000 ),int( 0 ),generate_password_hash( password), email,))
            mysql.connection.commit() #commit the insertion
            #Use flash function to flash a successfully reigstered message
            flash('Congratulations, you have successfully registered. Try logging in now!')
            #redirects to login page with successful message
            return redirect(url_for('login'))

    # Show registration form with relevant message (if any)
    return render_template('register.html')

@app.route('/profile',  methods=['GET', 'POST'])
def profile():
    print(request.form)
    if  'loggedin'  in session:

        if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            password = request.form['password']
            email = request.form['email']
            if not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            #checking email format at server side. This is slightly more 'rigourous' than the client side validation.
            #for example a@a will pass the client side email validation, but will fail the server side validation below.
                flash('Invalid email address!')
            else:   
                cursor.execute('UPDATE accounts set password = %s, email = %s where id = %s', (generate_password_hash( password), email,session['id'],))
 

                session['email'] =email
                mysql.connection.commit() #commit the insertion
                #Use flash function to flash a successfully reigstered message
                flash('Congratulations, you have successfully updated.')
                #redirects to login page with successful message
                return render_template('profile.html')
            return render_template('profile.html')
        return render_template('profile.html')
    else:
        return render_template('login.html')
@app.route('/search',  methods=['GET', 'POST'])
def search():
    # Check if user is loggedin
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM question')
        fields = ["Questiontext","QType","Difficulty","Category"]
        if request.method == 'POST':
            category =  request.form.get('category')
            print(request.form)
            if category in fields: #check that category is indeed a valid category (prevent SQL injection)
                search = '%' + request.form['search'] + '%'
                query = 'SELECT * FROM question WHERE ' + category + ' like %s' 
                cursor.execute(query, (search,))
                questions = cursor.fetchall()
                print(questions)
                return render_template('search.html',questions=questions,fields = fields)
         #get all books record from books table
        questions = cursor.fetchall() #fetch all records
        cursor.close()
        return render_template('search.html',questions=questions,fields = fields) #pass books data to search.html
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))
@app.route('/play',methods = ['GET','POST'])
def play():
    if 'loggedin' in session:
        
        return render_template('play.html')
    return render_template('login.html')
@app.route('/room',methods = ['GET','POST'])
def room():
    if 'loggedin' in session:
        if request.method == 'POST':
            return render_template('room.html')
        return render_template('room.html')
        
    return render_template('login.html')
@app.route('/room/create',methods = ['GET','POST'])
def create():
    if 'loggedin' in session:
        if request.method == 'POST':
            id = request.form.get("id")
            num = request.form.get("num")
            print(request.form)
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute("INSERT INTO ROOM VALUES (NULL, %s , %s, %s,1)", (id,session['id'],num,))
            mysql.connection.commit()
            cursor.execute('SELECT MAX(ROOMID) FROM ROOM')
            ROOMID = cursor.fetchone()
            session['room'] = int(ROOMID)
            checkROOM();
            cursor.execute("INSERT INTO JOINEDROOM VALUES (NULL,%s,%s)",(session["id"],ROOMID,))

            players = selectAllPlayers(ROOMID);
            cursor.execute("Select DISTINCT CATEGORY FROM QUESTION")
            category = cursor.fetchall()
            return render_template("inRoom.html" ,players = players,host = session['id'], category = category)
            
        else:
            return render_template('create.html')
    return render_template('login.html')
def checkROOM():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("DELETE * FROM JOINEDROOM WHERE USERID = &s", (session["id"],))
    mysql.connection.commit()
    cursor.close()
    return
def selectAllPlayers(ROOMID):
    cursor =  mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM USER WHERE USERID in (Select USERID from joinedroom where ROOMID = &s",(ROOMID,) )
    p = cursor.fetchall()
    cursor.close()
    return p
@app.route('/game',methods = ['GET','POST'])
def game():

    return render_template('game.html')
if __name__ == '__main__':
    app.run(debug = True)