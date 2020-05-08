#Import Flask Library
from flask import Flask, render_template, request, session, url_for, redirect
import pymysql.cursors

#Initialize the app from Flask
app = Flask(__name__)

#Configure MySQL
conn = pymysql.connect(host='localhost',
                       port = 3306,
                       user='root',
                       password='',
                       db='SportsManagement',
                       charset='utf8mb4',
                       cursorclass=pymysql.cursors.DictCursor)

#Define a route to hello function
@app.route('/')
def hello():
    return render_template('index.html')

#Define route for login
@app.route('/login')
def login():
    return render_template('login.html')

#Define route for register
@app.route('/register')
def register():
    return render_template('register.html')

#Authenticates the login
@app.route('/loginAuth', methods=['GET', 'POST'])
def loginAuth():
    #grabs information from the forms
    username = request.form['username']
    password = request.form['password']

    #cursor used to send queries
    cursor = conn.cursor()
    #executes query
    query = 'SELECT * FROM users WHERE username = %s and password = %s and role = %s'
    cursor.execute(query, (username, password, 'athlete'))
    #stores the results in a variable
    data = cursor.fetchone()
    #use fetchall() if you are expecting more than 1 data row
    cursor.close()
    error = None
    if(data):
        #creates a session for the the user
        #session is a built in
        session['username'] = username
        return render_template('athleteHome.html', username=username)
    else:
        cursor = conn.cursor()
        # executes query
        query = 'SELECT * FROM users WHERE username = %s and password = %s and role = %s'
        cursor.execute(query, (username, password, 'coach'))
        # stores the results in a variable
        data = cursor.fetchone()
        # use fetchall() if you are expecting more than 1 data row
        cursor.close()
        if (data):
            # creates a session for the the user
            # session is a built in
            session['username'] = username
            return render_template('coachHome.html', username=username)
        else:
            cursor = conn.cursor()
            # executes query
            query = 'SELECT * FROM users WHERE username = %s and password = %s and role = %s'
            cursor.execute(query, (username, password, 'admin'))
            # stores the results in a variable
            data = cursor.fetchone()
            # use fetchall() if you are expecting more than 1 data row
            cursor.close()
            if (data):
                # creates a session for the the user
                # session is a built in
                session['username'] = username
                return render_template('administratorHome.html', username=username)
            else:
                #returns an error message to the html page
                error = 'Invalid login or username'
                return render_template('login.html', error=error)

#Authenticates the register
@app.route('/registerAuth', methods=['GET', 'POST'])
def registerAuth():
    #grabs information from the forms
    username = request.form['username']
    password = request.form['password']
    firstName = request.form['firstName']
    lastName = request.form['lastName']
    phoneNumber = request.form['phoneNumber']
    email = request.form['email']
    role = request.form['role']

    #cursor used to send queries
    cursor = conn.cursor()
    #executes query
    query = 'SELECT * FROM users WHERE username = %s'
    cursor.execute(query, (username))
    #stores the results in a variable
    data = cursor.fetchone()
    #use fetchall() if you are expecting more than 1 data row
    error = None
    if(data):
        #If the previous query returns data, then user exists
        error = "This user already exists"
        return render_template('register.html', error = error)
    else:
        ins = 'INSERT INTO users VALUES(%s, %s, %s, %s, %s, %s, %s)'
        cursor.execute(ins, (username, password, firstName, lastName, phoneNumber, email, role))
        conn.commit()
        cursor.close()
        if(role == 'athlete'):
            cursor = conn.cursor()
            ins = 'INSERT INTO membershipfee VALUES(%s, %s)'
            cursor.execute(ins, (username, 100))
            conn.commit()
            cursor.close()
        elif(role == 'coach'):
            cursor = conn.cursor()
            ins = 'INSERT INTO salary VALUES(%s, %s)'
            cursor.execute(ins, (username, 100))
            conn.commit()
            cursor.close()
        else:
            return render_template('register.html', error=error)
        return render_template('index.html')

@app.route('/manageClasses')
def manageClasses():
    user = session['username']
    cursor = conn.cursor()
    query1 = 'SELECT sportID, coachID, time FROM Teaches WHERE athleteID = %s' # configure
    cursor.execute(query1, user) # add parameters
    data1 = cursor.fetchall() # list of all enrolled classes
    cursor.close()
    return render_template('manageClasses.html', registeredClasses=data1)

@app.route('/enrollInClass')
def enrollInClass():
    classToEnroll = request.args['classToEnroll']
    # If already enrolled in class raise error.
    # If taking another class during that day raise error

@app.route('/dropClass')
def dropClass():
    classToDrop = request.args['classToDrop']
    # If class does not exist raise error

@app.route('/manageEquipments')
def manageEquipments():
    user = session['username']
    cursor = conn.cursor()
    query1 = 'needs config'  # configure
    cursor.execute(query1)  # add parameters
    data1 = cursor.fetchall()  # list of all enrolled classes
    cursor.close()
    return render_template('manageEquipments.html', checkedEquipments=data1)

@app.route('/checkoutEquipment')
def checkoutEquipment():
    equipmentToCheckout = request.args['equipmentToCheckout']

@app.route('/returnEquipment')
def returnEquipment():
    equipmentToReturn = request.args['equipmentToReturn']

@app.route('/updateCoachSalary')
def updateCoachSalary():
    #get all the coach info
    cursor = conn.cursor()
    query = 'SELECT * FROM salary'
    cursor.execute(query)
    data = cursor.fetchall()
    cursor.close()
    return render_template('updateCoachSalary.html', coaches=data)

@app.route('/updateSalary', methods=['GET', 'POST'])
def updateSalary():
    coachID = request.args['coachID']
    newWage = request.args['newWage']
    cursor = conn.cursor()
    upd = 'UPDATE salary SET wage = %s WHERE coachID = %s'
    cursor.execute(upd, (newWage, coachID))
    conn.commit()
    cursor.close()
    return redirect(url_for('admin'))

@app.route('/displayFinancialReport')
def displayFinancialReport(): #Takes data from salary and membership tables to calculate total wage and fees
    cursor = conn.cursor()
    query = 'SELECT * FROM salary'
    cursor.execute(query)
    data = cursor.fetchall()
    query1 = 'SELECT SUM(wage) AS totalWage FROM salary'
    cursor.execute(query1)
    data1 = cursor.fetchall()
    query2 = 'SELECT * FROM membershipfee'
    cursor.execute(query2)
    data2 = cursor.fetchall()
    query3 = 'SELECT SUM(fee) as totalFee FROM membershipfee'
    cursor.execute(query3)
    data3 = cursor.fetchall()
    query4 = 'SELECT (SELECT SUM(fee) FROM membershipfee) - (SELECT SUM(wage) FROM salary) AS totalWage'
    cursor.execute(query4)
    data4 = cursor.fetchall()
    cursor.close()
    return render_template('displayFinancialReport.html', coachSalaries = data, totalCoachSalary = data1, athleteFees = data2, totalAthleteFees = data3, total = data4)

@app.route('/logout')
def logout():
    session.pop('username')
    return redirect('/')
        
app.secret_key = 'some key that you will never guess'
#Run the app on localhost port 5000
#debug = True -> you don't have to restart flask
#for changes to go through, TURN OFF FOR PRODUCTION
if __name__ == "__main__":
    app.run('127.0.0.1', 5000, debug = True)
