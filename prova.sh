ip=$1
mask=$2

cidr_to_netmask() {
  local cidr=$1
  local mask=""
  for ((i=0; i<32; i++)); do
    if ((cidr > 0)); then
      mask+="1"
      ((cidr--))
    else
      mask+="0"
    fi
  done
  echo "$((2#${mask:0:8}))"."$((2#${mask:8:8}))"."$((2#${mask:16:8}))"."$((2#${mask:24:8}))"
}

cidr_to_netmask_flipped() {
  local cidr=$1
  local netmask=$((0xffffffff ^ ( (1 << (32 - cidr)) - 1 ) ))
  
  local ip
  ip=$(printf "%d.%d.%d.%d\n" \
    $(( (netmask >> 24) & 0xFF )) \
    $(( (netmask >> 16) & 0xFF )) \
    $(( (netmask >> 8) & 0xFF )) \
    $(( netmask & 0xFF )) )
  
  local flipped_ip
  IFS='.' read -r a b c d <<< "$ip"
  flipped_ip="$((255 - a)).$((255 - b)).$((255 - c)).$((255 - d))"
  
  echo "$flipped_ip"
}

gateway_ip=$(echo $ip | awk -F. '{print $1"."$2"."$3"."$4+1}')
my_ip=$(echo $ip | awk -F. '{print $1"."$2"."$3"."$4+2}')

echo "Inserisci il test a cui sei interessato:"
read -p "Test: " test

echo "Inserisci il nome CONTAINERlab del nodo target:"
read -p "Target: " target

topology_file="test/$test/topology.clab.yaml"
if [[ ! -f "$topology_file" ]]; then
  echo "Errore: topology.clab.yaml non trovato!"
  exit 1
fi

startup_config_file=""
target_found=false
used_interfaces=()

target_found=false
startup_config_file=""

while IFS= read -r line; do
  if [[ "$line" =~ ^[[:space:]]*([A-Za-z0-9_-]+):[[:space:]]*$ ]]; then
    current_node="${BASH_REMATCH[1]}"
    
    if [[ "$current_node" == "$target" ]]; then
      target_found=true
    else
      target_found=false
    fi
  fi
  
  if $target_found && [[ "$line" =~ startup-config:[[:space:]]*(.*) ]]; then
    startup_config_file="test/$test/${BASH_REMATCH[1]}"
    break
  fi
done < "$topology_file"

if [[ -n "$startup_config_file" ]]; then
  echo "File di configurazione trovato: $startup_config_file"
else
  echo "Errore: Nessun file di configurazione trovato per il nodo $target"
  exit 1
fi

links_found=false
while IFS= read -r line; do
  if [[ "$line" =~ ^[[:space:]]*links:[[:space:]]*$ ]]; then
    links_found=true
  fi

  if [[ "$links_found" == true && "$line" =~ endpoints: ]]; then
    endpoint1=$(echo "$line" | sed -E 's/.*\["([^":]+):([^,]+)", "([^":]+):([^,]+)".*/\1/')
    interface1=$(echo "$line" | sed -E 's/.*\["([^":]+):([^,]+)", "([^":]+):([^,]+)".*/\2/')
    endpoint2=$(echo "$line" | sed -E 's/.*\["([^":]+):([^,]+)", "([^":]+):([^,]+)".*/\3/')
    interface2=$(echo "$line" | sed -E 's/.*\["([^":]+):([^,]+)", "([^":]+):([^,]+)".*/\4/')
    
    if [[ "$endpoint1" == "$target" ]]; then
      used_interfaces+=("$interface1")
    elif [[ "$endpoint2" == "$target" ]]; then
      used_interfaces+=("$interface2")
    fi
  fi

done < "$topology_file"

eth_target=""
for eth in eth1 eth2 eth3 eth4 eth5 eth6 eth7 eth8; do
  if [[ ! " ${used_interfaces[@]} " =~ " ${eth} " ]]; then
    eth_target=$eth
    break
  fi
done

if [[ -z "$eth_target" ]]; then
  echo "Errore: nessuna interfaccia disponibile per il nodo target!"
  exit 1
fi

echo $eth_target

echo "    - endpoints: [\"$target:$eth_target\", \"host:veth-host\"]" >> "$topology_file"

netmask_decimal=$(cidr_to_netmask $mask)
netmask_flipped=$(cidr_to_netmask_flipped $mask)

echo -e "Inserisci l'indirizzo IP dell'intera rete emulata e la relativa maschera:"
read -p "IP: " net_ip
read -p "Mask: " net_mask

echo -e "\n! ospf-mgmt-app !\n!" >> "$startup_config_file"
echo "int $eth_target" >> "$startup_config_file"
echo "no switchport" >> "$startup_config_file"
echo "ip addr $gateway_ip $netmask_decimal" >> "$startup_config_file"
echo "no shutdown" >> "$startup_config_file"
echo "router ospf 1" >> "$startup_config_file"
echo "network $ip $netmask_flipped area 0" >> "$startup_config_file"
echo "!" >> "$startup_config_file"

echo "Deploying topology from: test/$test/topology.clab.yaml"
sudo containerlab deploy -t "test/$test/topology.clab.yaml"

sudo ip addr add "$my_ip"/"$mask" dev veth-host
sudo ip route add "$net_ip"/"$net_mask" via "$gateway_ip"

sleep 60

source venv/bin/activate
python3 src/main.py "$gateway_ip"
deactivate

sudo ip route remove "$net_ip"/"$net_mask" via "$gateway_ip"
sudo ip addr remove "$my_ip"/"$mask" dev veth-host

sudo containerlab destroy -t "test/$test/topology.clab.yaml"

sed -i '$d' "test/$test/topology.clab.yaml"
sed -i '/! ospf-mgmt-app !/,$d' "$startup_config_file"

echo "Test completato e pulizia eseguita."
