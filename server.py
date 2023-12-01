
# import the libarys
from database.db_connect import drop_db, create_db, add_user_and_passw, check_user_and_passw, get_user_id
from knn_sdk.ClassificadorKNN import Classificador
import datetime

import csv
from flask import Flask, render_template, request, jsonify, url_for


TYPING_DATA_PATH = './database/biometria.csv' # Folder where the data will be saved .csv 
LOG_NAME = 'resultados.log'
K = 1
SPLIT = 0.8
app = Flask(__name__, static_folder='./static')

@app.route('/')
def home():
	return render_template('./home/home.html')

@app.route('/cadastro', methods = ['GET', 'POST'])
def cadastro():
	if request.method == 'GET':
		return render_template('./cadastro/cadastro.html')
	elif request.method == 'POST':
		response = dict(request.get_json())
		username  = response['username']
		password = response['password']
		id, result = add_user_and_passw(username, password)

		if result:
			return jsonify({'cadastro_cod': 'UserRegistrySuccess', 'id_usuario': id})
		else:
			return jsonify({'cadastro_cod': 'UsernameAlreadyExist'})


@app.route('/cadastro/biometria', methods = ['POST'])
def biometria():
	if request.method == 'POST':
		response = dict(request.get_json())
		user_id  = response['user_id']
		data = response['data']
		data.append(user_id) # adds the user id to the end of the list
		try:
			with open(TYPING_DATA_PATH, 'a',newline='') as file:			
				writer = csv.writer(file)
				writer.writerow(data)

			return jsonify({'biometric_cod': 'Success'})
		except:
			return jsonify({'biometric_cod': 'It was not possible to register the biometric data'})

@app.route('/treinar/biometria', methods = ['POST'])
def treinar():
	if request.method == 'POST':
		response = dict(request.get_json())
		username  = response['username']
		data = response['data']
		user_id = get_user_id(username)
		if user_id == None: #If a user not registered in the training is typed, still take advantage of the data.
			user_id = 999 
		data.append(user_id) # adds the user id to the end of the list
		try:
			with open(TYPING_DATA_PATH, 'a',newline='' ) as file:			
				writer = csv.writer(file)
				writer.writerow(data)

			return jsonify({'biometric_cod': 'Success'})
		except:
			return jsonify({'biometric_cod': 'It was not possible to register the biometric data'})


@app.route('/login', methods = ['GET'])
def login():
	return render_template('./login/login.html')

@app.route('/login/auth1', methods = ['POST']) # Route to first authentication
def auth1():
	response = dict(request.get_json())
	username  = response['username']
	password = response['password']

	id, result, user_id = check_user_and_passw(username, password)

	if result:
		return jsonify({'auth1_code': 'success', 'id_usuario': user_id})
	else:
		if id == 3:
			return jsonify({'auth1_code': 'UsernameNotExist'})
		elif id == 1:
			return jsonify({'auth1_code': 'PasswordIsWrong'})

@app.route('/login/auth2', methods = ['POST']) # Route to second authentication
def auth2():
	response = dict(request.get_json())
	amostra_digitacao  = response['typing_data']
	user_id = response['user_id']
	
	##### Classificador
	classifica = Classificador(TYPING_DATA_PATH, amostra_digitacao, SPLIT, K)
	resultado = classifica.knn_manhattan_sem_treino()
	cross_val_score = classifica.get_cv_score()

	if str(user_id) in resultado[0]:
		match = True
	else:
		match = False
	
	data_hora_atual = datetime.datetime.now()
	data_atual = data_hora_atual.strftime("%d/%m/%Y %H:%M:%S ")
    
	with open(LOG_NAME, 'a') as arquivo: # Creates the log file
		arquivo.write('[+]  Real User: ')
		arquivo.write(str(user_id))
		arquivo.write(' | Intended User: ')
		arquivo.write(str(resultado[0]))
		arquivo.write(' | Algorithm: ')
		arquivo.write(str(resultado[2]))
		arquivo.write(' | Value of K: ')
		arquivo.write(str(K))
		arquivo.write(' | Match: ')
		arquivo.write(str(match))
		arquivo.write(' | Accuracy: ')
		arquivo.write(str(cross_val_score))
		arquivo.write(' | Data: ')
		arquivo.write(data_atual)
		arquivo.write('\n')

	return jsonify({'user_id':str(user_id), 'predict': str(resultado[0]), 'accuracy': str(cross_val_score), 'result': str(match), 'algoritimo': str(resultado[2])})

@app.route('/treinar', methods = ['GET', 'POST'])
def treina_bio():
	if request.method == 'GET':
		return render_template('./train/train.html')

@app.route('/best_params', methods = ['GET'])
def best_params():
	return render_template('./best_params/best_params.html')

@app.route('/best_params/result', methods = ['GET'])
def best_params_result():
	amostra_digitacao = '' # artifical to allow the use of the class
	classifica = Classificador(TYPING_DATA_PATH, amostra_digitacao, 0.7, 3)
	best_score, best_params, best_estimator = classifica.hyper_parameters_tuning()

	data_hora_atual = datetime.datetime.now()
	data_atual = data_hora_atual.strftime("%d/%m/%Y %H:%M:%S ")

	with open(LOG_NAME, 'a') as arquivo: # Creates the log file
		arquivo.write('[+]  Best Score: ')
		arquivo.write(str(best_score))
		arquivo.write(' |  Best Params: ')
		arquivo.write(str(best_params))
		arquivo.write(' |  Best Estimator: ')
		arquivo.write(str(best_estimator))
		arquivo.write(' | Data: ')
		arquivo.write(data_atual)
		arquivo.write('\n')

	return jsonify({'best_score':str(best_score), 'best_params': str(best_params), 'best_estimator': str(best_estimator) })
	
# Server Start
if __name__ == '__main__':
	app.run(host='127.0.0.1', debug=True, port=3000)
