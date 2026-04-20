#!/bin/bash
# Script de verificação de DNS
# Date:20-04-2026
# Autor: Smith Braz

if [ "$1" == "" ]

then

echo "#########################################"
echo "#        DNS Search by Smith Braz       #"
echo "#########################################"
echo "# Use mode: $0 dominio.xyz #"
echo "#########################################"
echo "#   Exemplo: ./script.sh dominio.xyz    #"
echo "#########################################"

else

echo "#########################################"
echo "#     Realizando verificação de SOA     #"
echo "#########################################"
host -t SOA $1
echo "#########################################"
echo "#     Realizando verificação de IPv4    #"
echo "#########################################"
host -t A $1
echo "#########################################"
echo "#    Realizando verificação de IPv6     #"
echo "#########################################"
host -t AAAA $1
echo "#########################################"
echo "#     Realizando verificação de DNS     #"
echo "#########################################"
host -t NS $1
echo "#########################################"
echo "#    Realizando verificação de CNAME    #"
echo "#########################################"
host -t CNAME $1
echo "#########################################"
echo "# Realizando verificação de MAILSERVER  #"
echo "#########################################"
host -t MX $1
echo "#########################################"
echo "#     Realizando verificação de PTR     #"
echo "#########################################"
host -t PTR $1
echo "#########################################"
echo "#    Realizando verificação de HINFO    #"
echo "#########################################"
host -t HINFO $1
echo "#########################################"
echo "#     Realizando verificação de TXT     #"
echo "#########################################"
host -t TXT $1
echo "#########################################"
echo "#    Realizando verificação de Geral    #"
echo "#########################################"
host -a $1
echo "#########################################"
echo "# Realizando verificação de DNS Reverso #"
echo "#########################################"
for ns in $(host -t NS $1 | cut -d " " -f4);do host -l $1 $ns;done
echo "#########################################"

fi
