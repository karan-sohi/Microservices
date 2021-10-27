import mysql.connector

db_conn = mysql.connector.connect(host="karankafka.eastus2.cloudapp.azure.com", user="user", password="password", database="events")

db_cursor = db_conn.cursor()

db_cursor.execute('''
          CREATE TABLE vanilla_cake
          (id INT NOT NULL AUTO_INCREMENT,
           cake_id INT NOT NULL, 
           name VARCHAR(250) NOT NULL,
           vanilla_type VARCHAR(250) NOT NULL,
           preparation_method VARCHAR(250) NOT NULL,
           sell_by_date VARCHAR(250) NOT NULL,
           date_created VARCHAR(100) NOT NULL, 
           CONSTRAINT vanilla_cake_pk PRIMARY KEY (id))
                ''')

db_cursor.execute('''
          CREATE TABLE chocolate_cake
          (id INT NOT NULL AUTO_INCREMENT, 
           cake_id INT NOT NULL,
           name VARCHAR(250) NOT NULL,
           chocolate_type VARCHAR(250) NOT NULL,
           preparation_method VARCHAR(250) NOT NULL,
           sell_by_date VARCHAR(250) NOT NULL,
           date_created VARCHAR(100) NOT NULL, 
           CONSTRAINT chocolate_cake_pk PRIMARY KEY (id) )
                ''')

db_conn.commit()
db_conn.close()
