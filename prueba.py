import paramiko
from getpass import getpass
import paramiko.ssh_exception
from tabulate import tabulate
from tqdm import tqdm
from time import sleep
from pyfiglet import Figlet
from termcolor import colored

#Una vez que se conecte al servidor, extraer los logs guardados, puede ser guardando en una variable lo que arroje este comando: tail -f /var/log/syslog 
#Filtrar los logs por el nombre del router
def extract_logs(connection):
    router_name = ['Router 1', 'Router 2', 'Router 3']
    
    routers_info = [[idx, name] for idx, name in enumerate(router_name, 1)]
    print(tabulate(routers_info, headers=["ID", "Router"], tablefmt="pretty"))
    choice = int(input("Select a router: "))

    if choice not in range(1, 4):
        print("Invalid choice. Please select a number between 1 and 3.")
        return
    
    router_command = f"Router{choice}"
    
    command = f"tail -n 10000 /var/log/syslog | grep '{router_command}'" # Comando para buscar por el nombre del router
    try:
        stdin, stdout, stderr = connection.exec_command(command) # Ejecutar el comando en el servidor
        filtered_logs = [] # Lista para filtrar la salida de stdout (la ejecucion del comando)
        for line in stdout: # Iterar sobre la salida de stdout (todos los logs)
            if '%SYS' in line: #Si el log contiene '%SYS', agregarlo a la lista filtered_logs
                filtered_logs.append(line.strip())

        # Guardar los logs filtrados en un archivo de texto
        with open(f"Logs-{router_command}.txt", "w+") as archivo:
            archivo.write('\n'.join(filtered_logs))
            
        print("Logs filtered and saved successfully.")
        
    except Exception as e:
        print(f"Command '{command}' failed: {e}")
        return None

      
# Función para conectarme al servidor
def connect(server):
  
  client = paramiko.SSHClient() # Variable para crear conexiones al servidor
  try:
    with tqdm(total=100, position=0, leave=True, desc=f"Connecting to {server['ip']}", unit="%") as pbar:
      client.set_missing_host_key_policy(paramiko.AutoAddPolicy()) # 
      client.connect(server['ip'], username=server['user'], password=server['pwd'])
      for _ in range(100):
        sleep(0.01)  # Simulate connection time
        pbar.update(1)
    return client, print("\n" *100)
  except paramiko.ssh_exception.AuthenticationException as e:
    print(f"{server['ip']}: Authentication failed")
    return None

#Menu de visibilidad
def menu(server, connection):
  
  custom_fig = Figlet(font='slant')
  title_text = colored(custom_fig.renderText('Syslog Extraction'), 'yellow')  # Título en ASCII art
  print(title_text)
  extract_logs(connection)

 
  
def intro():
  custom_fig = Figlet(font='slant')
  title_text = colored(custom_fig.renderText('Welcome to \nSyslog System'), 'yellow')  # Título en ASCII art
  return print(title_text)
  
#Datos generales del servidor en un diccionario
def main():
  intro()
  # Información del servidor en una lista
  srvr_linux = { 
      'ip':  '192.168.64.129',
      'user': input('Username: '),
      'pwd': getpass('Clave: ')
      }
  
  connection, _ = connect(srvr_linux) #Conexion al servidor
  menu(srvr_linux, connection) # Recibe el servidor y la conexion al servidor
  
  
if __name__ == "__main__":
    main()

