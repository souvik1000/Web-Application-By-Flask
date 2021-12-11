from flask import *
import sqlite3, hashlib, os
from werkzeug.utils import secure_filename

app = Flask(__name__)

app.secret_key = 'random string'
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = set(['jpeg', 'jpg', 'png', 'gif'])
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# For Image Upload
def allowed_file(filename):
    return '.' in filename and \
            filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

# Valid For User
def is_valid(email, password):
    con = sqlite3.connect('database.db')
    cur = con.cursor()
    cur.execute('SELECT email, password FROM users')
    data = cur.fetchall()
    for row in data:
        if row[0] == email and row[1] == hashlib.md5(password.encode()).hexdigest():
            return True
    return False

# Valid For Admin
def is_valid_admin(email, password):
    con = sqlite3.connect('database.db')
    cur = con.cursor()
    cur.execute('SELECT email, password FROM admindetails')
    data = cur.fetchall()
    print(data)
    for row in data:
        print(row)
        if row[0] == email and row[1] == password:
            return True
    return False

def parse(data):
    ans = []
    i = 0
    while i < len(data):
        curr = []
        for j in range(7):
            if i >= len(data):
                break
            curr.append(data[i])
            i += 1
        ans.append(curr)
    return ans

def getLoginDetails():
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        if 'email' not in session:
            loggedIn = False
            firstName = ''
            noOfItems = 0
        else:
            loggedIn = True
            cur.execute("SELECT userId, firstName FROM users WHERE email = '" + session['email'] + "'")
            userId, firstName = cur.fetchone()
            cur.execute("SELECT count(productId) FROM cart WHERE userId = " + str(userId))
            noOfItems = cur.fetchone()[0]
    conn.close()
    return (loggedIn, firstName, noOfItems)


# ROOT HOME SECTION

@app.route("/")
def root():
    loggedIn, firstName, noOfItems = getLoginDetails()
    # itemData = request.args.get('products')
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        cur.execute('SELECT categoryId, name FROM categories')
        categoryData = cur.fetchall()
        # if itemData is not None:
        #     print(itemData)
        # else:
        cur.execute('SELECT productId, name, price, description, image, stock FROM products')
        itemData = cur.fetchall()
    # itemData = parse(itemData)   
    return render_template('home.html', itemData=itemData, loggedIn=loggedIn, firstName=firstName, noOfItems=noOfItems, categoryData=categoryData)


# ADMINLOGIN

@app.route('/adminlogin')
def adminLogin():
    return render_template('adminlogin.html')

@app.route('/adminpanel')
def adminPanel():
    success_code = request.args.get('success_code')
    if (success_code == "200"):
        with sqlite3.connect('database.db') as conn:
            cur = conn.cursor()
            cur.execute('SELECT productId, name, price, description, image, stock FROM products')
            itemData = cur.fetchall()
            cur.execute('SELECT categoryId, name FROM categories')
            categoryData = cur.fetchall()
        return render_template('adminpanel.html', itemData=itemData, categoryData=categoryData)
    else:
        return render_template_string('''
                                        <div class="error">
                                            <h1>Error Page 404</h1>
                                        </div>
                                      ''')

# ADMINLOGIN - [VALIDATION]

@app.route('/adminvalidation', methods = ['POST', 'GET'])
def adminValidation():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if is_valid_admin(email, password):
            session['email'] = email
            return redirect(url_for('adminPanel', success_code=200))
        else:
            error = 'Invalid UserId / Password'
            return render_template('adminlogin.html', error=error)


# ADD SECTION

@app.route("/addItem", methods=["GET", "POST"])
def addItem():
    if request.method == "POST":
        name = request.form['name']
        price = float(request.form['price'])
        description = request.form['description']
        stock = int(request.form['stock'])
        categoryType = request.form['category']

        #Uploading image procedure
        image = request.files['image']
        if image and allowed_file(image.filename):
            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        imagename = filename
        with sqlite3.connect('database.db') as conn:
            try:
                cur = conn.cursor()
                categoryId = cur.execute("SELECT categoryId FROM categories WHERE name = ?", [categoryType])
                cur.execute('''INSERT INTO products (name, price, description, image, stock, categoryId) VALUES (?, ?, ?, ?, ?, ?)''', [name, price, description, imagename, stock, categoryId.fetchone()[0]])
                conn.commit()
                msg="added successfully"
            except Exception as e:
                msg="error occured"
                print(e)
                conn.rollback()
        conn.close()
        print(msg)
        return redirect(url_for('adminPanel', success_code=200))


# DELETE SECTION

@app.route('/delete')
def delete():
    return render_template('delete.html')

@app.route("/removeItem", methods=['GET', 'POST'])
def removeItem():
    if request.method == 'POST':
        productName = request.form['productname']
        with sqlite3.connect('database.db') as conn:
            try:
                cur = conn.cursor()
                cur.execute("DELETE FROM products WHERE name = ?",[productName])
                conn.commit()
                msg = "Deleted successsfully"
            except:
                conn.rollback()
                msg = "Error occured"
        conn.close()
        print(msg)
        return redirect(url_for('adminPanel', success_code=200))
    else:
        productName = request.args.get('productname')
        with sqlite3.connect('database.db') as conn:
            try:
                cur = conn.cursor()
                cur.execute("DELETE FROM products WHERE name = ?",[productName])
                conn.commit()
                msg = "Deleted successsfully"
            except:
                conn.rollback()
                msg = "Error occured"
        conn.close()
        print(msg)
        return redirect(url_for('adminPanel', success_code=200))


# EDIT & UPDATE SECTION

@app.route('/edit')
def edit():
    return render_template('edit.html')

@app.route("/editItem", methods=['POST', 'GET']) 
def editItem():
    if request.method == 'POST':
        productName = request.form['productname']
        with sqlite3.connect('database.db') as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM products WHERE name = ?",[productName])
            productData = cur.fetchone()
        conn.close()
        return render_template("edit.html", productData=productData)
    else:
        productName = request.args.get('productname')
        with sqlite3.connect('database.db') as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM products WHERE name = ?",[productName])
            productData = cur.fetchone()
            conn.close()
            return render_template("edit.html", productData=productData)
                
        

@app.route("/updateProduct", methods=["GET", "POST"])
def updateProduct():
    if request.method == 'POST':
        productId = request.form['productid']
        productName = request.form['productname']
        price = float(request.form['price'])
        description = request.form['description']
        stock = int(request.form['stock'])
        with sqlite3.connect('database.db') as con:
                try:
                    cur = con.cursor()
                    cur.execute('UPDATE products SET name = ?, price = ?, description = ?, stock = ? WHERE productId = ?', [productName, price, description, stock, productId])
                    con.commit()
                    msg = "Saved Successfully"
                except:
                    con.rollback()
                    msg = "Error occured"
        con.close()
        return redirect(url_for('adminPanel', success_code=200))

    
# USER LOGIN

@app.route("/loginForm")
def loginForm():
    if 'email' in session:
        return redirect(url_for('root'))
    else:
        return render_template('login.html', error='')
    
@app.route("/login", methods = ['POST', 'GET'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if is_valid(email, password):
            session['email'] = email
            return redirect(url_for('root'))
        else:
            error = 'Invalid UserId / Password'
            return render_template('login.html', error=error)


# USER REGISTRATION

@app.route("/registerationForm")
def registrationForm():
    return render_template("register.html")

@app.route("/register", methods = ['GET', 'POST'])
def register():
    if request.method == 'POST':  
        password = request.form['password']
        email = request.form['email']
        firstName = request.form['firstName']
        lastName = request.form['lastName']
        address1 = request.form['address1']
        address2 = request.form['address2']
        zipcode = request.form['zipcode']
        city = request.form['city']
        state = request.form['state']
        country = request.form['country']
        phone = request.form['phone']
        with sqlite3.connect('database.db') as con:
            try:
                cur = con.cursor()
                cur.execute('INSERT INTO users (password, email, firstName, lastName, address1, address2, zipcode, city, state, country, phone) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', (hashlib.md5(password.encode()).hexdigest(), email, firstName, lastName, address1, address2, zipcode, city, state, country, phone))
                con.commit()
                msg = "Registered Successfully"
            except:
                con.rollback()
                msg = "Error Occured! Please Try Again."
        con.close()
        return render_template("login.html", error=msg)


# USER LOGOUT

@app.route("/logout")
def logout():
    session.pop('email', None)
    return redirect(url_for('root'))


# USER ACCOUNT PROFILE & EDIT & CHANGE PASSWORD

@app.route("/account/profile")
def profileHome():
    if 'email' not in session:
        return redirect(url_for('root'))
    loggedIn, firstName, noOfItems = getLoginDetails()
    return render_template("profileHome.html", loggedIn=loggedIn, firstName=firstName, noOfItems=noOfItems)

@app.route("/account/profile/view")
def viewProfile():
    if 'email' not in session:
        return redirect(url_for('root'))
    loggedIn, firstName, noOfItems = getLoginDetails()
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        cur.execute("SELECT userId, email, firstName, lastName, address1, address2, zipcode, city, state, country, phone FROM users WHERE email = '" + session['email'] + "'")
        profileData = cur.fetchone()
    conn.close()
    return render_template("viewProfile.html", profileData=profileData, loggedIn=loggedIn, firstName=firstName, noOfItems=noOfItems)

@app.route("/account/profile/edit")
def editProfile():
    if 'email' not in session:
        return redirect(url_for('root'))
    loggedIn, firstName, noOfItems = getLoginDetails()
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        cur.execute("SELECT userId, email, firstName, lastName, address1, address2, zipcode, city, state, country, phone FROM users WHERE email = '" + session['email'] + "'")
        profileData = cur.fetchone()
    conn.close()
    return render_template("editProfile.html", profileData=profileData, loggedIn=loggedIn, firstName=firstName, noOfItems=noOfItems)

@app.route("/updateProfile", methods=["GET", "POST"])
def updateProfile():
    userId = request.args.get('userId')
    if request.method == 'POST':
        email = request.form['email']
        firstName = request.form['firstName']
        lastName = request.form['lastName']
        address1 = request.form['address1']
        address2 = request.form['address2']
        zipcode = request.form['zipcode']
        city = request.form['city']
        state = request.form['state']
        country = request.form['country']
        phone = request.form['phone']
        with sqlite3.connect('database.db') as con:
                try:
                    cur = con.cursor()
                    cur.execute('UPDATE users SET firstName = ?, lastName = ?, address1 = ?, address2 = ?, zipcode = ?, city = ?, state = ?, country = ?, phone = ? WHERE userId = ?', (firstName, lastName, address1, address2, zipcode, city, state, country, phone, userId))
                    con.commit()
                    msg = "Saved Successfully"
                except:
                    con.rollback()
                    msg = "Error occured"
        con.close()
        return redirect(url_for('profileHome'))

@app.route("/account/profile/changePassword", methods=["GET", "POST"])
def changePassword():
    if 'email' not in session:
        return redirect(url_for('loginForm'))
    if request.method == "POST":
        oldPassword = request.form['oldpassword']
        oldPassword = hashlib.md5(oldPassword.encode()).hexdigest()
        newPassword = request.form['newpassword']
        newPassword = hashlib.md5(newPassword.encode()).hexdigest()
        with sqlite3.connect('database.db') as conn:
            cur = conn.cursor()
            cur.execute("SELECT userId, password FROM users WHERE email = '" + session['email'] + "'")
            userId, password = cur.fetchone()
            if (password == oldPassword):
                try:
                    cur.execute("UPDATE users SET password = ? WHERE userId = ?", (newPassword, userId))
                    conn.commit()
                    msg="Changed successfully"
                except:
                    conn.rollback()
                    msg = "Failed"
                return render_template("profileHome.html", msg=msg)
            else:
                msg = "Wrong password"
        conn.close()
        return render_template("changePassword.html", msg=msg)
    else:
        return render_template("changePassword.html")


# SEARCH ITEMS FROM SEARCH-BAR

@app.route('/searchItem')
def searchItem():   
    searchItem= (request.args.get("searchQuery"))
    searchItem=searchItem.lower()
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM products WHERE lower(name) LIKE ?",['%'+searchItem+'%'])
        products = cur.fetchall()
        return render_template('result.html', products=products)  
        # return redirect(url_for('root', products=products))


# PRODUCT DISPLAY WITH DESCRIPTION

@app.route("/productDescription")
def productDescription():
    loggedIn, firstName, noOfItems = getLoginDetails()
    productId = request.args.get('productId')
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        cur.execute('SELECT productId, name, price, description, image, stock FROM products WHERE productId = ' + productId)
        productData = cur.fetchone()
    conn.close()
    return render_template("productDescription.html", data=productData, loggedIn = loggedIn, firstName = firstName, noOfItems = noOfItems)


# CART SECTION HANDLE

@app.route("/addToCart")
def addToCart():
    if 'email' not in session:
        return redirect(url_for('loginForm'))
    else:
        productId = int(request.args.get('productId'))
        with sqlite3.connect('database.db') as conn:
            cur = conn.cursor()
            cur.execute("SELECT userId FROM users WHERE email = '" + session['email'] + "'")
            userId = cur.fetchone()[0]
            cur.execute("SELECT count(*) as countcart FROM cart WHERE cart.productId = ? AND cart.userId = ?",[productId, userId])
            countCartProduct = cur.fetchone()[0]
            # print(countCartProduct[0])
            try:
                if countCartProduct > 0:
                    cur.execute("SELECT cartId, qty FROM cart WHERE cart.productId = ? AND cart.userId = ?",[productId, userId])
                    qty = cur.fetchone()
                    cartId = qty[0]; updatedQTY = qty[1] + 1
                    # print("cartId: ",cartId, " updateQty: ", updatedQTY)
                    cur.execute("UPDATE cart SET qty = ? WHERE cartId = ?", [updatedQTY, cartId])
                else:
                    cur.execute("INSERT INTO cart (userId, productId, qty) VALUES (?, ?, ?)", [userId, productId, 1])
                conn.commit()
                msg = "Added successfully"
            except:
                conn.rollback()
                msg = "Error occured"
        conn.close()
        return redirect(url_for('root'))

@app.route("/cart")
def cart():
    if 'email' not in session:
        return redirect(url_for('loginForm'))
    loggedIn, firstName, noOfItems = getLoginDetails()
    email = session['email']
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        cur.execute("SELECT userId FROM users WHERE email = '" + email + "'")
        userId = cur.fetchone()[0]
        cur.execute("SELECT products.productId, products.name, products.price, products.image, cart.qty FROM products, cart WHERE products.productId = cart.productId AND cart.userId = " + str(userId))
        products = cur.fetchall()
    totalPrice = 0
    for product in products:
        totalPrice += (product[2] * product[4])
    return render_template("cart.html", products = products, totalPrice=totalPrice, loggedIn=loggedIn, firstName=firstName, noOfItems=noOfItems)

@app.route("/removeFromCart")
def removeFromCart():
    if 'email' not in session:
        return redirect(url_for('loginForm'))
    email = session['email']
    productId = int(request.args.get('productId'))
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        cur.execute("SELECT userId FROM users WHERE email = '" + email + "'")
        userId = cur.fetchone()[0]
        try:
            cur.execute("DELETE FROM cart WHERE userId = " + str(userId) + " AND productId = " + str(productId))
            conn.commit()
            msg = "removed successfully"
        except:
            conn.rollback()
            msg = "error occured"
    conn.close()
    return redirect(url_for('cart'))


# CHECKOUT PRODUCTS

@app.route("/checkout", methods=['GET','POST'])
def checkout():
    if 'email' not in session:
        return redirect(url_for('loginForm'))
    loggedIn, firstName, noOfItems = getLoginDetails()
    email = session['email']
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        cur.execute("SELECT userId FROM users WHERE email = '" + email + "'")
        userId = cur.fetchone()[0]
        cur.execute("SELECT products.productId, products.name, products.price, products.image, cart.cartId FROM products, cart WHERE products.productId = cart.productId AND cart.userId = " + str(userId))
        products = cur.fetchall()
    totalPrice = 0
    for product in products:
        totalPrice += (product[2] * product[4])
        cur.execute("INSERT INTO Orders (userId, productId) VALUES (?, ?)", (userId, product[0]))
    cur.execute("DELETE FROM cart WHERE userId = " + str(userId))
    conn.commit()
    return render_template("checkout.html", products = products, totalPrice=totalPrice, loggedIn=loggedIn, firstName=firstName, noOfItems=noOfItems)


if __name__ == "__main__":
    app.run(debug=True)