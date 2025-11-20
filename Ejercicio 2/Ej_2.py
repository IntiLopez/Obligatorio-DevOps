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

#Security Group para RDS

ec2_sg = ec2.create_security_group(
    GroupName='ec2-web-sg',
    Description='Security group para la web'
)

#Permitimos el trafico de HTTP(Puerto 80) para la app

ec2.authorize_security_group_ingress(
    GroupId=ec2_sg['GroupId'],
    IpPermissions=[
        {
            'IpProtocol':'tcp',
            'FromPort':80,
            'ToPort':80,
            'IpRanges':[{'CidrIp': '0.0.0.0/0'}]
        }
    ]
)
print(f"Security Group de EC creado con exito: {ec2_sg['GroupId']}")

#Security Group para RDS

rds_sg = ec2.create_security_group(
    GroupName= 'rds_sg',
    Description='SG para la base de datos'
)

#Permitimos que RDS pueda acceder a travez del puerto 3306 desde la EC2

ec2.authorize_security_group_ingress(
    GroupId=rds_sg['GroupId'],
    IpPermissions=[
        {
            'IpProtocol':'tcp',
            'FromPort':3306,
            'ToPort':3306,
            'UserIdGroupPairs':[{'GroupId': ec2_sg['GroupId']}]
        }
    ]
)
print(f"Security Group de RDS creado con exito: {rds_sg['GroupId']}")

user_data = f'''#!/bin/bash
yum update -y
yum install -y httpd unzip awscli php php-mysqlnd -y
systemctl start httpd
systemctl enable httpd

#Creamos la carpeta donde se va a alojar la aplicacion y nos posicionamos en ella
mkdir -p /var/www/html/app
cd /var/www/html/app

#Descargamos el zip desde la instancia S3
aws s3 cp s3://{bucket_name}/{object_name} /var/www/html/obligatorio.zip

#Descomprimimos el archivo de la aplicacion
unzip -o /var/www/html/obligatorio.zip -d /var/www/html/obligatorio-main
echo "La aplicacion se desplego correctamente desde S3" > /var/www/html/index.html

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
    SecurityGroupIds=[ec2_sg['GroupId']],
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

#Colocamos un mensaje en pantalla mientras la instancia inicie
print(f"Espere mientras inicia la instancia")

# Creamos RDS con sus parámetros

DB_INSTANCE_ID = 'app-mysql'
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
        VpcSecurityGroupIds=[rds_sg['GroupId']]
    )
    print(f"Instancia RDS {DB_INSTANCE_ID} creada correctamente.")

except rds.exceptions.DBInstanceAlreadyExistsFault:

    print(f"La instancia {DB_INSTANCE_ID} ya existe.")




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




