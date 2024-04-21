# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter

class CSVDBPipeline:
    def __init__(self):
        self.file = open('unitop_data.csv', 'a', encoding='utf-8')
        self.file.write('coursename$lecturer$intro$describe$courseUrl\n')

    def process_item(self, item, spider):
        line = f"{item['coursename']}${item['lecturer']}${item['intro']}${item['describe']}${item['courseUrl']}\n"
        self.file.write(line)
        return item

    def close_spider(self, spider):
        self.file.close()

###############

import json

class JsonPipeline:
    def __init__(self):
        self.file = None
        self.is_first_item = True

    def open_spider(self, spider):
        self.file = open('jsondataunitop.json', 'w', encoding='utf-8')  # Mở file trong chế độ ghi lại
        self.file.write('[')  # Mở mảng JSON

    def process_item(self, item, spider):
        try:
            # Kiểm tra xem các trường dữ liệu có giá trị không rỗng
            if all(value is not None for value in item.values()):
                line = json.dumps(dict(item), ensure_ascii=False)
                if self.is_first_item:
                    self.is_first_item = False
                else:
                    line = ',\n' + line
                self.file.write(line)
        except Exception as e:
            print("Error processing item:", e)
        return item

    def close_spider(self, spider):
        self.file.write(']')  
        self.file.close()

import pymongo
import json
from bson.objectid import ObjectId
### mongo db
class MongoDBPipeline:
    def __init__(self):
        self.client = pymongo.MongoClient('mongodb+srv://nhatlinhdev201:FTYVDXyNoAADKzWG@cluster0.qoouwrv.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0')
        self.db = self.client['bigdata']
        self.collection = self.db['unitop']
    
    def process_item(self, item, spider):
        try:
            # Kiểm tra xem item có dữ liệu không
            if item:
                # Chèn một mục vào collection
                self.collection.insert_one(dict(item))
                return item
            else:
                # Nếu item không có dữ liệu, bỏ qua và không chèn vào MongoDB
                raise DropItem("Item is empty")
        except Exception as e:
            raise DropItem(f"Error inserting item: {e}")

########
import pymysql
from scrapy.exceptions import DropItem

class MySQLPipline:
    def __init__(self):
        self.conn = pymysql.connect(
            host='localhost',
            user='root',
            password='sapassword',
            database='bigdata'
        )
        ## Create cursor, used to execute commands
        self.cur = self.conn.cursor()
        ## Create quotes table if none exists
        self.cur.execute("""
        CREATE TABLE IF NOT EXISTS unitops(
            id int NOT NULL auto_increment, 
            courseUrl text,
            coursename text,
            lecturer VARCHAR(255),
            intro text,
            `describe` text,
            votenumber VARCHAR(100),
            rating int,
            newfee VARCHAR(100),
            oldfee VARCHAR(100),
            lessonnum VARCHAR(100),
            PRIMARY KEY (id)
        )
        """)
    def process_item(self, item, spider):
        try:
            ## Define insert statement
            self.cur.execute(""" insert into unitops (courseUrl, coursename, lecturer, intro, `describe`, votenumber, rating, newfee, oldfee, lessonnum) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""", (
                item["courseUrl"],
                item["coursename"],
                item["lecturer"],
                item["intro"],
                item["describe"],
                item["votenumber"],
                int(item["rating"]),  # Cast rating to int
                item["newfee"],
                item["oldfee"],
                item["lessonnum"]
            ))
            ## Execute insert of data into database
            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            raise DropItem(f"Error inserting item: {e}")
        
    def close_spider(self, spider):
        ## Close cursor & connection to database 
        self.cur.close()
        self.conn.close()


##########
##pgr
import psycopg2
from psycopg2 import Error
from scrapy.exceptions import DropItem

class PostgreSQLPipeline:
    def __init__(self):
        try:
            # Kết nối tới PostgreSQL
            self.connection = psycopg2.connect(
                user="postgres",
                password="admin",
                host="localhost",
                port="5432",
                database="bigdata"
            )
            self.cursor = self.connection.cursor()
            # Tạo bảng nếu chưa tồn tại
            create_table_query = '''
            CREATE TABLE IF NOT EXISTS unitops (
                id SERIAL PRIMARY KEY,
                courseUrl TEXT,
                coursename TEXT,
                lecturer VARCHAR(255),
                intro TEXT,
                description TEXT,
                votenumber VARCHAR(100),
                rating INT,
                newfee VARCHAR(100),
                oldfee VARCHAR(100),
                lessonnum VARCHAR(100)
            );
            '''
            self.cursor.execute(create_table_query)
            self.connection.commit()
            print("Table created successfully in PostgreSQL ")

        except (Exception, Error) as error:
            print("Error while connecting to PostgreSQL", error)

    def process_item(self, item, spider):
        try:
            # Chèn một mục vào bảng
            postgres_insert_query = """INSERT INTO unitops (courseUrl, coursename, lecturer, intro, description, votenumber, rating, newfee, oldfee, lessonnum) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
            record_to_insert = (item["courseUrl"], item["coursename"], item["lecturer"], item["intro"], item["describe"], item["votenumber"], item["rating"], item["newfee"], item["oldfee"], item["lessonnum"])
            self.cursor.execute(postgres_insert_query, record_to_insert)
            self.connection.commit()
            print("Item inserted successfully into PostgreSQL ")
        except (Exception, psycopg2.Error) as error:
            print("Failed to insert record into PostgreSQL table:", error)
            raise DropItem(f"Error inserting item: {error}")

    def close_spider(self, spider):
        if self.connection:
            self.cursor.close()
            self.connection.close()
            print("PostgreSQL connection is closed")
