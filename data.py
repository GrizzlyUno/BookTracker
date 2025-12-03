from google_books_api_wrapper.api import GoogleBooksAPI
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton, QLineEdit, QMessageBox
import PyQt5.QtWidgets as QtWidgets
from PyQt5.QtGui import QPixmap
import datetime
import os
import csv
import pandas as pd
from PIL import Image
import requests
from io import BytesIO

client = GoogleBooksAPI()

csvfile = "books.csv"
# 1. Functions ----
def convert_image_to_jpg(image_url):
    try:
        # Sending a GET request to the image URL to retrieve the image data
        response = requests.get(image_url)

        # Checking if the response is successful
        if response.status_code == 200:
            # Opening the image using PIL's Image module
            image = Image.open(BytesIO(response.content))

            # Converting the image to JPG format
            jpg_image = image.convert("RGB")

            return jpg_image
        else:
            raise ValueError("Failed to retrieve the image from the provided URL.")
    except Exception as e:
        raise ValueError(f"Error converting image to JPG: {e}")

## 1.1 Data Handeling ----
def call_data():
    with open(csvfile, 'r') as file:  
        # creating a csv reader object  
        data = pd.read_csv(csvfile)
        
        file.close()
        return data
            
def update_data(newdata):
    with open(csvfile, 'a') as file:  
        data = pd.read_csv(csvfile)
        for row in data.iterrows():
            if str(row[1]['ISBN']) == newdata[8]:
                print(str(row[1]['ISBN']), newdata[8])
                print("Book already exists in the database.")
                return
            else:
                print(str(row[1]['ISBN']), newdata[8])
        destroy_list()
        csvwriter = csv.writer(file)
        csvwriter.writerow(newdata)
        file.close()
        create_list()
    
def fetch_book(isbn):
    if len(str(isbn)) == 10 or len(str(isbn)) == 13:
        if len(str(isbn)) == 13:
            book_by_isbn = client.get_book_by_isbn13(isbn)
        elif len(str(isbn)) == 10:
            book_by_isbn = client.get_book_by_isbn10(isbn)
        return book_by_isbn
    else:
        print("Invalid ISBN length")

def add_book_to_table(isbn):
    book = fetch_book(isbn)
    if book:
        update_data([
            book.title,
            book.authors,
            book.publisher,
            book.published_date,
            datetime.datetime.now().strftime("%Y-%m-%d"),
            book.description,
            book.subjects,
            book.large_thumbnail,
            isbn,
            book.page_count,
            0,
            ()
        ])
    else:
        print("Book not found")

def get_book_recommedations(subject):
    list = client.get_books_by_subject(subject)
    print(list.get_all_results())
    
## 1.2 GUI Data Presentation ----    
def create_list():
    with open(csvfile, 'a') as file:  
        data = pd.read_csv(csvfile)
        for row in data.iterrows():
            ListObj = QtWidgets.QListWidgetItem(f"{str(row[1]['Name'])} by {str(row[1]['Authors'])}", list)
            ListObj.setToolTip(str(row[1]['ISBN']))
        file.close()

def destroy_list():
    for obj in list.findItems("*", Qt.MatchWildcard):
        list.clear()

def present_data(ISBN):
    UserData = call_data()
    for row in UserData.iterrows():
        if str(row[1]['ISBN']) == str(ISBN):
            BookNameLabel.setText(f"Book Name: {str(row[1]['Name'])} by {str(row[1]['Authors'])}")
            PublisherLabel.setText(f"Publisher: {str(row[1]['Publisher'])}")
            SubjectLabel.setText(f"Subject: {str(row[1]['Categories'])}")
            PublishingDateLabel.setText(f"Published Date: {str(row[1]['Published Date'])}")
            print(f"this prints: {len(str(row[1]['Thumbnail']))}")
            if len(str(row[1]['Thumbnail'])) <= 3:
                ImageLabel.setText("No Image Available")
                return
            else:
                convert_image_to_jpg(f"{(str(row[1]['Thumbnail']))}").save("temp.jpg")
                pixmap = QPixmap("temp.jpg").scaled(150, 200, Qt.KeepAspectRatio)
                print(row[1]['Thumbnail'])
                ImageLabel.setText("")
                ImageLabel.setPixmap(pixmap)
                break
        
## 1.3 GUI Helpers ----

def create_window():
    second_window = QWidget()
    second_window.setWindowTitle("Book Details")
    second_window.resize(400, 300)
    second_window.setStyleSheet("background-color: #121212")
    main_window.setMinimumSize(400, 300)
    main_window.setMaximumSize(400, 300)

    second_window.show()

    return second_window

# 2. GUI Setup ----
## 2.1 Main Window ----
app = QApplication([])
main_window = QWidget()
main_window.setWindowTitle("Book Tracker")
main_window.resize(720, 480)
main_window.setStyleSheet("background-color: #121212")

main_window.setMinimumSize(720, 480)
main_window.setMaximumSize(720, 480)

## 2.2 GUI Elements ----
Button = QtWidgets.QPushButton(main_window)
Button.setText("Add Book by ISBN")
Button.setGeometry(220, 10, 100, 30)
Button.setStyleSheet("background-color: #1E88E5; color: white; border-radius: 5px;")
Button.clicked.connect(lambda: add_book_to_table(Input.text()))

Input = QtWidgets.QLineEdit(main_window)
Input.setStyleSheet("background-color: #1E88E5; color: white; border-radius: 5px;")
Input.setGeometry(10, 10, 200, 30)
Input.setPlaceholderText("Enter ISBN")

BookNameLabel = QtWidgets.QLabel(main_window)
BookNameLabel.setText("Book Name: ")
BookNameLabel.setGeometry(30, 50, 700, 30)
BookNameLabel.setStyleSheet("color: white; border-radius: 5px;")

PublisherLabel = QtWidgets.QLabel(main_window)
PublisherLabel.setText("Publisher: ")
PublisherLabel.setGeometry(30, 70, 700, 30)
PublisherLabel.setStyleSheet("color: white; border-radius: 5px;")

SubjectLabel = QtWidgets.QLabel(main_window)
SubjectLabel.setText("Subject: ")
SubjectLabel.setGeometry(30, 90, 700, 30)
SubjectLabel.setStyleSheet("color: white; border-radius: 5px;")

PublishingDateLabel = QtWidgets.QLabel(main_window)
PublishingDateLabel.setText("Published Date: ")
PublishingDateLabel.setGeometry(30, 110, 700, 30)
PublishingDateLabel.setStyleSheet("color: white; border-radius: 5px;")

PublishingDateLabel = QtWidgets.QLabel(main_window)
PublishingDateLabel.setText("Published Date: ")
PublishingDateLabel.setGeometry(30, 110, 700, 30)
PublishingDateLabel.setStyleSheet("color: white; border-radius: 5px;")

ImageLabel = QtWidgets.QLabel(main_window)
ImageLabel.setGeometry(30, 150, 150, 200)
ImageLabel.setStyleSheet("background-color: #1E1E1E; border-radius: 5px;")

EditButtonLabel = QtWidgets.QPushButton(main_window)
EditButtonLabel.setText("Edit Book")
EditButtonLabel.setGeometry(30, 370, 150, 30)
EditButtonLabel.setStyleSheet("background-color: #1E88E5; color: white; border-radius: 5px;")

list = QtWidgets.QListWidget(main_window)
list.setGeometry(330, 10, 380, 460)
list.setStyleSheet("background-color: #1E1E1E; color: white; border-radius: 5px;")
list.itemSelectionChanged.connect(lambda: present_data(list.currentItem().toolTip()))
            
create_list()

main_window.show()
app.exec_()