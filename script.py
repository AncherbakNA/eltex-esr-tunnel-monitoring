from datetime import datetime
from netmiko import NetmikoTimeoutException, NetmikoAuthenticationException, ConnectHandler
import telebot


# Принимает: информацию об устройстве + команду для выполнения
# Выполняет:  show команду на устройство
# Возвращает: вывод show команды
def send_show_command(device, cmd):
    result = {}
    try: 
        with ConnectHandler(**device) as ssh:
            result[cmd] = ssh.send_command(cmd)
        return result
    except (NetmikoTimeoutException, NetmikoAuthenticationException) as error:
        print(error)


# Принимает: массив строк + массив слов
# Выполняет: проверку состояния туннеля по кол-ву совпадений необходимых слов в каждой строке
# Возвращает: статус туннеля (True/False, Up/Down)
def check_tunnel_status(formatted_result, words_to_check):
    IPsec_SA_counter = 0
    for string in formatted_result:
        counter = 0
        for word in words_to_check:
            if word in string: 
                counter += 1 
        if counter is len(words_to_check): 
            IPsec_SA_counter += 1
    if IPsec_SA_counter is 0:
        return False
    else:
        return True


# Принимает: статус туннеля (True/False) + ТГ токен бота + ID чата ТГ + сообщение
# Выполняет: отправку уведомления о падении туннеля
# Возвращает: -
def generate_notification_message(tunnel_status, telegram_token, chat_id, message):
    if tunnel_status is True:
        print(f"UP at {datetime.now()}")
        return
    else:
        print(f"DOWN at {datetime.now()}")
        telebot.TeleBot(telegram_token, parse_mode=None).send_message(chat_id, message) 
        return


if __name__ == "__main__":
    # Информация об устройстве
    device = {
        "device_type": "eltex_esr",
        "ip": "YOURR",
        "port": "YOURR",
        "username": "YOURR",
        "password": "YOURR",
    }
    # Show команда
    cmd = ["show security ipsec vpn status"]
    # Слова, по которым будет происходить проверка состояния туннеля
    words_to_check = ["Established", # Необходимый статус - Established
                   "YOURR", # src ip
                   "YOURR", # dst ip
                   "YOURR"] # Имя VPN`а
    # Результат выполнения функции send_show_command
    result = send_show_command(device, cmd)
    # Преобразование цельной строки в массив строк
    formatted_result = (result.get("show security ipsec vpn status")).split('\n')
    # Статус туннеля
    tunnel_status = check_tunnel_status(formatted_result, words_to_check)
    # Информация для формирования сообщения
    message_info = {
        "telegram_token": "YOURR", # токен ТГ бота
        "chat_id": "YOURR", # ID чата ТГ
        "message": "YOURR", # Сообщение для отправки в ТГ чат
    }
    generate_notification_message(tunnel_status, 
                                message_info["telegram_token"],
                                message_info["chat_id"],
                                message_info["message"])
