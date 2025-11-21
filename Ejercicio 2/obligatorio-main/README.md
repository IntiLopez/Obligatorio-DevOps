# Aplicación PHP + MySQL (2 capas)

## Instalación

Lea atentamente las especificaciones del README para poder asegurar una instalacion exitosa de la aplicacion

## Instalación Apache (httpd) + PHP-FPM

```bash
# 1) Actualiza índices y paquetes
sudo dnf clean all
sudo dnf makecache
sudo dnf -y update

# 2) Instala Apache + PHP 8.4 + mariadb y extensiones típicas
sudo dnf -y install httpd php php-cli php-fpm php-common php-mysqlnd mariadb105

# 3) Habilita y arranca servicios
sudo systemctl enable --now httpd
sudo systemctl enable --now php-fpm

# 4) Asegura que Apache pase .php a PHP-FPM
# En AL2023 normalmente se instala /etc/httpd/conf.d/php-fpm.conf con esto,
# pero si no existiera:
echo '<FilesMatch \.php$>
  SetHandler "proxy:unix:/run/php-fpm/www.sock|fcgi://localhost/"
</FilesMatch>' | sudo tee /etc/httpd/conf.d/php-fpm.conf

# 5) Archivo de prueba
echo "<?php phpinfo(); ?>" | sudo tee /var/www/html/info.php

# 6) Reinicia para tomar config
sudo systemctl restart httpd php-fpm
```




### Pasos de despliegue

1. **Asegúrate de que todos los archivos de la aplicación estén en `/var/www/html`**.
  - Los archivos del repositorio (excepto el README y init_db.sql) deben encontrarse en la ruta `/var/www/html`
  - Fuera del **webroot**, en /var/www debes poner el archivo init_db.sql y el archivo .env que crearás más adelante, esta es una medida simple de seguridad para evitar que los archivos puedan ser descargados al sacarlos del **webroot**


2. **Configura la base de datos (RDS):**
   - Crea una instancia de Amazon RDS MySQL y toma nota de:
     - Endpoint DNS
     - Usuario y contraseña
     - Nombre de la base de datos
   - Asegúrate de que el Security Group de RDS permita conexiones desde la IP pública de tu instancia EC2 (puerto 3306).
   - Ejecuta el script `init_db.sql` desde tu EC2 para crear la tabla y los datos:
     ```sh
     mysql -h <endpoint-rds> -u <usuario> -p<contraseña> <nombre_db> < /var/www/init_db.sql
     ```
   - Crea el archivo `.env` para que el `config.php` tome el endpoint, usuario, contraseña y base de datos de tu RDS, además le agregamos las variables **APP_USER** y **APP_PASS**
     ```bash
        sudo tee /var/www/.env >/dev/null <<'ENV'
        DB_HOST=<ENDPOINT>
        DB_NAME=<DB_NAME>
        DB_USER=<DB_USER>
        DB_PASS=<DB_PASS>

        APP_USER=<APP_USER>
        APP_PASS=<APP_PASS>
        ENV

        sudo chown apache:apache /var/www/.env
        sudo chmod 600 /var/www/.env```


3. **Verifica permisos:**
   - Asegúrate de que los archivos sean legibles por el usuario de Apache:
     ```sh
     sudo chown -R apache:apache /var/www/html
     ```

4. **Reinicia Apache:**
   ```sh
   sudo systemctl restart httpd php-fpm
   ```


5. **Accede a la aplicación:**
   - Abre tu navegador y entra a `http://<IP-de-la-instancia>/info.php` o a la APP
   - En el navegador entra a `http://<IP-de-la-instancia>/login.php`
---

## Usuario y contraseña por defecto

- **Usuario:** `admin`
- **Contraseña:** `admin123`

**Notas:**
- Si falta el favicon.ico, puedes ignorar el error o subir un archivo vacío.
- Si usas otro sistema operativo, adapta los comandos de instalación.
