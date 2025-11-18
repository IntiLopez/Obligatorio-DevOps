import boto3
from getpass import getpass
ssm = boto3.client('ssm')
from botocore.exceptions import ClientError

from setroubleshoot.server import instance_id

ec2 = boto3.client('ec2')

user_data = '''#!/bin/bash
yum update -y
yum install -y httpd
systemctl start httpd
systemctl enable httpd
echo "¡Aplicacion funcionando correctamente!" > /var/www/html/index.html
'''
# Lanzamos la instancia EC2 con el bash anterior
ec2_response = ec2.run_instances(
    ImageId='ami-06b21ccaeff8cd686',
    InstanceType='t2.micro',
    MinCount=1,
    MaxCount=1,
    IamInstanceProfile={'Name': 'Obligatorio_EC2'},
    UserData=user_data
)

# Obtenemos el ID de la instancia creada
ec2_id = ec2_response['Instances'][0]['InstanceId']

#Creamos un TAG
ec2.create_tags(
    Resources=[ec2_id],
    Tags=[{'Key': 'Name', 'Value': 'webserver-devops'}]
)
print(f"Instancia creada con ID: {ec2_id} y tag 'webserver-devops'")

# Creamos RDS con sus parámetros
rds = boto3.client('rds')
DB_INSTANCE_ID = 'app-mysql'
DB_NAME = 'app'
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
        BackupRetentionPeriod=0
    )
    print(f'Instancia RDS {DB_INSTANCE_ID} creada correctamente.')

except rds.exceptions.DBInstanceAlreadyExistsFault:

    print(f'La instancia {DB_INSTANCE_ID} ya existe.')

#Esperamos que la instancia este corriendo
ec2.get_waiter('instance_status_ok').wait(InstanceIds=[instance_id])

s3 = boto3.client('s3')

bucket_name = 'Obligatorio-DevOPs-boto3'
file_path = 'Obligatorio.zip'

try:
    s3.create_bucket(Bucket=Obligatorio-DevOPs-boto3)
    print(f"Bucket creado: {Obligatorio-DevOPs-boto3}")
except ClientError as e:
    if s3.response['Error']['Code'] == 'BucketAlreadyOwnedByYou':
        print(f"El bucket {bucket_name} ya existe y es tuyo.")
    else:
        print(f"Error creando bucket: {e}")
        exit(1)






