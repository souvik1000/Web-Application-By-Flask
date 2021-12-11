import sqlite3

#Open database
conn = sqlite3.connect('database.db')

#Create table
conn.execute('''CREATE TABLE users 
		(userId INTEGER PRIMARY KEY, 
		password TEXT,
		email TEXT,
		firstName TEXT,
		lastName TEXT,
		address1 TEXT,
		address2 TEXT,
		zipcode TEXT,
		city TEXT,
		state TEXT,
		country TEXT, 
		phone TEXT
		)''')

conn.execute('''CREATE TABLE products
		(productId INTEGER PRIMARY KEY,
		name TEXT,
		price REAL,
		description TEXT,
		image TEXT,
		stock INTEGER,
		categoryId INTEGER,
		FOREIGN KEY(categoryId) REFERENCES categories(categoryId)
		)''')

conn.execute('''CREATE TABLE cart
		(cartId INTEGER PRIMARY KEY,
      	userId INTEGER,
		productId INTEGER,
		qty INTEGER,
		FOREIGN KEY(userId) REFERENCES users(userId),
		FOREIGN KEY(productId) REFERENCES products(productId)
		)''')

conn.execute('''CREATE TABLE categories
		(categoryId INTEGER PRIMARY KEY,
		name TEXT
		)''')

conn.execute('''CREATE TABLE orders
		(userId INTEGER,
		productId INTEGER,
		FOREIGN KEY(userId) REFERENCES users(userId),
		FOREIGN KEY(productId) REFERENCES products(productId)
		)''')

conn.execute('''CREATE TABLE admindetails
            (adminId TEXT PRIMARY KEY,
			firstName TEXT,
			lastName TEXT,
            email TEXT,
            password TEXT
			 )''')

# adminId = ["admin1", "admin2", "admin3"]
# firstName = ["Souvik", "Kirti", "Raghib"]
# lastName = ["Ghosh", "Garg", "Shams"]
# email = ["ghosh.souvik500@gmail.com", "kirtigarg255@gmail.com", "raghibshams@gmail.com"]
# password = ["souvik", "kirti", "raghib"]

# conn.execute("INSERT INTO admindetails(adminId, firstName, lastName, email, password) VALUES('admin1', 'Souvik', 'Ghosh', 'ghosh.souvik500@gmail.com', 'souvik')")
# conn.execute("INSERT INTO admindetails(adminId, firstName, lastName, email, password) VALUES('admin2', 'Kirti', 'Garg', 'kirtigarg255@gmail.com', 'kirti')")
# conn.execute("INSERT INTO admindetails(adminId, firstName, lastName, email, password) VALUES('admin3', 'Raghib', 'Shams', 'raghibshams@gmail.com', 'raghib')")

conn.close()

