from flask import Flask, request, render_template, jsonify
import smtplib
import mysql.connector
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__)

db_host = 'localhost'  
db_user = 'root'  
db_password = 'andres72sql'  
db_name = 'correos_distribuidos'

correos_enviados = []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/enviar-correo', methods=['POST'])
def enviar_correo():
    correo_destino = request.form['correo']
    mensaje = request.form['mensaje']

    servidor_smtp = 'smtp-mail.outlook.com'  
    puerto_smtp = 587
    usuario = 'AndresApiDistribuidos@outlook.com'  
    contraseña = 'Andres72UMB' 

    msg = MIMEMultipart()
    msg['From'] = usuario
    msg['To'] = correo_destino
    msg['Subject'] = 'Mensaje Distribuidos'

    msg.attach(MIMEText(mensaje, 'plain'))
    
    

    try:
        servidor = smtplib.SMTP(servidor_smtp, puerto_smtp)
        servidor.starttls()

        servidor.login(usuario, contraseña)

        servidor.sendmail(usuario, correo_destino, msg.as_string())

        correos_enviados.append({
            'destinatario': correo_destino,
            'mensaje': mensaje,
        })

        servidor.quit()
        
        conexion = mysql.connector.connect(
        host=db_host,
        user=db_user,
        password=db_password,
        database=db_name
    )
    
        cursor = conexion.cursor()
        cursor.execute("INSERT INTO correos (destinatario, mensaje) VALUES (%s, %s)", (correo_destino, mensaje))
        conexion.commit()
        cursor.close()
        conexion.close()

        return 'Correo enviado con éxito a {}'.format(correo_destino)
    except Exception as e:
        return 'Error al enviar el correo: {}'.format(str(e))
    
    

@app.route('/lista-correos', methods=['GET'])
def lista_correos():
    conexion = mysql.connector.connect(
        host=db_host,
        user=db_user,
        password=db_password,
        database=db_name
    )

    cursor = conexion.cursor()
    cursor.execute("SELECT destinatario, mensaje FROM correos")
    correos = cursor.fetchall()
    cursor.close()
    conexion.close()

    correos_enviados = [{'destinatario': correo[0], 'mensaje': correo[1]} for correo in correos]

    return jsonify(correos_enviados)

if __name__ == '__main__':
    app.run(debug=True)