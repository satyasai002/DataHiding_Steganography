import sys
sys.path.insert(0, './src')
import os
import streamlit as st
import pandas as pd
import uuid
from PIL import Image
from src.stegno_algo import lsb_encode, lsb_decode
from src.share_algo import generate_shares, compress_n_join_shares
import hashlib
path = "C:/Users/user/PycharmProjects/Data_hiding/Data_hiding/images/"
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
def create_grouptable():
	c.execute('CREATE TABLE IF NOT EXISTS groups(id TEXT,groupName TEXT,users VARCHAR(255),noMems TEXT)')
def create_imgstable():
	c.execute('CREATE TABLE IF NOT EXISTS images(id TEXT,groupName TEXT,user TEXT,img TEXT)')
def add_imgdata(gName,mems,src):
	for i in range(len(mems)):
		id = uuid.uuid1()
		c.execute('INSERT INTO images(id,groupName,user,img) VALUES (%s,%s,%s,%s)',(id,gName,mems[i],src[i]))
	conn.commit()
def is_group_available(gname):
	query = "SELECT * FROM groups WHERE groupName=%s"
	values = (gname)
	c.execute(query, values)
	result = c.fetchone()

	if result:
		return False
	else:
		return True
def add_groupdata(gName,mems,nMems):
	id = uuid.uuid1()
	print(id)
	for mem in mems:
		c.execute("UPDATE users SET groups = CONCAT(IFNULL(groups, ''), %s) WHERE email = %s", (',' + gName, mem))
	c.execute('INSERT INTO groups(id,groupName,users,noMems) VALUES (%s,%s,%s,%s)',(id,gName,','.join(mems),nMems))
	conn.commit()
def login_user(email,password):
	c.execute('SELECT * FROM admin WHERE email =%s AND password = %s',(email,password))
	data = c.fetchall()
	return data


def view_all_users():
	c.execute('SELECT * FROM users')
	data = c.fetchall()
	return data



def main():
	"""Simple Login App"""

	st.title("Admin")

	menu = ["Home","Login"]
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

				task = st.selectbox("Task",["Create Group","Profiles"])
				if task == "Create Group":
					st.subheader("Create new group")
					gName = st.text_input("Enter group name")
					nMems = int(st.number_input("Enter Number of Members in group"))
					mems = []
					for i in range(nMems):
						mem = st.text_input(f"Enter email of {i+1} person",key=i)
						mems.append(mem)
					print(mems)
					img = st.file_uploader('Upload Cover Image', type=['jpg', 'png', 'jpeg'])
					if img is not None:
						img = Image.open(img)
						try:
							img.save(f'{path}/{gName}.jpg')
						except:
							img.save(f'{path}/{gName}.png')
						st.image(img, caption='Selected image to use for data encoding',use_column_width=True)
					password = st.text_input("Enter password");
					if st.button('Encode data and Generate shares'):

						# Checks
						if len(password) == 0:
							st.warning('No data to hide')
						# elif not is_group_available(gName):
						# 	st.warning("Group name already taken!!")
						elif img is None:
							st.warning('No image file selected')
						# Generate splits
						else:
							print("In main try: ", password)
							src=generate_shares(lsb_encode(password,gName), nMems,gName)
							try:
								os.remove(f'{path}/{gName}.jpg')
							except FileNotFoundError:
								os.remove(f'{path}/{gName}.png')
							st.success(
								f'Data encoded using Steganography and splitted into {nMems} shares using Visual Cryptography :)!')
							create_grouptable()
							create_imgstable()
							add_groupdata(gName,mems, nMems)
							add_imgdata(gName,mems,src)
							st.success("New group created")





				elif task == "Profiles":
					st.subheader("User Profiles")
					user_result = view_all_users()
					clean_db = pd.DataFrame(user_result,columns=["ID","Email","Username","Password","Groups"])
					st.dataframe(clean_db)
			else:
				st.warning("Incorrect Username/Password")


if __name__ == '__main__':
	main()