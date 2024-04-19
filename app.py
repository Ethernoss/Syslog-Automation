import paramiko
from flask import Flask, render_template, request

app = Flask(__name__)

def extract_logs(connection, router_command):
    try:
        command = f"tail -n 1000 /var/log/syslog | grep '{router_command}'" # Comando para buscar por el nombre del router
        stdin, stdout, stderr = connection.exec_command(command) # Ejecutar el comando en el servidor
        
        filtered_logs = [] # Lista para filtrar la salida de stdout (la ejecucion del comando)
        for line in stdout: # Iterar sobre la salida de stdout (todos los logs)
       # if '%SYS' in line: #Si el log contiene '%SYS', agregarlo a la lista filtered_logs
            log_parts = line.split() # Dividir el log en partes
            timestamp = ' '.join(log_parts[:3]) # Concatenar las primeras 3 partes del log (timestamp)
            ip_address = log_parts[3] # Obtener la IP del log
            severity = log_parts[9].split('-')[1] # Obtener la severidad del log
            hostname = log_parts[5].replace(':','') # Obtener el hostname del log
            message = ' '.join(log_parts[10:]) # Obtener el mensaje del log
            # Crear un diccionario con los datos del log
            log = {
                "Timestamp": timestamp,
                "IP Address": ip_address,
                "Severity": severity,
                "Hostname": hostname,
                "Message": message
            }
            filtered_logs.append(log) # Agregar el log a la lista filtered_logs
        
        return filtered_logs # Devolver la lista filtered_logs
    except Exception as e:
        print(f"Failed to extract logs: {e}") 
        return []

def connect(server):
    client = paramiko.SSHClient() # Variable para crear la conexion al servidor
    try:
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy()) # Agregar la politica de llave del host
        client.connect(server['ip'], username=server['user'], password=server['pwd']) # Conexion al servidor con credenciales
        return client
    except paramiko.ssh_exception.AuthenticationException as e: 
        print(f"{server['ip']}: Authentication failed")
        return None

@app.route('/', methods=['GET', 'POST']) # Crear una ruta para la pagina principal
def index():
    if request.method == 'POST': # Verificar si el metodo de la peticion es POST
        router_choice = int(request.form['router']) # Obtener la opcion del router
        router_command = f"Router{router_choice}" # Crear el comando para ejecutar en el router
        # Diccionario con la informacion del servidor
        server_info = { 
            'ip': '192.168.64.129',
            'user': request.form['username'],
            'pwd': request.form['password']
        }
        
        connection = connect(server_info) # Crear la conexion al servidor
        if connection:
            logs = extract_logs(connection, router_command) # Extraer los logs del router
            return render_template('logs.html', logs=logs) # Devolver los logs al usuario
        else:
            return "Failed to connect to the server. Please check your credentials and try again."
    else:
        return render_template('index.html') # Devolver la pagina principal al usuario

if __name__ == "__main__":
    app.run(debug=True)
