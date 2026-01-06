from flask import Flask
from flask_apscheduler import APScheduler
from cadastrando_produtos_zig import *

app = Flask(__name__)

scheduler = APScheduler()

@scheduler.task('interval', id='my_job', seconds=5)
def my_job():
    print('Iniciando rotina de cadastro dos produtos da ZIG')

    email = "paulonascimento0910@gmail.com",
    password = "shwzichufwbrrsqn"    
    
    APP_KEY = '5521527811800'
    APP_SECRET = '9cff454af6348882c175d91a11f0d5d9'

    REDE ="4a7eeb7e-f1a4-4ab9-86ee-2472a26f494a"
    TOKEN = "97d12c95488644a583036818050c3f7c4ed7d40cdc534574baba3b217dfe137e"

    PREFIXO_EMPRESA = 'PTF-'
    'Cadastro de produtos'
    'Envio do email dos produtos cadastrados'
    'Cadastro do pedido'
    'Envio do email dos pedidos cadastrados'
    
    rotina_produtos_zig(APP_KEY,APP_SECRET,REDE,TOKEN,email,password)
    



if __name__ == '__main__':

    #scheduler.init_app(app)

    #scheduler.start()

    #app.run()

    email = "paulonascimento0910@gmail.com",
    password = "shwzichufwbrrsqn"    
    
    APP_KEY = '5521527811800'
    APP_SECRET = '9cff454af6348882c175d91a11f0d5d9'

    REDE ="4a7eeb7e-f1a4-4ab9-86ee-2472a26f494a"
    TOKEN = "97d12c95488644a583036818050c3f7c4ed7d40cdc534574baba3b217dfe137e"

    PREFIXO_EMPRESA = 'PTF-'
    'Cadastro de produtos'
    'Envio do email dos produtos cadastrados'
    'Cadastro do pedido'
    'Envio do email dos pedidos cadastrados'
    
    for day in range(7,1,-1):
        rotina_produtos_zig(APP_KEY,APP_SECRET,REDE,TOKEN,email,password,dias_retroativos=day)

        time.sleep(30)


