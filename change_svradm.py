from werkzeug.security import generate_password_hash, check_password_hash

def generate(userid, password):
    credentials = password
    salt = bcrypt.gensalt()
    hashed_credentials = generate_password_hash(credentials)


    with open("server_adm.txt", "w") as file:
        file.write(salt.decode('utf-8'))
        file.write('\n')
        file.write(hashed_credentials.decode('utf-8'))


userid = input('UserID: ')
password = input('Password: ')

generate(userid,password)
