from pydoc import describe

import boto3
from getpass import getpass
from botocore.exceptions import ClientError

ec2 = boto3.client('ec2')
s3 = boto3.client('s3')
rds = boto3.client('rds')

#Creamos el Bucket
bucket_name = 'obligatorio-devops-boto3'
file_path = 'obligatorio.zip'
object_name = file_path.split('/')[-1]

try:
    s3.create_bucket(Bucket=bucket_name)
    print(f"Bucket creado: {bucket_name}")
except ClientError as e:
    if e.response['Error']['Code'] == 'BucketAlreadyOwnedByYou':
        print(f"El bucket {bucket_name} ya existe.")
    else:
        print(f"Error creando bucket: {e}")
        exit(1)

#subir los archivos al bucket S3

try:
    s3.upload_file(file_path, bucket_name,object_name)
    print(f"Archivo {file_path} subido a s3://{bucket_name}/{object_name}")
except FileNotFoundError:
    print(f"El archivo {file_path} no existe en el directorio actual.")
    exit(1)
except ClientError as e:
    print(f"Error subiendo archivo al bucket: {e}")
    exit(1)

#Security Group para ec2

sg_name ='ec2-web-sg'
sg_desc ='Security group para la web'

resp = ec2.describe_security_groups(
    Filters=[{'Name':'group-name','Values': [sg_name]}]
)
if resp['SecurityGroups']:
    ec2_sg_id=resp['SecurityGroups'][0]['GroupId']
    print(f"El Security Group {ec2_sg_id} ya existe, lo reutilizare")
else:
    ec2_sg_id = ec2.create_security_group(
        GroupName='ec2-web-sg',
        Description='Security group para la web'
)
print(f"Security Group de EC2 creado con exito: {ec2_sg_id}")

#Permitimos el trafico de HTTP(Puerto 80) para la app

try:
    ec2.authorize_security_group_ingress(
        GroupId=ec2_sg_id,
        IpPermissions=[
            {
                'IpProtocol':'tcp',
                'FromPort':80,
                'ToPort':80,
                'IpRanges':[{'CidrIp': '0.0.0.0/0'}]
            }
        ]
    )
except ClientError as e:
    if e.response['Error']['Code'] == 'InvalidPermission.Duplicate' :
        print(f"La regla ya existe en el Security Group, la voy a reutilizar")
    else:
        raise


#Security Group para RDS

sg_name_rds ='rds_sg'
sg_desc_rds ='SG para la base de datos'

resp = ec2.describe_security_groups(
    Filters=[{'Name':'group-name','Values': [sg_name_rds]}]
)
if resp['SecurityGroups']:
    rds_sg_id=resp['SecurityGroups'][0]['GroupId']
    print(f"El Security Group {rds_sg_id} ya existe, lo reutilizare")
else:
    rds_sg_id = rds.create_security_group(
        GroupName= 'rds_sg',
        Description='SG para la base de datos'
)

print(f"Security Group de RDS creado con exito: {rds_sg_id}")

#Permitimos que RDS pueda acceder a travez del puerto 3306 desde la EC2

try:
    ec2.authorize_security_group_ingress(
        GroupId=rds_sg_id,
        IpPermissions=[
            {
                'IpProtocol':'tcp',
                'FromPort':3306,
                'ToPort':3306,
                'UserIdGroupPairs':[{'GroupId': ec2_sg_id}]
            }
        ]
    )
except ClientError as e:
    if e.response['Error']['Code'] == 'InvalidPermission.Duplicate' :
        print(f"La regla ya existe en el Security Group, la voy a reutilizar")
    else:
        raise

# Creamos RDS con sus parámetros

DB_INSTANCE_ID = 'app-mysql-2'
DB_NAME = 'demo_db'
DB_USER = 'admin'

#Solicitamos la password a traves de un input
DB_PASS = getpass("Introduce la contraseña del admin RDS: ")

if not DB_PASS:
    raise Exception('Por favor ingrese una contraseña valida.')

try:
    rds.create_db_instance(
        DBInstanceIdentifier=DB_INSTANCE_ID,
        AllocatedStorage=20,
        DBInstanceClass='db.t3.micro',
        Engine='mysql',
        MasterUsername=DB_USER,
        MasterUserPassword=DB_PASS,
        DBName=DB_NAME,
        PubliclyAccessible=True,
        BackupRetentionPeriod=0,
        VpcSecurityGroupIds=[rds_sg_id]
    )
    print(f"Instancia RDS {DB_INSTANCE_ID} creada correctamente.")

except rds.exceptions.DBInstanceAlreadyExistsFault:

    print(f"La instancia {DB_INSTANCE_ID} ya existe.")

#Colocamos un mensaje en pantalla mientras la instancia inicie
print(f"Espere mientras se crea la instancia")

#esperamos a que la instancia este creada
waiter = rds.get_waiter('db_instance_available')
waiter.wait(DBInstanceIdentifier=DB_INSTANCE_ID)

#Sacamos la informacion de la instancia
resp_db = rds.describe_db_instances(DBInstanceIdentifier=DB_INSTANCE_ID)
rds_endpoint = resp_db ['DBInstances'][0]['Endpoint']['Address']


user_data = f'''#!/bin/bash
yum update -y
yum install -y httpd unzip awscli php php-mysqlnd mariadb105 -y
systemctl start httpd
systemctl enable httpd

#Creamos la carpeta donde se va a alojar la aplicacion y nos posicionamos en ella
mkdir -p /var/www/html/app
cd /var/www/html/app

#Descargamos el zip desde la instancia S3
#aws s3 cp s3://{bucket_name}/{object_name} /var/www/html/app/obligatorio.zip
aws s3 cp s3://{bucket_name}/{object_name} /tmp/obligatorio.zip

#Descomprimimos el archivo de la aplicacion
#unzip -o /var/www/html/app/obligatorio.zip -d /var/www/html/app/obligatorio-main
unzip -o /tmp/obligatorio.zip -d /tmp/

cp /tmp/obligatorio-main/app.css /var/www/html/app.css
cp /tmp/obligatorio-main/app.js /var/www/html/app.js
cp /tmp/obligatorio-main/config.php /var/www/html/config.php
cp /tmp/obligatorio-main/index.html /var/www/html/index.html
cp /tmp/obligatorio-main/index.php /var/www/html/index.php
cp /tmp/obligatorio-main/login.css /var/www/html/login.css
cp /tmp/obligatorio-main/login.html /var/www/html/login.html
cp /tmp/obligatorio-main/login.js /var/www/html/login.js
cp /tmp/obligatorio-main/login.php /var/www/html/login.php
cp /tmp/obligatorio-main/login.php /var/www/init_db.sql


mysql -h {rds_endpoint} -u {DB_USER} -p{DB_PASS} {DB_NAME} < /var/www/init_db.sql
   
sudo tee /var/www/.env >/dev/null <<'ENV'
DB_HOST={rds_endpoint}
DB_NAME={DB_NAME}
DB_USER={DB_USER}
DB_PASS={DB_PASS}

ENV

sudo chown apache:apache /var/www/.env
sudo chmod 600 /var/www/.env```

sudo chown -R apache:apache /var/www/html
sudo chmod -R 755 /var/www/html

echo "La aplicacion se desplego correctamente" > /var/www/html/app/obligatorio-main/index.html

#Reiniciamos apache
systemctl restart httpd
'''

# Lanzamos la instancia EC2 con el bash anterior
ec2_response = ec2.run_instances(
    ImageId='ami-06b21ccaeff8cd686',
    InstanceType='t2.micro',
    MinCount=1,
    MaxCount=1,
    IamInstanceProfile={'Name': 'LabInstanceProfile'},
    SecurityGroupIds=[ec2_sg_id],
    UserData=user_data

)

# Obtenemos el ID de la instancia creada
ec2_id = ec2_response['Instances'][0]['InstanceId']

#Creamos un TAG
ec2.create_tags(
    Resources=[ec2_id],
    Tags=[{'Key': 'Name', 'Value': 'ec2-web'}]
)
print(f"Instancia creada con ID: {ec2_id} y nombre de instancia 'ec2-web'")

#Esperamos que la instancia este corriendo
ec2.get_waiter('instance_status_ok').wait(InstanceIds=[ec2_id])




#'Endpoint': {
#            'Address': 'string',



#dejar donde tienen que ir y corregir nombres de variables

#Comandos para instalar app en repo

#EC2
#https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2.html

#Crear Instancias EC2
#https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2/client/run_instances.html

#Crear Tags
#https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2/client/create_tags.html

#Waiter para EC2
#https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2/waiter/InstanceStatusOk.html

#-----------------------------------------------------------------------------------------------

#S3
#https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html

#Crear Bucket S3
#https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3/client/create_bucket.html

#Subir archivos S3
#https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3/client/upload_file.html


#-----------------------------------------------------------------------------------------------

#RDS
#https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/rds.html

#Creamos instancia de RDS
#https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/rds/client/create_db_instance.html



#Documentacion de Security Group
#https://boto3.amazonaws.com/v1/documentation/api/latest/guide/ec2-example-security-group.html

#Crear Security Groups
#https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2/client/create_security_group.html

#Autorizar Security Groups
#https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2/client/authorize_security_group_ingress.html

#Instancias EC2
#https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2/client/run_instances.html




