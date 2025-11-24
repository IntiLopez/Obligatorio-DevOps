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
			contra="$2"	#Guardo el -p y la contraseña para tirar la variable entera al useradd
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
#Permiso de lectura sobre el archivo?
if ! [ -r "$archivo" ];then
	echo No tiene permisos de lectura sobre el archivo
	exit 6
fi
cont=0
#reviso el archivo linea a linea si es correcto
for linea in $(cat $archivo);do
	 cont=$((cont+1))
	if ! [[ "$linea" =~ ^[a-z_][a-z0-9_-]*:[^:]*:.*:(SI|NO):.*$ ]];then
		#Campo usuario no vacio y que se respeten los
                 #https://unix.stackexchange.com/questions/287077/why-cant-linux-usernames-begin-with-numbers
                 #Aca comenta que se puede crear usuarios con numeros pero no es recomendable así que..
                 #Aunque en RedHat si lo admite
                 #https://access.redhat.com/solutions/3103631

		echo Estructura del archivo incorrecta, revise la linea $cont
		exit 7
	fi
done
#-----------------------------RECORRIDO PRINCIPAL---------------------
cont=0
errorfatal="false"
for linea in $(cat $archivo);do
        cont=$((cont+1)) #Doble parentesis para que haga una suma posta y no strings turbios
	gsh="$(echo $linea | cut -d":" -f5)" #| cut -d:"/" -f3)" #Esta variable nos servira para mas adelante
        #Vsh="$(find /usr/bin -maxdepth 1 -wholename "/usr$gsh")" #Busca que el shell exista
	#if [ -z "$Vsh" ];then #Si no encuentra la shell
		#echo La shell de la linea $cont no es correcta
	#	errorfatal="true"
	#fi Si va el verificador del shell se deja si no no
	#--------------------------------------------------------
	usuario=$(echo "$linea" | cut -d":" -f1)
	comentario="$(echo "$linea" | cut -d":" -f2)" 2> /dev/null #Si el comentario esta vacio que el cut no moleste
	home=$(echo "$linea" | cut -d":" -f3)
	crear=$(echo "$linea" | cut -d":" -f4)
	#---------------------------------------------------------
	if [[ "$crear" = "SI" ]];then #Los parentesis rectos dobles son la posta, evaluan mejor
        	creard="-m"
        else
                creard="-M" #Con control previo en el Regex que recibe NO espesificamente
        fi
	#----------------------CAMPOS POR DEFECTO---------------------------------------
	usuariocreado=$(cat /etc/passwd | cut -d":" -f1 | grep "^$usuario$") #Ese grep busca una linea vacia si esta vacio
	if [ -n "$usuariocreado" ];then
		errorfatal="true"
	else
		armocomand=() #Creo que sin un array esto es imposible, lo intente
		if [ -n "$comentario" ];then #Si no esta vacio agrega al array, igual con los demas
			armocomand+=(-c "$comentario")
		fi
		if [  -n "$home" ] && [[ "$crear" = "SI" ]];then
			armocomand+=(-d "$home")  
		fi
		if [ -n "$gsh" ];then
			armocomand+=(-s "$gsh") 
		fi
		if [ ${#armocomand[@]} -eq 0 ];then #comparo si la longitud del array es 0, en vez del -z "", 3 horas con esto
			useradd $creard "$usuario" 2> /dev/null
			#echo "useradd $creard $usuario" #TEST
		else
			useradd "${armocomand[@]}" $creard "$usuario" 2> /dev/null 
		        #echo "useradd ${armocomand[@]} $creard $usuario" #TEST	
		fi
		if ! [ -z "$contra" ];then
	                echo $usuario:$contra | sudo chpasswd 2> /dev/null
                fi
	fi
	#-------------------------------------------------------------
	if [[ "$desplegar" = "1" ]];then #Despegar es el -i para mostrar informacion
		usuariocreado=$(cat /etc/passwd | cut -d":" -f1 | grep "^$usuario$")
		if [ -z "$usuariocreado"  ];then
			errorfatal="true"
		else
			if [[ "$errorfatal" = "false" ]];then
				echo Usuario $usuario creado con éxito con datos indicados:
				echo "	Comentario: $comentario"
				echo "	Dir home: $home"
				echo "	Asegurado existencia de directorio home: $crear"
				echo "	Shell por defecto: $gsh"
				echo corresponde a la linea $cont
			else
				echo ATENCION: el usuario $usuario de la linea $cont no pudo ser creado
			fi
		fi
		#Este if reamlente esta bien?
	fi #Aca termina el -i que despliega informaciontrucho

	#Reseteo de variables por ciclo
	errorfatal="false" #Seteo la variable preparandola para el siguente recorrido
	usuariocreado=""
done #Fin del for de recorrida de linea a linea
#---------------------------------COMENTARIOS----------------------------------
#Links de paginas que me ayudar con el array
#https://atareao.es/tutorial/scripts-en-bash/arrays-en-bash
#https://www.hostinger.com/tutorials/how-to-use-bash-array
