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

archivo="$1"	#Descarte todo, solo me queda el archivo lo guardo

#Archivo ingresado igual a vacio como tu alma :P
if [ -z "$archivo" ];then
        echo "Error, no ingreso ningun archivo o " >&2
        exit 4
fi
#El archivo no es un archivo.. si pasa este exit tambien existe
if ! [ -f "$archivo" ];then
        echo que poenes gil? Esto no es un archivo, son papas, cocinalas estan re duras
        exit 5
fi
#Esta bien el archivo??
#La esctructura del archivo es incorrecta testeando
cont=0
contusu=0
for linea in $(cat $archivo);do
        cont=$((cont+1)) #Doble parentesis para que haga una suma posta y no strings turbios
        if ! [[ "$linea" =~ ^[a-z_][a-z0-9_-]*:[^:].*:+/.*:(SI|NO):/bin/.*$ ]];then
		#Quedo largo pero esto verifica correctamente toda la linea completa y verifica
		#que el campo usuario no este vacio
                #https://unix.stackexchange.com/questions/287077/why-cant-linux-usernames-begin-with-numbers
                #Aca comenta que se puede crear usuarios con numeros pero no es recomendable así que..
                #Aunque en RedHat si lo admite
                #https://access.redhat.com/solutions/3103631
		#Aca no hacemos eso $meme
                errorfatal="true" #Esto nos manda al mensaje de "ATENCION no se creo"
        fi
	gsh="$(echo $linea | cut -d":" -f5)" #| cut -d:"/" -f3)" #Esta variable nos servira para mas adelante como tu hermana
        Vsh="$(find /usr/bin -maxdepth 1 -wholename "/usr$gsh")" #Busca que el shell exista
	if [ -z "$Vsh" ];then #Si no encuentra la shell
		#echo La shell de la linea $cont no es correcta
		errorfatal="true"
	fi
	#----------------------------------------------
	usuario=$(echo "$linea" | cut -d":" -f1)
	
	comentario="$(echo "$linea" | cut -d":" -f2)" 2> /dev/null #Si el comentario esta vacio que el cut no moleste
	home=$(echo "$linea" | cut -d":" -f3)
	crear=$(echo "$linea" | cut -d":" -f4)
	#----------------------------------------------
	if [[ "$crear" = "SI" ]];then #Los parentesis rectos dobles son la posta, evaluan mejor
        	creard=" -m"
        else
                creard=" -M" #Con control previo en el Regex que recibe NO espesificamente
        fi
	#if [ -z "$usuario" ];then #Esto ya lo controlo en el Regex
	#---------------Variables de testeo---------
	echo $usuario
	echo $comentario
	echo $creard
	echo $home
	echo $gsh
	#-------------------PENDIENTES------------------------
	#Hacer dos versiones del useradd una con esto que esta debajo y otra con las opciones por defecto
	#Si esta con las opciones por defecto que hay que separar con su parametro "-"
	#tambien hay que cambiar la linea del Regex ya que no aceptaria la bash vacia para que deje por defecto
	#revisar si el Regex filtra algo más
	useradd $creard -d $home -c "$comentario" -s "$shell" $usuario #2> /dev/null

	if [[ "$desplegar" = "1" ]];then
		usuariocreado=$(cat /etc/passwd | cut -d":" -f1 | grep $usuario)
		if [ -z "$usuario"  ];then
			errorfatal="true"
		else
			echo Usuario $usuario creado con éxito con datos indicados:
			echo "	Comentario: $comentario"
			echo "	Dir home: $home"
			echo "	Asegurado existencia de directorio home: $crear"
			echo "	Shell por defecto: $gsh"
			#----------------PENDIENTES 2-------------------------------
			#Estas variables si estan por defecto tienen que venir con el valor que dice la letra
			#La idea es que si estan por defecto "vacias" que directamente le agregue a todas el
			#valor
		fi
		if [[ "$errorfatal" = "true"]];then
			echo ATENCION: el usuario $usuario de la linea $cont no pudo ser creado
		fi
	errorfatal="falso" #Seteo la variable preparandola para el siguente recorrido
	fi
done #Fin del for de recorrida de linea a linea
