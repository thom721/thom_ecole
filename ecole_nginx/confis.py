
# PS C:\Windows\system32> Test-NetConnection -ComputerName 192.168.1.2 -Port 31415

# sudo apt install netcat-traditional -y
#  nc -vz 190.115.169.206 31415
# ComputerName     : 192.168.1.2
# RemoteAddress    : 192.168.1.2
# RemotePort       : 31415
# InterfaceAlias   : Wi-Fi
# SourceAddress    : 192.168.1.2
# TcpTestSucceeded : True



        # response = self.api_handler_.authorisation_request(email=email, password=password, permission=self.permissions_delete)


 
# class MainWindow(QWidget):
#     def __init__(self):
#         super().__init__()

#         self.setWindowTitle("Mon Application Professionnelle")
#         self.setGeometry(300, 300, 600, 400)

#         # Icône de l'application (remplace par le chemin de ton icône)
#         icon_path = "icon.png"  # ou .ico sur Windows
#         self.setWindowIcon(QIcon(icon_path))


#  https://downloads.sourceforge.net/project/symmetricds/symmetricds/symmetricds-3.12.0/symmetric-server-3.12.0.zip

# unzip symmetric-server-3.12.0.zip -d /opt/symmetric-ds


# cd C:\symmetric-ds\bin
# sym.bat --port 31417 --server

# symmetric.bat --port 31415 --server --ssl-keystore "C:/Program Files/ecole-serve/mysql-8.0.41-winx64/certs/client-cert.pem" --ssl-keystore-password your_password

# symmetric.bat --port 31415 --server --ssl-keystore "C:/path/to/client-cert.pem" --ssl-keystore-password ""

# symmetric.bat --port 31415 --server --console ^
#     --ssl-keystore "C:/Program Files/ecole-serve/mysql-8.0.41-winx64/certs/client-cert.pem" ^

# keytool -list -v -keystore "C:/Program Files/ecole-serve/mysql-8.0.41-winx64/certs/client-cert.pem"

# openssl pkcs12 -export ^
#   -in "C:\Program Files\ecole-serve\mysql-8.0.41-winx64\certs\ca.pem" ^
#   -inkey "C:\Program Files\ecole-serve\mysql-8.0.41-winx64\certs\ca-key.pem" ^
#   -out keystore.p12 ^
#   -name symmetricds ^
#   -passout pass:@@@@@@@@

# keytool -importcert ^
#   -file "C:\Program Files\ecole-serve\mysql-8.0.41-winx64\certs\ca.pem" ^
#   -keystore truststore.p12 ^
#   -storetype PKCS12 ^
#   -alias symmetricds-trust ^
#   -storepass @@@@@@@@



# SHOW STATUS LIKE 'Ssl_cipher';

# cd /opt/symmetric-ds/bin
# ./sym --port 31416 --server

# URL officielle Oracle (adaptée à votre version)
# $jdkUrl = "https://download.oracle.com/java/24/latest/jdk-24_windows-x64_bin.exe"
# $expectedHash = "a1b2c3d4..." # Remplacez par le vrai SHA256 de la page Oracle
# $downloadPath = "$env:USERPROFILE\Downloads\jdk-24_windows-x64_bin.exe"

# # Téléchargement avec vérification
# Invoke-WebRequest -Uri $jdkUrl -OutFile $downloadPath
# $actualHash = (Get-FileHash -Path $downloadPath -Algorithm SHA256).Hash
# if ($actualHash -ne $expectedHash) {
#     throw "Erreur: Hash de vérification incorrect!"
# }

# openssl pkcs12 -export -in ca.pem -nokeys -out truststore.p12 -name root -passout pass:1234

       
# openssl pkcs12 -export ^
#   -in client-cert.pem ^
#   -inkey client-key.pem ^
#   -out keystore.p12 ^
#   -name symds ^
#   -CAfile ca.pem ^
#   -caname root ^
#   -passout pass:1234

# openssl pkcs12 -export ^
#   -in ca.pem ^
#   -nokeys ^
#   -out truststore.p12 ^
#   -name root ^
#   -passout pass:1234

# dism /online /Enable-Feature /FeatureName:TelnetClient

# netstat -ano | findstr 31418

# taskkill /PID <PID> /F

# sym.bat console --engine corp-000 --port 31415 --jmx-port 31419

# INSERT INTO sym_node (node_id, external_id, node_group_id, sync_enabled, sync_url, created_at_node_id, oldest_load_time)
# VALUES ('corp:000', '000', 'corp', 1, 'http://192.168.0.110:31415/sync/corp-000', NOW(), NOW());

# INSERT INTO sym_node_security (node_id, node_password, enabled, initial_load_enabled, registration_enabled, sync_url)
# VALUES ('corp:000', 'your_password_here', 1, 1, 1, 'http://192.168.0.110:31415/sync/corp-000');


# INSERT INTO sym_node_security (node_id, node_password, initial_load_enabled, registration_enabled, sync_url)
# VALUES ('corp:000', '@@@@@@@@', 1, 1, 'http://192.168.0.110:31415/sync/corp-000');


#          INSERT INTO sym_node_security (node_id, node_password, registration_enabled, initial_load_enabled)
# VALUES ('corp-000', '@@@@@@@@@@', 1, 1);

# INSERT INTO sym_node (node_id, node_group_id, external_id)
# VALUES ('store-win-node', 'corp', '001');

# INSERT INTO sym_node_security (node_id, node_password)
# VALUES ('store-001', '@@@@@@@@@@');


#  cache                       
#  cache_locks     
#  personal_access_tokens      
#  sessions                      
#             
#  annee_academiques           
#  annees                      
#  classe_facultes             
#  classes                     
#  classes_etudiants           
#  client_infos                
#  cours                       
#  cours_etudiants             
#  depenses                    
#  etudiant_facultes           
#  etudiants                   
#  facultes                    
#  failed_jobs                 
#  frais_dinscriptions         
#  frais_divers                
#  heart_autos                 
#  job_batches                 
#  jobs                        
#  log_actives                 
#  logs                        
#  migrations                  
#  model_has_permissions       
#  model_has_roles             
#  niveau_detudes              
#  niveaux                     
#  notes                       
#  order_items                 
#  paiements                   
#  parametre_paiements         
#  params_exams                
#  password_reset_tokens       
#  permissions                 
#  personnels                  
#  pieces_soumises             
#  pmts                        
#  presences                   
#  professeurs                 
#  profiles                    
#  programmes                  
#  responsables                
#  role_has_permissions        
#  roles                       
#  users                       
#  ventes

# INSERT INTO sym_trigger (trigger_id, source_table_name, channel_id, sync_on_insert, sync_on_update, sync_on_delete, create_time, last_update_time)
# VALUES
# ('annee_academiques', 'annee_academiques', 'default', 1, 1, 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
# ('annees', 'annees', 'default', 1, 1, 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
# ('cache', 'cache', 'default', 1, 1, 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
# ('cache_locks', 'cache_locks', 'default', 1, 1, 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
# ('classe_facultes', 'classe_facultes', 'default', 1, 1, 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
# ('classes', 'classes', 'default', 1, 1, 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
# ('classes_etudiants', 'classes_etudiants', 'default', 1, 1, 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
# ('client_infos', 'client_infos', 'default', 1, 1, 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
# ('cours', 'cours', 'default', 1, 1, 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
# ('cours_etudiants', 'cours_etudiants', 'default', 1, 1, 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
# ('depenses', 'depenses', 'default', 1, 1, 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
# ('etudiant_facultes', 'etudiant_facultes', 'default', 1, 1, 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
# ('etudiants', 'etudiants', 'default', 1, 1, 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
# ('facultes', 'facultes', 'default', 1, 1, 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
# ('failed_jobs', 'failed_jobs', 'default', 1, 1, 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
# ('frais_dinscriptions', 'frais_dinscriptions', 'default', 1, 1, 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
# ('frais_divers', 'frais_divers', 'default', 1, 1, 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
# ('heart_autos', 'heart_autos', 'default', 1, 1, 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
# ('job_batches', 'job_batches', 'default', 1, 1, 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
# ('jobs', 'jobs', 'default', 1, 1, 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
# ('log_actives', 'log_actives', 'default', 1, 1, 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
# ('logs', 'logs', 'default', 1, 1, 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
# ('migrations', 'migrations', 'default', 1, 1, 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
# ('model_has_permissions', 'model_has_permissions', 'default', 1, 1, 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
# ('model_has_roles', 'model_has_roles', 'default', 1, 1, 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
# ('niveau_detudes', 'niveau_detudes', 'default', 1, 1, 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
# ('niveaux', 'niveaux', 'default', 1, 1, 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
# ('notes', 'notes', 'default', 1, 1, 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
# ('order_items', 'order_items', 'default', 1, 1, 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
# ('paiements', 'paiements', 'default', 1, 1, 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
# ('parametre_paiements', 'parametre_paiements', 'default', 1, 1, 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
# ('params_exams', 'params_exams', 'default', 1, 1, 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
# ('password_reset_tokens', 'password_reset_tokens', 'default', 1, 1, 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
# ('permissions', 'permissions', 'default', 1, 1, 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
# ('personal_access_tokens', 'personal_access_tokens', 'default', 1, 1, 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
# ('personnels', 'personnels', 'default', 1, 1, 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
# ('pieces_soumises', 'pieces_soumises', 'default', 1, 1, 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
# ('pmts', 'pmts', 'default', 1, 1, 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
# ('presences', 'presences', 'default', 1, 1, 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
# ('professeurs', 'professeurs', 'default', 1, 1, 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
# ('profiles', 'profiles', 'default', 1, 1, 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
# ('programmes', 'programmes', 'default', 1, 1, 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
# ('responsables', 'responsables', 'default', 1, 1, 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
# ('role_has_permissions', 'role_has_permissions', 'default', 1, 1, 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
# ('roles', 'roles', 'default', 1, 1, 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
# ('sessions', 'sessions', 'default', 1, 1, 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
# ('users', 'users', 'default', 1, 1, 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
# ('ventes', 'ventes', 'default', 1, 1, 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);


# scp "C:\bases_2_aug_2025.sql" root@82.29.153.24:/tmp/

# Créez d'abord la base de données
# mysql -u root -p -e "CREATE DATABASE lemignon CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;"

# mysql -u root -p -Nse 'SHOW TABLES' nom_de_votre_base | while read table; do mysql -u root -p -e "DROP TABLE $table" nom_de_votre_base; done

# sym_node

# INSERT INTO sym_node (
#     node_id,
#     node_group_id,
#     external_id,
#     sync_enabled,
#     sync_url,
#     schema_version,
#     database_type,
#     database_version,
#     created_at_node_id
# ) VALUES (
#     'win-node',
#     'main',
#     'win',
#     1,
#     'http://192.168.0.110:31415/sync/main',
#     null,
#     'mysql',
#     '8.0',
#     'win-node'
# );

# INSERT INTO sym_node (
#     node_id,
#     node_group_id,
#     external_id,
#     sync_enabled,
#     sync_url,
#     schema_version,
#     database_type,
#     database_version,
#     created_at_node_id
# ) VALUES (
#     'deb-node',
#     'main',
#     'deb',
#     1,
#     'https://82.29.153.24:31415/sync/main',
#     null,
#     'MariaDB',
#     '10.11.11',
#     'deb-node'
# );

# INSERT INTO sym_node_security (node_id, node_password, registration_enabled, created_at_node_id)
# VALUES ('deb-node', '@@@@@@@@', 1, 'win-node');


# INSERT INTO sym_node_security (node_id, node_password, registration_enabled, created_at_node_id)
# VALUES ('win-node', '@@@@@@@@', 1, 'deb-node');


# INSERT INTO sym_node_security (node_id, node_password, registration_enabled)
# VALUES
#   ('win-node', '@@@@@@@@', 1),
#   ('deb-node', '@@@@@@@@', 1);

# INSERT INTO sym_node_identity (node_id) VALUES ('win-node');
# symadmin --engine deb-node open-registration win-node main
# symadmin --engine win-node open-registration deb-node main


# Action	Faire sur win-node ?	Faire sur deb-node ?
# Créer sym_node_group	Oui	Oui
# Ajouter tous les nœuds dans sym_node et sym_node_security	Oui	Oui
# Créer le sym_node_group_link	Oui	Oui
# Créer sym_router	Oui	Oui
# Créer les sym_trigger	Oui	Oui
# Créer sym_trigger_router	Oui	Oui
# Configurer engine.properties	Oui (avec son propre node_id)	Oui (avec son propre node_id)

# 1️⃣ Script SQL à exécuter sur Windows (win-node)

# -- 1. Groupe unique
# INSERT INTO sym_node_group (node_group_id, description)
# VALUES ('main', 'Groupe unique main full bidirectionnel'),
# VALUES ('relais', 'Groupe unique relais full bidirectionnel');

# -- 2. Nœuds
# INSERT INTO sym_node (node_id, node_group_id, external_id, sync_enabled, sync_url)
# VALUES 
# ('win-node', 'main', 'win-node', 1, 'http://190.115.169.206:31415/sync/win-node'),
# ('deb-node', 'main', 'deb-node', 1, 'http://82.29.153.24:31415/sync/deb-node'),
# ('relais-node', 'relais', 'relais-node', 1, 'http://82.29.153.24:31415/sync/deb-node');

# -- 3. Node Identity
# INSERT INTO sym_node_identity (node_id, external_id, node_group_id, sync_enabled, created_at)
# VALUES 
# ('win-node', 'win-node', 'main', 1, NOW()),
# ('deb-node', 'deb-node', 'main', 1, NOW());

# -- 4. Node Security
# INSERT INTO sym_node_security (node_id, registration_enabled, node_password)
# VALUES
# ('win-node', 1, '@@@@@@@@'),
# ('deb-node', 1, '@@@@@@@@');

# -- 5. Node Group Link
# # INSERT INTO sym_node_group_link (source_node_group_id, target_node_group_id, data_event_action)
# # VALUES ('main', 'main', 'W');
# INSERT INTO sym_node_group_link (source_node_group_id, target_node_group_id, data_event_action, sync_config_enabled, sync_sql_enabled, is_reversible, create_time)
# VALUES ('main', 'main', 'W', 1, 1, 1, NOW());

# -- 6. Canal
# INSERT INTO sym_channel (channel_id, processing_order, max_batch_size, enabled, description)
# VALUES ('default', 1, 100000, 1, 'Canal par défaut');

# -- 7. Router
# INSERT INTO sym_router (router_id, source_node_group_id, target_node_group_id, router_type,last_update_time,create_time)
# VALUES ('main-router', 'main', 'main', 'default', NOW(), NOW());




# 2️⃣ Script SQL à exécuter sur Debian (deb-node)

# -- 1. Groupe unique
# INSERT INTO sym_node_group (node_group_id, description)
# VALUES ('main', 'Groupe unique full bidirectionnel');

# -- 2. Nœuds
# INSERT INTO sym_node (node_id, node_group_id, external_id, sync_enabled, sync_url)
# VALUES 
# ('deb-node', 'main', 'deb-node', 1, 'http://82.29.153.24:31415/sync/deb-node'),
# ('win-node', 'main', 'win-node', 1, 'http://190.115.169.206:31415/sync/win-node');

# -- 3. Node Identity
# INSERT INTO sym_node_identity (node_id, external_id, node_group_id, sync_enabled, created_at)
# VALUES 
# ('deb-node', 'deb-node', 'main', 1, NOW()),
# ('win-node', 'win-node', 'main', 1, NOW());

# -- 4. Node Security
# INSERT INTO sym_node_security (node_id, registration_enabled, node_password, created_at)
# VALUES
# ('deb-node', 1, '@@@@@@@@', NOW()),
# ('win-node', 1, '@@@@@@@@', NOW());

# -- 5. Node Group Link
# INSERT INTO sym_node_group_link (source_node_group_id, target_node_group_id, data_event_action)
# VALUES ('main', 'main', 'W');

# INSERT INTO sym_node_group_link (source_node_group_id, target_node_group_id, data_event_action, sync_config_enabled, sync_sql_enabled, is_reversible, create_time)
# VALUES ('main', 'main', 'W', 1, 1, 1, NOW());

# -- 6. Canal
# INSERT INTO sym_channel (channel_id, processing_order, max_batch_size, enabled, description)
# VALUES ('default', 1, 100000, 1, 'Canal par défaut');

# INSERT INTO sym_router (router_id, source_node_group_id, target_node_group_id, router_type,last_update_time,create_time)
# VALUES ('main-router', 'main', 'main', 'default', NOW(), NOW());


# wget https://dev.mysql.com/get/mysql-apt-config_0.8.33-1_all.deb
# sudo dpkg -i mysql-apt-config_0.8.33-1_all.deb
# sudo apt update
# sudo apt install mysql-server

# sudo apt-get update
# sudo apt-get install mysql-server

# sudo systemctl stop mysql
# sudo apt-get remove --purge mysql-server mysql-client mysql-common -y
# sudo apt-get autoremove -y
# sudo apt-get autoclean
# sudo rm -rf /etc/mysql /var/lib/mysql /var/log/mysql

# sudo apt-get purge mysql-server mysql-client mysql-common -y
# sudo apt-get autoremove -y
# sudo apt-get autoclean
# sudo apt install mysql-server -y






# CREATE USER 'repl'@'82.29.153.24' IDENTIFIED BY '@@@@@@@@';
# GRANT REPLICATION SLAVE ON *.* TO 'repl'@'82.29.153.24';
# FLUSH PRIVILEGES;

# CREATE USER 'repl'@'10.10.0.3' IDENTIFIED WITH caching_sha2_password BY '@@@@@@@@';
# GRANT ALL PRIVILEGES ON lemignon.* TO 'repl'@'10.10.0.3';;

# GRANT PROCESS ON *.* TO 'repl'@'10.10.0.3';
# FLUSH PRIVILEGES;
# FLUSH PRIVILEGES;

# drop database lemignon;
# create database lemignon;


# CHANGE MASTER TO
#   MASTER_HOST='10.10.0.1',
# MASTER_PORT=3306,
#   MASTER_USER='repl',
#   MASTER_PASSWORD='@@@@@@@@',
#   MASTER_AUTO_POSITION=1;

# STOP SLAVE;
# CHANGE MASTER TO
#   MASTER_HOST='10.10.0.1',
#   MASTER_USER='repl',
#   MASTER_PASSWORD='@@@@@@@@',
#   MASTER_PORT=3306,
# MASTER_AUTO_POSITION=1;
# START SLAVE;
# SHOW SLAVE STATUS\G

# SHOW BINARY LOGS; 

# PURGE BINARY LOGS BEFORE '2025-08-18 00:00:00';


# STOP SLAVE;
# SET GLOBAL gtid_purged='822d55af-73b4-11f0-a5f5-b4b52f7ff6af:1-2627,a5225dd4-7aab-11f0-9104-bc2411cd5f6c:1-3074,f4ab0b01-7b87-11f0-8620-bc2411cd5f6c:1-6';
# START SLAVE;

# | gtid_executed | 822d55af-73b4-11f0-a5f5-b4b52f7ff6af:1-2627,
# a5225dd4-7aab-11f0-9104-bc2411cd5f6c:1-3074,
# f4ab0b01-7b87-11f0-8620-bc2411cd5f6c:1-6 |

# STOP SLAVE;
# RESET MASTER; 

# STOP SLAVE;
# CHANGE MASTER TO
#   MASTER_SSL=0,
#   MASTER_SSL_CA='',
#   MASTER_SSL_CERT='',
#   MASTER_SSL_KEY='',
#   GET_MASTER_PUBLIC_KEY=1;  
# START SLAVE;
# SHOW SLAVE STATUS\G


# STOP SLAVE;
# CHANGE MASTER TO
#   MASTER_HOST='10.10.0.2',
#   MASTER_USER='repl',
#   MASTER_PASSWORD='@@@@@@@@',
#   MASTER_PORT=3307,
#   MASTER_SSL=1,
#   MASTER_SSL_CA='/tmp/ca.pem',
#   MASTER_SSL_CERT='/tmp/client-cert.pem',
#   MASTER_SSL_KEY='/tmp/client-key.pem',
# MASTER_AUTO_POSITION=1;
# START SLAVE;
# SHOW SLAVE STATUS\G

# sudo mysqld_safe --skip-grant-tables &

# sudo rm -rf /var/lib/mysql/*
# sudo rm -rf /var/run/mysqld/mysqld.sock
# sudo rm -rf /var/log/mysql/*
 

#  sudo mysqld --initialize --user=mysql --datadir=/var/lib/mysql
# sudo grep 'temporary password' /var/log/mysql/error.log

# sudo pkill mysqld_safe
# sudo pkill mysqld

# ALTER USER 'root'@'localhost' IDENTIFIED WITH caching_sha2_password BY '@#1900';
# ALTER USER 'root'@'127.0.0.1' IDENTIFIED WITH caching_sha2_password BY '@#1900';
# FLUSH PRIVILEGES;



# CHANGE MASTER TO 
#     MASTER_HOST='10.10.0.1',
#     MASTER_USER='repl',
#     MASTER_PASSWORD='@@@@@@@',
#     MASTER_PORT=3306,
#     MASTER_SSL=1,
#     MASTER_SSL_CA='C:\ca.pem',
#     MASTER_SSL_VERIFY_SERVER_CERT=0;
# START SLAVE;


# START SLAVE;
# SHOW SLAVE STATUS\G

# mysqladmin -u root -p flush-hosts

# Vérifier les hôtes bloqués :
# sql
# SELECT * FROM performance_schema.host_cache;

# Configurer les paramètres MySQL (my.cnf/my.ini) :
# ini
# [mysqld]
# max_connect_errors=100000  # Augmenter cette valeur
# wait_timeout=28800
# interactive_timeout=28800


# sudo iptables -A INPUT -p tcp --dport 22 -j ACCEPT
# sudo iptables-save > /etc/iptables/rules.v4


# sudo apt install ufw -y


# sudo ufw allow 22/tcp
# sudo ufw reload
# sudo ufw status

# New-NetFirewallRule -Name "SSH" -DisplayName "OpenSSH" -Enabled True -Direction Inbound -Protocol TCP -Action Allow -LocalPort 22


# cd "C:\Program Files\OpenSSH"
# .\install-sshd.ps1
# Start-Service sshd
# Set-Service sshd -StartupType Automatic


# SELECT batch_id, node_id, channel_id, status, last_update_time
# FROM sym_outgoing_batch
# WHERE node_id = 'win-node'
# ORDER BY last_update_time DESC;


# sudo nano /etc/systemd/system/symmetricds.service

# [Unit]
# Description=SymmetricDS Service
# After=network.target

# [Service]
# Type=forking
# User=root
# Group=root
# WorkingDirectory=/opt/symmtric-ds
# ExecStart=/opt/symmtric-ds/bin/sym_service start
# ExecStop=/opt/symmtric-ds/bin/sym_service stop
# ExecReload=/opt/symmtric-ds/bin/sym_service restart
# Restart=on-failure

# [Install]
# WantedBy=multi-user.target

# sudo /opt/symmetric-ds/bin/sym_service start
# sudo systemctl daemon-reload
# sudo systemctl enable symmetricds
# sudo systemctl start symmetricds
# sudo systemctl status symmetricds

# # journalctl -xeu symmetricds.service
# sudo lsof -i :31415
# # ou
# sudo netstat -tulnp | grep 31415

# sudo kill -9 773845


            # Réplication
            # server-id=1
            # log_bin=mysql-bin
            # # binlog_format=ROW
            # binlog_row_image=FULL
            # # expire_logs_days=30
            # sync_binlog=1

            # R�plication
            # server-id=1
            # log_bin=mysql-bin 
            # binlog_row_image=FULL
            # expire_logs_days=360
            # sync_binlog=1

            # binlog_format=ROW
            # gtid_mode=ON
            # enforce_gtid_consistency=ON
            # master_info_repository=TABLE
            # relay_log_info_repository=TABLE
            # relay_log_recovery=ON
            # log_slave_updates=ON
            # sync_binlog=1
            # innodb_flush_log_at_trx_commit=1
            
            # log_slave_updates = ON



