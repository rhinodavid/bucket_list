from flask import Flask, render_template, json, request, redirect, session
from flaskext.mysql import MySQL
from werkzeug import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'P)99(uvtehdG7AZj{q3['

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
  try:
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

  except Exception as e:
    return json.dumps({'error':str(e)})

  finally:
    cursor.close()
    conn.close()

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
      if check_password_hash(str(data[0][3]),_password):
        session['user'] = data[0][0]
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

@app.route('/userHome')
def userHome():
  if session.get('user'):
    return render_template('userHome.html')
  else:
    return render_template('error.html',error = 'Unauthorized Access')

@app.route('/logout')
def logout():
  session.pop('user',None)
  return redirect('/')

@app.route('/showAddWish')
def showAddWish():
  return render_template('addWish.html')

@app.route('/addWish',methods=['POST'])
def addWish():
  try:
    _user_id = session.get('user')
    _wish_title = request.form['inputTitle']
    _wish_description = request.form['inputDescription']

    conn = mysql.connect()
    cursor = conn.cursor()

    if _user_id and _wish_title and _wish_description:
      cursor.callproc('sp_addWish',(_wish_title,_wish_description,_user_id))
      data = cursor.fetchall()
      if len(data) is 0:
        conn.commit()
        return redirect('/userHome')
      else:
        return render_template('error.html',error = "There was a problem adding the wish")
  except Exception as e:
    return render_template('error.html',error = str(e))
  finally:
    cursor.close()
    conn.close()

@app.route('/getWish')
def getWish():
  try:
    if session.get('user'):
      _user = session.get('user')

      conn = mysq.connect()
      cursor = conn.cursor()
      cursor.callproc('sp_GetWishByUser',(_user))
      wishes = cursor.fetchall()

      wishes_dict = []
      for wish in wishes:
        wish_dict = {
          'Id': wish[0],
          'Title': wish[1],
          'Description': wish[2],
          'Date': wish[4]
        }
        wishes_dict.append(wish_dict)
        return json.dumps(wishes_dict)
    else:
      return render_template('error.html',error = 'Unauthorized Access')
  except Exception as e:
    return render_template('error.html',error = str(e))


if __name__ == "__main__":
  app.run()