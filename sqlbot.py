import telebot
from string import Template
import mysql.connector

# Telegram your token
bot = telebot.TeleBot("1)
# Telegram your group id
group_id = %%%

# получить id канала/группы
#print(bot.get_chat('@botanskiytest').id)

db = mysql.connector.connect(
    host="127.0.0.1",
    user="%%%",
    passwd="%%%",
    port="%%%",
    database="regibot"
)


cursor = db.cursor()

#cursor.execute("CREATE DATABASE photoregbot")

#cursor.execute("CREATE TABLE regs (id INT AUTO_INCREMENT PRIMARY KEY, \
#first_name VARCHAR(255), phone VARCHAR(255), description VARCHAR(255), user_id INT(11))")

#cursor.execute("CREATE TABLE users (id INT AUTO_INCREMENT PRIMARY KEY, \
#first_name VARCHAR(255), phone VARCHAR(255), telegram_user_id INT(11) UNIQUE)")

user_data = {}

class User:
    def __init__(self, first_name):
        self.first_name = first_name
        self.phone = ''
        #self.photo = ''
        self.description = ''

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
        msg = bot.send_message(message.chat.id, "Введите имя и фамилию")
        bot.register_next_step_handler(msg, process_firstname_step)

def process_firstname_step(message):
    try:
        user_id = message.from_user.id
        user_data[user_id] = User(message.text)
        
        msg = bot.send_message(message.chat.id, "Напишите данные для отправки")
        bot.register_next_step_handler(msg, process_description_step)
    except Exception as e:
        bot.reply_to(message, 'ooops!')

def process_description_step(message):
    try:
        user_id = message.from_user.id
        user = user_data[user_id]
        user.description = message.text

        # Проверка есть ли пользователь в БД
        sql = "SELECT * FROM users WHERE telegram_user_id = {0}".format(user_id)
        cursor.execute(sql)
        existsUser = cursor.fetchone()

        # Если нету, то добавить в БД
        if (existsUser == None):
               sql = "INSERT INTO users (first_name, phone, telegram_user_id) \
                                  VALUES (%s, %s, %s)"
               val = (message.from_user.first_name, message.from_user.phone, user_id)
               cursor.execute(sql, val)

        # Регистрация заявки
        sql = "INSERT INTO regs (first_name, phone, description, user_id) \
                                  VALUES (%s, %s, %s, %s)"
        val = (user.first_name, user.phone, user.description, user_id)
        cursor.execute(sql, val)
        db.commit()

        # Сохранение фото на сервере
        #file_photo = bot.get_file(user.photo_id)
        #filename, file_extension = os.path.splitext(file_photo.file_path)

        #downloaded_file_photo = bot.download_file(file_photo.file_path)

        #src = 'photos/' + user.photo_id + file_extension
        #with open(src, 'wb') as new_file:
         #   new_file.write(downloaded_file_photo)

        bot.send_message(message.chat.id, "Вы успешно зарегистрированны!")

    except Exception as e:
        bot.reply_to(message, 'oooops')
