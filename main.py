import sys
sys.path.insert(0, './src')
import os
from PIL import Image
import streamlit as st
import pandas as pd
import uuid
from src.stegno_algo import lsb_encode, lsb_decode
from src.share_algo import generate_shares, compress_n_join_shares
path = "C:/Users/user/PycharmProjects/Data_hiding/Data_hiding/images"

# Security
#passlib,hashlib,bcrypt,scrypt

import hashlib


def make_hashes(password):
	return hashlib.sha256(str.encode(password)).hexdigest()

def check_hashes(password,hashed_text):
	if make_hashes(password) == hashed_text:
		return hashed_text
	return False
# DB Management
import pymysql as mysql
conn = mysql.connect(
	  host="localhost",
	  user="root",
	  password="",
	  database="data_hiding"
	)
c = conn.cursor()
# DB  Functions

def create_usertable():
	c.execute('CREATE TABLE IF NOT EXISTS users(id TEXT,username TEXT,email TEXT,password TEXT,groups VARCHAR(255))')
def create_accesstable():
	c.execute('CREATE TABLE IF NOT EXISTS access(id TEXT, groupName TEXT,entries VARCHAR(255),members VARCHAR(255),nMems TEXT,nEntries TEXT )')

def add_access(src,gName,email,mems):
	c.execute("SELECT groupName FROM access WHERE groupName = %s", (gName,))
	result = c.fetchone()
	if result is None:
		id = uuid.uuid1()
		c.execute('INSERT INTO access(id,groupName,entries,members,nMems,nEntries) VALUES (%s,%s,%s,%s,%s,%s)', (id,gName,src,email,mems,"1"))
		conn.commit()


	else:
		c.execute(
			"UPDATE access SET entries = CONCAT(entries, %s), members = CONCAT(members, %s), nEntries = nEntries + %s WHERE groupName = %s",(',' + src, ',' +email, 1, gName))
		conn.commit()
		c.execute("SELECT * FROM access WHERE groupName = %s", (gName,))
		result1 = c.fetchone()
		return int(result1[5]) == mems

def is_uploaded(gName,email):
	create_accesstable()
	c.execute("SELECT members FROM access WHERE groupName = %s ", (gName,))
	result = c.fetchone()
	if result is not None:
		mems = result[0].split(',')
		if email in mems: return True
		else: return False
def is_ready(gName,mems):
	c.execute("SELECT * FROM access WHERE groupName = %s", (gName,))
	result1 = c.fetchone()
	return int(result1[5]) == mems
def get_src(gName):
	c.execute("SELECT entries FROM access WHERE groupName = %s", (gName,))
	result = c.fetchone()
	return result[0].split(',')
def get_groups(email):
	c.execute("SELECT groups FROM users WHERE email = %s", (email,))
	result = c.fetchone()
	if result[0] is not None:
		grps = result[0].split(',')
		return grps[1:]
def get_group(gName):
	c.execute("SELECT * FROM groups WHERE groupName = %s",(gName,))
	result = c.fetchone()
	if len(result)>0:
		mems = result[2].split(',')
		return mems

def get_imgs(email,groupName):
	c.execute("SELECT * FROM images WHERE user = %s AND groupName = %s", (email, groupName))
	result = c.fetchall()
	if len(result) > 0:
		print("Matching images found:")
		for row in result:
			print("ID: {}, Group: {}, User: {}, Image: {}".format(row[0], row[1], row[2], row[3]))
			c.execute("DELETE FROM images WHERE id = %s", (row[0],))
			print("Deleted query with id {}".format(row[0]))
			conn.commit()
			return row[3]
	else:
		return "No image"



def add_userdata(email,username,password):
	id = uuid.uuid1()
	print(id);
	c.execute('INSERT INTO users(id,email,username,password) VALUES (%s,%s,%s,%s)',(id,email,username,password))
	conn.commit()
def is_email_available(email):
	query = "SELECT * FROM users WHERE email=%s"
	values = (email)
	c.execute(query, values)
	result = c.fetchone()

	if result:
		return False
	else:
		return True
def login_user(email,password):
	c.execute('SELECT * FROM users WHERE email =%s AND password = %s',(email,password))
	data = c.fetchall()
	return data


def view_all_users():
	c.execute('SELECT * FROM userstable')
	data = c.fetchall()
	return data



def main():
	"""Simple Login App"""

	st.title("User Page")

	menu = ["Home","Login","SignUp"]
	choice = st.sidebar.selectbox("Menu",menu)

	if choice == "Home":
		st.subheader("Home")

	elif choice == "Login":
		st.subheader("Login Section")

		email = st.sidebar.text_input("Email ID")
		password = st.sidebar.text_input("Password",type='password')

		if st.sidebar.checkbox("Login"):
			# if password == '12345':
			hashed_pswd = make_hashes(password)

			result = login_user(email,check_hashes(password,hashed_pswd))
			if result:
				st.success("Logged In as {}".format(email))
				grps = []
				grps = get_groups(email)
				if grps is not None:
					choice = st.sidebar.radio('Groups', grps)
				else:
					choice = ""

				task = st.selectbox("Task",["Access Account","Download Share image"])
				if task == "Access Account":
					st.subheader(f"{choice}")
					gmems = get_group(choice)
					st.subheader("Members:")
					for mem in gmems:
						st.text(f"{mem}")
					if not is_uploaded(choice,email):

						st.subheader("Upload your Share")
						img = st.file_uploader(label="image",type=['png'])
						if img is not None:
							img = Image.open(img)
							img.save(f'{path}/{choice}-{email}.png')
							st.image(img, caption='Selected image to use for data encoding',use_column_width=True)
						src = f'{choice}-{email}.png'
						if st.button('Add Share to Access'):
							create_accesstable()
							isaccess = add_access(src,choice,email,len(gmems))
							if isaccess:
								st.success("Access content!!")
							else:
								st.warning("Shares need to be uploded by users")
					else:
						st.warning("Your share is already uploaded!!")
						if  is_ready(choice,len(gmems)):
							if st.button("Open Lock!!"):
								shares = get_src(choice)
								print(shares)
								compress_n_join_shares(shares,choice)
								st.success('Decoded message: ' + lsb_decode(
									f'{path}/compress-{choice}.png'))




				elif task == "Download Share image":
					st.subheader(f"{choice}")
					gimg=get_imgs(email,choice)
					if gimg == "No image":
						st.warning("image already downloaded")
					else:
						with open(f"{path}/{gimg}", "rb") as file:
							print(file)
							btn = st.download_button(
								label="Download image",
								data=file,
								file_name=f"{choice}-{email}.png",
								mime="image/png"
						)

			else:
				st.warning("Incorrect Username/Password")






	elif choice == "SignUp":
		st.subheader("Create New Account")
		new_email = st.text_input("Email")
		new_user = st.text_input("Username")
		new_password = st.text_input("Password",type='password')

		if st.button("Signup"):
				create_usertable()
				add_userdata(new_email, new_user, make_hashes(new_password))
				st.success("You have successfully created a valid Account")
				st.info("Go to Login Menu to login")



if __name__ == '__main__':
	main()