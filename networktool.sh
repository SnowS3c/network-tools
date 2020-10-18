#!/bin/bash

'''
TODO:
    Port Scans -> dont show the ip from the machine # localip shows in read
    Port Scans -> option to select a custom target
    Port Scans -> add an option for choose multiple targets
'''

'''
REQUERIMENTS:
    NMAP
    Scapy (Include in module folder)
'''

# COLORS AND TEXT FORMAT
underline=`tput smul`
nounderline=`tput rmul`
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m'


# FILES PATH
iplistf='iplist_result.txt'
nmapf='nmap_result.txt'
portscanf='portscan_result.txt'
synportscanf='syn_portscan_result.txt'

trap trap_ctrlc 2

initialize() {
    net_adapter=($(ip a | grep ^[0-9]: | tr " " ":" | cut -d ":" -f 3))
    for adapt in ${net_adapter[@]}
    do
        if [[ $adapt != "lo" ]] ; then
            default_adapt="$adapt"

            localip=$(ip a | grep "$default_adapt" | tail -1 | tr -s " " ":" | cut -d ":" -f 3 | cut -d "/" -f 1)
            mask=$(ip a | grep "$default_adapt" | tail -1 | tr -s " " ":" | cut -d ":" -f 3 | cut -d "/" -f 2)
            if [[ "$localip" =~ [0-9.]+ ]] ; then
                break
            fi
        fi

    done
}


ipsweep () {
    clear
    echo "###### IPSWEEP ######"

    echo "Your machine ip: $localip"
    echo "Mask: $mask"

    # Check if older result is saved
    [[ -f "$iplistf" ]] && rm -f "$iplistf"
    if [ $mask == "24" ] ; then

        ipred=$(echo $localip | sed "s/.[0-9]\+$/.0/g")
        echo "ip/red: $ipred"
        ipred=$(echo $ipred | sed "s/.0$//")
        for ip in `seq 1 254`
        do
           ping $ipred.$ip -c 1 | grep "64 bytes" | cut -d " " -f 4 | tr -d ":" >> "$iplistf" &
        done
    fi
    wait $!
    cat "$iplistf"
    read -p "IPs saved in file "$iplistf""
}

nmap_f () {
    clear
    echo "##### NMAP #####"
    # Check root privileges
    [ "$(id -u)" -ne 0 ] && echo "Administrative privileges needed" && exit 1
    # Check if older result is saved
    [[ -f "$nmapf" ]] && rm -f "$nmapf"
    for ip in $(cat "$iplistf")
    do
        # Exclude local machine ip from the nmap scan
        ! [[ $localip == "$ip" ]] && nmap -sS -p 80 -T4 $ip >> "$nmapf"
    done
    cat "$nmapf"
    echo
    # AQUI
    read -p "$prompt[nmap_f]Nmap result saved in file "$nmapf""

}

port_scan() {
    cont=1
    echo "#### Targets ####"
    for ip in $(cat "$iplistf")
    do
        echo "$cont: $ip"
        cont=$((cont + 1))
    done
    read -p 'Select a target: ' target_s
    a=($(cat "$iplistf"))
    target=${a[$((target_s - 1))]}
    [[ $target == "" ]] || ! [[ "$target_s" =~ [0-9]+ ]] && read -p 'Select a valid target' && return 1
    [[ "$localip" == "$target" ]] && target="localhost"
    read -p 'Select first port: ' -ei '1' first_port
    read -p 'Select last port: ' -ei '6000' last_port
    read -p 'Want to save the result in a file?[Y/N] ' res
    case $res in
        [yY])
            python3 module/portscanner.py $target $first_port $last_port | tee "$portscanf"
            echo "Scan result saved in file "$portscanf""
            ;;
        *)
            # $1 target, $2 first port, $3 last port
            python3 module/portscanner.py $target $first_port $last_port
            ;;
    esac
    echo
    read -p "Port scan finished."
}

syn_port_scan() {
    clear
    echo "##### SYN PORTSCANNER #####"
    [ "$(id -u)" -ne 0 ] && echo "Administrative privileges needed" && exit 1
    echo "#### Targets ####"
    cont=1
    for ip in $(cat "$iplistf")
    do
        [[ "$ip" == "$localip" ]] && echo -e "${RED}$cont: $ip${NC}" || echo "$cont: $ip"
        cont=$((cont + 1))
    done
    read -p 'Select a target: ' target
    a=($(cat "$iplistf"))
    target=${a[$((target - 1))]}
    [[ "$localip" == "$target" ]] && read -p "Localhost is an invalid target!" && menu
    read -p 'Select first port: ' -ei '1' first_port
    read -p 'Select last port: ' -ei '6000' last_port
    read -p 'Want to save the result in a file?[Y/N] ' res
    case $res in
        [yY])
            python3 module/synportscanner.py $target $first_port $last_port | tee "$synportscanf"
            echo "Scan result saved in file "$synportscanf""
            ;;
        *)
            # $1 target, $2 first port, $3 last port
            python3 module/synportscanner.py $target $first_port $last_port
            ;;
    esac
    echo
    read -p "Port scan finished."
}

trap_ctrlc () {
    echo -e "\nCrtl+C pressed. Closing program"
    exit 2
}

menu () {
    while :
    do
        clear
        cat<<EOF
        ==============================
        NETWORK TOOLS
        ------------------------------
        Please enter your choice:

        Option (1) Ipsweep
        Option (2) Nmap (*)
        Option (3) PortScanner
        Option (4) Silent PortScanner (Slow but sneaky)(*)
               (Q)uit
        ------------------------------
        (*)needs root privileges

EOF
#        read -p "$(cat<<EOF
#        Select an option:
#EOF
#        )" opt
        read -p "$prompt" opt

        case $opt in
            1)
                ipsweep
                ;;
            2)
                nmap_f
                ;;
            3)
                port_scan
                ;;
            4)
                syn_port_scan
                ;;
            [qQ])
                echo "Program Closed"
                exit
                ;;

        esac
    done
}

prompt="${underline}nt1${nounderline} > "
initialize
menu
