#Import Flask Library
from flask import Flask, render_template, request, session, url_for, redirect
import pymysql.cursors

#Initialize the app from Flask
app = Flask(__name__)

#Configure MySQL
conn = pymysql.connect(host='localhost',
                       port = 3306,
                       user='root',
                       password='',#sportsmanagement
                       db='SportsManagement',
                       charset='utf8mb4',
                       cursorclass=pymysql.cursors.DictCursor)

#Define a route to hello function
@app.route('/')
def hello():
    return render_template('design.html')

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
        cursor = conn.cursor()
        query = 'SELECT firstName FROM users WHERE username = %s'
        cursor.execute(query, (username))
        fname = cursor.fetchone()
        cursor.close()
        session['fname'] = fname
        return render_template('athleteHome.html', fname=fname)
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
            cursor = conn.cursor()
            query = 'SELECT firstName FROM users WHERE username = %s'
            cursor.execute(query, (username))
            fname = cursor.fetchone()
            cursor.close()
            session['fname'] = fname
            return render_template('coachHome.html', fname=fname)
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
                cursor = conn.cursor()
                query = 'SELECT firstName FROM users WHERE username = %s'
                cursor.execute(query, (username))
                fname = cursor.fetchone()
                cursor.close()
                session['fname'] = fname
                return render_template('administratorHome.html', fname=fname)
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
        return render_template('register.html', error=error)
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
        return render_template('design.html')

@app.route('/admin')
def admin():
    fname = session['fname']
    return render_template('administratorHome.html', fname=fname)

@app.route('/athlete')
def athlete():
    fname = session['fname']
    return render_template('athleteHome.html', fname=fname)

@app.route('/coach')
def coach():
    fname = session['fname']
    return render_template('coachHome.html', fname=fname)


@app.route('/manageClasses')
def manageClasses():
    user = session['username']
    cursor = conn.cursor()
    query1 = 'SELECT coach, day, time, sport FROM Classes WHERE athlete = %s' # configure
    cursor.execute(query1, user) # add parameters
    data1 = cursor.fetchall() # list of all enrolled classes

    query2 = 'SELECT name FROM Sports'
    cursor.execute(query2)
    data2 = cursor.fetchall()

    query3 = 'SELECT sport FROM Classes WHERE athlete = %s'
    cursor.execute(query3, (user))
    enrolledSports = cursor.fetchall()

    query4 = 'SELECT day FROM Classes WHERE athlete = %s'
    cursor.execute(query4, (user))
    enrolledDays = cursor.fetchall()

    query5 = 'SELECT time FROM Classes WHERE athlete = %s'
    cursor.execute(query5, (user))
    enrolledTimes = cursor.fetchall()

    cursor.close()
    return render_template('manageClasses.html', registeredClasses=data1, sports=data2, enrolledSport=enrolledSports, enrolledDay=enrolledDays, enrolledTime=enrolledTimes, error=request.args.get('error'))

@app.route('/enrollInClass')
def enrollInClass():
    user = session['username']
    cursor = conn.cursor()

    Sport = request.args['sport']
    Day =  request.args['day']
    Time =  request.args['time']

   
    query2 = 'SELECT coach FROM Sports WHERE name = %s'
    cursor.execute(query2, Sport)
    Coach = cursor.fetchone()

    query1 = 'SELECT * FROM Classes WHERE coach = %s AND day = %s AND time = %s'
    cursor.execute(query1, (Coach['coach'],Day,Time))
    data = cursor.fetchone()

    if(data):
        error = "Class not available"
        return (redirect(url_for('manageClasses', error=error)))

    query1 = 'SELECT * FROM Classes WHERE athlete = %s AND day = %s AND time = %s'
    cursor.execute(query1, (user,Day,Time))
    data1 = cursor.fetchone()

    if(data1):
        error = "Class not available"
        return (redirect(url_for('manageClasses', error=error)))



    ins = 'INSERT INTO Classes VALUES (%s, %s, %s, %s, %s)'
    cursor.execute(ins, (user, Coach['coach'], Day, Time, Sport))

    conn.commit()

    cursor.close()

    return redirect(url_for('manageClasses'))


@app.route('/dropClass')
def dropClass():
    user = session['username']
    cursor = conn.cursor()

    sport = request.args['enrolledSport']
    day = request.args['enrolledDay']
    time = request.args['enrolledTime']    

    drop = 'DELETE FROM Classes WHERE athlete = %s AND time = %s AND day = %s AND sport = %s'
    cursor.execute(drop, (user, time, day, sport))
    conn.commit()

    cursor.close()

    # If class does not exist raise error

    return redirect(url_for('manageClasses'))

@app.route('/manageEquipments')
def manageEquipments():
    user = session['username']
    cursor = conn.cursor()
    query1 = 'SELECT eq.ID, eq.Name FROM checkedEquipments AS cE JOIN Equipments AS eq ON ce.equipmentID = eq.ID WHERE cE.userID = %s'  
    cursor.execute(query1, user)  
    data1 = cursor.fetchall()  # list of all checked equipments

    query2 = 'SELECT name FROM Equipments'
    cursor.execute(query2)
    data2 = cursor.fetchall()

    cursor.close()
    return render_template('manageEquipments.html', checkedEquipments=data1, equipments=data2, error=request.args.get('error'), error2=request.args.get('error2'))

@app.route('/checkoutEquipment')
def checkoutEquipment():
    user = session['username']
    equipmentToCheckout =  request.args['equipments']
    cursor = conn.cursor()

    query1 = 'SELECT id FROM Equipments WHERE name = %s'
    cursor.execute(query1, equipmentToCheckout)
    data1 = cursor.fetchone()

    query2 = 'SELECT * FROM CheckedEquipments WHERE equipmentID = %s'
    cursor.execute(query2, data1['id'])
    data2 = cursor.fetchone()

    if(data2):
        error = "Equipment not available."
        return redirect(url_for('manageEquipments', error=error))

    ins = 'INSERT INTO CheckedEquipments (userID, equipmentID) VALUES (%s, %s)'
    cursor.execute(ins, (user, data1['id']))
    conn.commit()

    return redirect(url_for('manageEquipments'))

@app.route('/returnEquipment')
def returnEquipment():
    user = session['username']
    equipmentToReturn = request.args['equipmentToReturn']
    cursor = conn.cursor()
    
    query1 = 'SELECT id FROM Equipments WHERE name = %s'
    cursor.execute(query1, equipmentToReturn)
    data1 = cursor.fetchone()

    if (data1==None):
        error = "Equipment not available."
        return redirect(url_for('manageEquipments', error2=error))

    query2 = 'SELECT * FROM CheckedEquipments WHERE equipmentID = %s AND userID = %s'
    cursor.execute(query2, (data1['id'], user))
    data2 = cursor.fetchone()

    if(data2==None):
        error = "You do not have this equipment checked out."
        return redirect(url_for('manageEquipments', error2=error))

    remove = 'DELETE FROM CheckedEquipments WHERE equipmentID = %s AND userID = %s'
    cursor.execute(remove, (data1['id'], user))
    conn.commit()
    return redirect(url_for('manageEquipments'))

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
    return render_template('displayFinancialReport.html', coachSalaries=data, totalCoachSalary=data1, athleteFees=data2, totalAthleteFees=data3, total=data4)

@app.route('/viewRoster')
def viewRoster(): #Displays the athletes being coached by a selected coach
    user = session['username']
    cursor = conn.cursor()

    query1 = 'SELECT firstName FROM users WHERE username = %s'
    cursor.execute(query1,user)
    coachID = cursor.fetchone()

    query = 'SELECT * FROM classes WHERE coach = %s'
    cursor.execute(query,coachID['firstName'])
    data1 = cursor.fetchall()

    cursor.close()
    return render_template('viewRoster.html', athletes=data1)

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
