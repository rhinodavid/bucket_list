from flask import Flask, render_template, json, request
from flaskext.mysql import MySQL
from werkzeug import generate_password_hash, check_password_hash

app = Flask(__name__)

mysql = MySQL()

# MySql configuration
app.config['MYSQL_DATABASE_USER'] = 'bucketlist'
app.config['MYSQL_DATABASE_PASSWORD'] = 'bucketlist'
app.config['MYSQL_DATABASE_DB'] = 'BucketList'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)

@app.route("/")
def main():
  return render_template('index.html')

@app.route('/showSignUp')
def showSignUp():
  return render_template('signup.html')

@app.route('/signUp',methods=['POST'])
def signUp():
  _name = request.form['inputName']
  _email = request.form['inputEmail']
  _password = request.form['inputPassword']

  if _name and _email and _password:
    conn = mysql.connect()
    cursor = conn.cursor()
    _hashed_password = generate_password_hash(_password)
    cursor.callproc('sp_createUser',(_name,_email,_hashed_password))
    data = cursor.fetchall()
    if len(data) is 0:
      conn.commit()
      return json.dumps({'message':'User created successfully'})
    else:
      return json.dumps({'error':str(data[0])})
  else:
    return json.dumps({'html':'<span>Enter the required fields</span>'})

@app.route('/showSignIn')
def showSignin():
  return render_template('signIn.html')

@app.route('/validateLogin',methods=['POST'])
def validateLogin():
  try:
    _username = request.form['inputEmail']
    _password = request.form['inputPassword']

    con = mysql.connect()
    cursor = con.cursor()
    cursor.callproc('sp_validateLogin', (_username,))
    data = cursor.fetchall()

    if len(data) > 0:
      if check_password_hash(str(data[0][3]), _password)
        return redirect('/userHome')
      else:
        return render_template('error.html', error='Wrong email address or password.')
    else:
      return render_template('error.html', error='Wrong email address or password.')

  except Exception as e:
    return render_template('error.html',error = str(e))
  finally:
    cursor.close()
    con.close()



if __name__ == "__main__":
  app.run()