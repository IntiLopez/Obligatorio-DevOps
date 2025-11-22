#!/bin/bash

#Definimos las variables a utilizar, sabemos que estan aca
desplegar=0	#Siempre es bueno saber donde estan estas variables
contra=""	
IFS="
" #Sin esto los espacios en el cat del for se los re come, como tu hermana se la re come, aclaro

if [ $# -gt 4 ];then
	echo Solo se admiten 4 parametros -i -c seguido de la contraseña y el archivo
	exit 6 #Esto hay que ordenarlo, por experiencia al final
fi
#Menos de dos paramentros aca no che
if [ $# -lt 2 ];then
	echo Falta gente en el cuadro
	echo Como minimo se admite el archivo como parametro
	exit 7
fi
#Archivo ingresado igual a vacio como tu alma :P
if [ -z "$archivo" ];then
        echo "Error, no ingreso ningun archivo o " >&2
        exit 4

fi
#El archivo no es un archivo.. si pasa esto tambien existe
if ! [ -f "$archivo" ];then
        echo que poenes gil? Esto no es un archivo, son papas, cocinalas estan re duras
        exit 5
fi
#Esta bien el archivo??
#La esctructura del archivo es incorrecta

	if [[  $(grep "^[0-9a-z]*") ]] 
		#https://unix.stackexchange.com/questions/287077/why-cant-linux-usernames-begin-with-numbers
		#Aca comenta que se puede crear usuarios con numeros pero no es recomendable así que..
	
	
		Vshell=$(find /usr/bin -maxdepth 1 -name "znew" | cut -d"/" -f4) #Busca que el shell exista

#Creamos un while para recorrer los parametros
while [ $# -gt 1 ];do	#Recorremos los parametros
	case "$1" in	
		-i) 	#COMENTAR
			desplegar=1
			shift
			;;
		-c)	#COMENTAR
			if [ -z "$2" ]; then
				echo "Error, Falta agregar la contraseña luego del parametro" >&2
				exit 2
			fi
			contra="-p $2"	#Guardo el -p y la contraseña para tirar la variable entera al useradd
			shift 2
			;;
		-*)	#COMENTAR
			echo "Error, el parametro $1 no es valido" >&2
			exit 3
			;;
	esac
done

archivo="$1"	#Descarte todo, solo me queda el archivo

#Probamos que funciona la lectura de los inputs con banderas
#echo "Opcion -i = $desplegar"
#echo "Contraseña = $contra"
#echo "Archivo = $archivo"

#while IFS= read i; do	#En cada iteracion del while lee linea por liena y lo guarda en la variable i evitando con IFS que corte por los espacios
for i in $(cat $archivo); do
	

	#Evaluar por aca cada linea del archivo por aca con un grep evaluando los campos
	usuario=$(echo "$i" | cut -d":" -f1)
	comentario=" -c $(echo "$i" | cut -d":" -f2) "
	home=$(echo "$i" | cut -d":" -f3)
	crear=$(echo "$i" | cut -d":" -f4) 
	#si dice "SI" directamente me coloque el -m que es crear el directorio HOME en useradd
	echo $i
	if ( "$crear" = "SI" );then
		crear=" -m"
	else 
		crear=" -M" #Con control previo si este campo recibe NO
	fi
	shell=$(echo "$i" | cut -d":" -f5)
#Probamos que funciona la lectura de los inputs con banderas
#echo "Opcion -i = $desplegar"
#echo "Contraseña = $contra"
#echo "Archivo = $archivo"
	
	if [ -z "$usuario" ]; then #La comprobacion del usuario tiene que estar antes y avisar al usuario que esta mal esto lo podemos hacer con un grep al archivo linea a linea o en este mismo antes de guardar las variables
		echo "Error, el usuario esta vacio"
		exit 5
	fi
	
	#La idea es que si llega hasta aca es que los controles ya estan hechos, sino que devuela errores
	#si el campo esta vacio habrìa que llenarlo con algo para 
#	useradd$crear $usuario $comentario $home $shell 2> /dev/null  
	#Probar que pasa si queda algo vacio, lo crea por defecto? o error?

	#Si esta el -i levantado utilizo la variable desplegar=1 para buscar el nombre en /etc/passwd, evaluar si ya fue creado o no y que hacer aca
done	
#done < "$archivo" #Del while



