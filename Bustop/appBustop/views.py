from django.http import HttpResponse
from django.template import Template, Context
from django.template.loader import get_template
from django.shortcuts import render
from django.shortcuts import redirect

#importar lo del email
from django.conf import settings
from django.core.mail import send_mail

#librería fecha
from datetime import datetime
        
#libreria pdf
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, Table, TableStyle, Image
from reportlab.lib.enums import TA_CENTER
from reportlab.lib import colors
from reportlab.lib.utils import ImageReader

#librería para busquedas en base de datos.
from django.contrib.postgres.search import SearchQuery, SearchVector

#importar modelos
from appBustop.models import Usuarios, Rutas, QuejasUsuarios, Admin, Concesionario, rutasAgregadas, ConcAgregados, rutasBuscadas

#LOGIN


def login(request):

   #si hay una sesion iniciada...
   if "sesion" in request.session:
      return redirect('/principalUsuario/')
   
   elif "admin" in request.session:
      return redirect('/principalAdmin/')
   
   elif "conce" in request.session:
      return redirect('/principalCons/')
   
   else:
      if request.method == "POST":
         
         nombreusuario = request.POST['nombreusuario']
         contra = request.POST['contrausuario']

         datospersona = Usuarios.objects.filter(usuario__icontains=nombreusuario)

         administradores = Admin.objects.filter(
             nombre_admin__icontains=nombreusuario)

         concesionarios = Concesionario.objects.filter(
             conce__icontains=nombreusuario)

         #Si encuentra a una persona con ese usuario
         if datospersona :

            for dato in datospersona:
               contrareal = dato.contrasena
               nombre = dato.nombre
               apellido = dato.apellido
               localidad = dato.localidad
               correo = dato.correo
               nacimiento = dato.nacimiento
            
            #Si ingresa bien su usuario y contraseña
            if contra == contrareal:

               usuarioNormalLoguqado = True

               request.session['sesion'] = nombreusuario
               request.session['nombre'] = nombre
               request.session['apellido'] = apellido
               return redirect('/principalUsuario/')

            #Contraseña esta mal  
            else:
               bandera = True
               bandera2 = True
               error = "Ha ingresado mal la contraseña."
               return render(request, "Principal/login.html", {"bandera": bandera, "bandera2": bandera2, "error": error, "nombreusuario": nombreusuario})
               # return HttpResponse(mensaje)

         #si se encuentra en administradores.
         elif administradores:

            for dato in administradores:
               contrareal = dato.contrasena
               correo = dato.correo

            #Si ingresa bien su usuario y contraseña
            if contra == contrareal:

               request.session['admin'] = nombreusuario
               return redirect('/principalAdmin/')

            #Contraseña esta mal
            else:
               bandera = True
               bandera2 = True
               error = "Ha ingresado mal la contraseña."
               return render(request, "Principal/login.html", {"bandera": bandera, "bandera2": bandera2, "error": error, "nombreusuario": nombreusuario})
               # return HttpResponse(mensaje)

         elif concesionarios:

            for dato in concesionarios:
               contrareal = dato.contrasena
               nombre = dato.nombre_conce
               rutaencargado = dato.nombre_ruta
               correo = dato.correo

            #Si ingresa bien su usuario y contraseña
            if contra == contrareal:

               request.session['conce'] = nombreusuario
               request.session['nombreconce'] = nombre
               return redirect('/principalCons/')

            #Contraseña esta mal
            else:
               bandera = True
               bandera2 = True
               error = "Ha ingresado mal la contraseña."
               return render(request, "Principal/login.html", {"bandera": bandera, "bandera2": bandera2, "error": error, "nombreusuario": nombreusuario})
               # return HttpResponse(mensaje)

         #si no se encuentra a alguien con ese usuario..
         else:
            bandera = True
            error = "No se ha encontrado a nadie con ese usuario."
            return render(request, "Principal/login.html", {"bandera": bandera, "error": error})
            # mensaje = "No se encontro alguien con ese usuario xd"
            # return HttpResponse(mensaje)


      return render(request, "Principal/login.html")

def salir(request):
   del request.session["sesion"]
   del request.session['nombre']
   del request.session['apellido'] 

   return redirect('/login/')


def salirAdmin(request):
   del request.session["admin"]

   return redirect('/login/')


def salirCons(request):
   del request.session["conce"]
   del request.session['nombreconce']

   return redirect('/login/')

def registro(request):

   if request.method == "POST":
      
      nombreusuario = request.POST['nombreusuario']
      nombre = request.POST['nombre']
      apellido = request.POST['apellido']
      contra = request.POST['contra']
      cc = request.POST['contraconfirmada']
      localidad = request.POST['localidad']
      correo = request.POST['correo']
      nacimiento = request.POST['nacimiento']

      usuariosregistrados = Usuarios.objects.all()

      for u in usuariosregistrados:
         #si el nombre ingresado es igual a un usuario ya registrado...

         if nombreusuario == u.usuario:
            error = "Ya hay un usuario registrado con ese nombre."
            hayerror = True
            return render(request, "Principal/registro.html", {"bandera": hayerror, "textoerror": error, "nombreusuario": nombreusuario, "nombre": nombre, "apellido": apellido, "contra": contra, "cc": cc, "localidad": localidad, "correo": correo, "nacimiento": nacimiento})

      textoerror = ""
      error = False
      error2 = False
      error3 = False
      error4 = False

      if contra == cc:
         error = False

      else:
         error = True
         textoerror += " Las contraseñas no coinciden. "

      if localidad == "l":
         error2 = True
         textoerror += " Selecciona una localidad. "
      else:
         error2 = False

      if nacimiento == "":
         error3 = True
         textoerror += " Falta ingresar la fecha de nacimiento. "
      else:
         error3 = False

      if correo == "":
         error4 = True
         textoerror += " Falta ingresar el correo electrónico. "
      
      else:
         error4 = False

      #si hay un error
      if error == True or error2 == True or error3 == True or error4 == True:
         hayerror = True
         return render(request, "Principal/registro.html", {"bandera": hayerror, "textoerror": textoerror, "nombreusuario": nombreusuario, "nombre": nombre, "apellido":apellido, "contra":contra, "cc":cc, "localidad":localidad, "correo":correo, "nacimiento":nacimiento})

            #return HttpResponse(textoerror)
      #si no hay errores
      elif error == False:
         hayerror = False

         registro = Usuarios(usuario=nombreusuario, nombre=nombre, apellido = apellido, contrasena = contra, localidad = localidad, correo = correo, nacimiento = nacimiento)
         registro.save()
         return render(request, "Principal/registro.html", {"bandera": hayerror})
            #datos = nombreusuario , " " , nombre , " " , apellido , " " , contra , " " , cc , " " , localidad , " " , correo , " " , nacimiento
            #return HttpResponse(datos)
      
   
   return render(request, "Principal/registro.html")



def olvido(request):

   #si se da clic en el boton..
   if request.method == "POST":

      nombreusuario = request.POST['nombreusuario']

      datospersona = Usuarios.objects.filter(usuario__icontains=nombreusuario)
      datospersona2 = Usuarios.objects.filter(correo__icontains=nombreusuario)

      if datospersona:

         for dato in datospersona:
            nombre = dato.nombre
            apellido = dato.apellido
            correo = dato.correo
            contraseña = dato.contrasena
         
         email_remitente = settings.EMAIL_HOST_USER
         email_destino = [correo]
         
         asunto = "Recuperación de contraseña - Bustop"
         mensaje = "Hola "+ nombre+ " "+ apellido+ "!. Creemos que olvidaste tu contraseña :(. Tu contraseña es: "+ contraseña+ "."

         send_mail(asunto, mensaje, email_remitente, email_destino)

         return render(request, "Principal/olvidoContra.html", {"datospersona":datospersona,"busqueda":nombreusuario, "nombre":nombre, "apellido":apellido})
      
      elif datospersona2:

         for dato in datospersona2:
            nombre = dato.nombre
            apellido = dato.apellido
            correo = dato.correo
            contraseña = dato.contrasena

         email_remitente = settings.EMAIL_HOST_USER
         email_destino = [correo]

         asunto = "Recuperación de contraseña - Bustop"
         mensaje = "Hola " + nombre + " " + apellido + \
             "!. Creemos que olvidaste tu contraseña :(. Tu contraseña es: " + \
             contraseña + "."

         send_mail(asunto, mensaje, email_remitente, email_destino)

         return render(request, "Principal/olvidoContra.html", {"datospersona": datospersona2, "busqueda": nombreusuario, "nombre": nombre, "apellido": apellido})

      else:
         error = "No se encontro el usuario."
         bandera = True
         return render(request, "Principal/olvidoContra.html", {"error": error, "bandera": bandera})
      #return HttpResponse(datospersona)

   
   return render(request, "Principal/olvidoContra.html")

#USUARIOS PRINCIPAL


def principalUsuario(request):

   principal = True

   return render(request, "Usuarios/bienUsuario.html", {"nombreusuario": request.session['sesion'], "nombre": request.session['nombre'], "apellido": request.session['apellido'], "principal":principal})

   

#BUSCAR RUTA


def buscarRuta(request):
   buscarin = True
   #cuando el usuario de clic en buscar..
   if request.method == "POST":

      busqueda = request.POST['busqueda']
      buscarin = True


      #Si funciona pero con la búsqueda exacta
      busquedaRutas = Rutas.objects.annotate(
          search=SearchVector('nombre_ruta', 'color', 'localidad')
      ).filter(search=SearchQuery(busqueda))
      #busquedaRutas = Rutas.objects.annotate(search=SearchVector('nombre_ruta', 'localidad', 'color'),).filter(search=busqueda)

      #si encuentra algo relacionado con esa búsqueda..
      if busquedaRutas:
         encontro = True
         return render(request, "Usuarios/bRutaUsuario.html", {"nombreusuario": request.session['sesion'], "nombre": request.session['nombre'], "apellido": request.session['apellido'], "busquedaRutas":busquedaRutas, "encontro":encontro, "busqueda":busqueda, "buscarin":buscarin})
      
      #si no hay resultados..
      noencontro = True
      return render(request, "Usuarios/bRutaUsuario.html", {"nombreusuario": request.session['sesion'], "nombre": request.session['nombre'], "apellido": request.session['apellido'], "noencontro": noencontro, "busqueda": busqueda, "buscarin": buscarin})

   return render(request, "Usuarios/bRutaUsuario.html", {"nombreusuario": request.session['sesion'], "nombre": request.session['nombre'], "apellido": request.session['apellido'], "buscarin": buscarin})

def infoRuta(request):

   #se obtiene el nombre de la ruta de la cual el usuario quiere info 
   nombreRuta = request.POST['nomreRuta']

   rutaBuscada = rutasBuscadas(usuario=request.session['sesion'], nombre_ruta = nombreRuta)
   rutaBuscada.save()

   infoRuta = Rutas.objects.filter(nombre_ruta__icontains=nombreRuta)

   for x in infoRuta:
      localidad = x.localidad
      ncamiones = x.ncamiones
      color = x.color
      tiempo = x.tiempo
      imagen = x.imagen
      iframe = x.iframe

   return render(request, "Usuarios/infoRuta.html", {"nombreusuario": request.session['sesion'], "nombre": request.session['nombre'], "apellido": request.session['apellido'] , "nombreRuta":nombreRuta, "localidad":localidad, "ncamiones":ncamiones, "color":color, "tiempo":tiempo, "imagen":imagen, "iframe":iframe})

#BUSCAR RUTA POS UBICACIÓN.


def ubicacionRuta(request):
   
   #Si busca una ruta con la ubicación.
   if request.method == "POST":
      ubicacion = request.POST['search']

      if (ubicacion == ""):
         buscarubi = True
         buscarnada = True

         coordenadax = '25.5852172'
         coordenaday = '-103.5620931'
         return render(request, "Usuarios/ubiUsuario.html", {"nombreusuario": request.session['sesion'], "nombre": request.session['nombre'], "apellido": request.session['apellido'], "buscarubi": buscarubi, "busqueda":ubicacion, "buscarnada":buscarnada, "cx":coordenadax, "cy":coordenaday})

      cinemiguelaleman = 'Cinemex, Boulevard Miguel Alemán, Flores Magón, Gómez Palacio, Durango, México'
      cinehamburgo = 'Cinemex Hamburgo, Francisco Villa, Rinconadas Hamburgo, Gómez Palacio, Durango, México'
      cinesanantonio = 'Cinépolis San Antonio, Gómez Palacio, Durango, México'

      sorianatrc = 'Soriana Híper Hidalgo, Avenida Hidalgo, Primitivo Centro, Torreón, Coahuila de Zaragoza, México'
      sorianacenetnario = 'Soriana Híper Centenario, Boulevard Miguel Alemán, Flores Magón, Gómez Palacio, Durango, México'
      sorianagomez = 'Soriana Centro Gomez Palacio Durango, Zona Centro, Gómez Palacio, Durango, México'
      sorianatec = 'Mercado Soriana - Lerdo, Filiberto García Monreal, Lerdo, Durango, México'
      sorianarosas = 'Citibanamex Soriana Las Rosas, Boulevard Miguel Alemán, Las Rosas, Gómez Palacio, Durango, México'
      sorianahamburgo = 'Soriana Híper - Hamburgo, Hamburgo, Gómez Palacio, Durango, México'

      imsschapala = 'IMSS Hospital General de Zona Número 51, Fidel Velásquez, Fidel Velázquez, Gómez Palacio, Durango, México'
      imsslasrosas = 'IMSS Unidad de Medicina Familiar/UMAA 53, Centro, Zona Centro, Gómez Palacio, Durango, México'

      abastosgomez = 'Central de Abastos, Gómez Palacio, Durango, México'

      mercadogomez = 'Mercado José Ramón Valdez, Calle Escobedo, Zona Centro, Gómez Palacio, Durango, México'
      mercadotrc = 'Mercado Juárez, Ejido Ana, Torreón, Coahuila de Zaragoza, México'

      plazagomez = 'Plaza de armas Gómez Palacio, Independencia, Zona Centro, Gómez Palacio, Durango, México'

      itsl = 'Instituto Tecnológico Superior de Lerdo, Placido Domingo, Ciudad Lerdo, Durango, México'

      #cines
      if (ubicacion == cinemiguelaleman):
         coordenadax = '25.5493075'
         coordenaday = '-103.4805941'

      elif(ubicacion == cinehamburgo): 
         coordenadax = '25.596881'
         coordenaday = '-103.4999307'
          
      elif(ubicacion == cinesanantonio):
         coordenadax = '25.5940292'
         coordenaday = '-103.4864311'
      
      #sorianas
      elif(ubicacion == sorianatrc):
         coordenadax = '25.5366364'
         coordenaday = '-103.4671171'

      elif(ubicacion == sorianacenetnario):
         coordenadax = '25.549727'
         coordenaday = '-103.4827496'
      
      elif(ubicacion == sorianagomez):
         coordenadax = '25.5616237'
         coordenaday = '-103.4971249'
      
      elif(ubicacion == sorianatec):
         coordenadax = '25.5423325'
         coordenaday = '-103.5352865'
      
      elif(ubicacion == sorianarosas):
         coordenadax = '25.5548161'
         coordenaday = '-103.5062044'
      
      elif(ubicacion == sorianahamburgo):
         coordenadax = '25.5939048'
         coordenaday = '-103.505694'
            
      #seguros
      elif(ubicacion == imsschapala):
         coordenadax = '25.5702524'
         coordenaday = '-103.5242721'
      
      elif(ubicacion == imsslasrosas):
         coordenadax = '25.5558524'
         coordenaday = '-103.5086422'

      #abastos y mercados
      elif(ubicacion == abastosgomez):
         coordenadax = '25.5681447'
         coordenaday = '-103.4824618'

      elif(ubicacion == mercadogomez):
         coordenadax = '25.5664645'
         coordenaday = '-103.5265615'
      
      elif(ubicacion == mercadotrc):
         coordenadax = '25.5376991'
         coordenaday = '-103.461774'

      #tec
      elif(ubicacion == itsl):
         coordenadax = '25.5480051'
         coordenaday = '-103.5454651'

      else:
         buscarubi = True
         busquedano = True
         coordenadax = '25.5852172'
         coordenaday = '-103.5620931'
         return render(request, "Usuarios/ubiUsuario.html", {"nombreusuario": request.session['sesion'], "nombre": request.session['nombre'], "apellido": request.session['apellido'], "buscarubi": buscarubi, "busqueda":ubicacion, "busquedano":busquedano, "cx":coordenadax, "cy":coordenaday})


      #si ninguna busqueda coincide..

      cines = ['25.5493075-103.4805941', '25.596881-103.4999307', '25.5940292-103.4864311']
      sorianas = ['25.5366364-103.4671171', '25.549727-103.4827496', '25.5616237-103.4971249', '25.5423325-103.5352865', '25.5548161-103.5062044', '25.5939048-103.505694']
      seguros = ['25.5702524-103.5242721', '25.5558524-103.5086422']
      mercadosabastos = ['25.5681447-103.4824618', '25.5664645-103.5265615', '25.5376991-103.461774']
      tec = ['25.5480051-103.5454651']

      sitiosHamburgo = [cines[0], cines[1], cines[2], sorianas[0], sorianas[1], sorianas[5], mercadosabastos[0], mercadosabastos[2]]

      sitiosNucleo = [cines[0], sorianas[0], sorianas[1], mercadosabastos[0], mercadosabastos[2]]

      sitiosChilchota = [cines[1], cines[2], sorianas[3], seguros[0], seguros[1], tec[0]]

      sitiosParque = [sorianas[2], sorianas[4], seguros[1], mercadosabastos[0], mercadosabastos[1]]

      sitiosSanAntonio = [cines[1], cines[2], sorianas[2], sorianas[5], mercadosabastos[1]]

      coordenadacompleta = coordenadax+coordenaday;

      rutas = []

      for x in sitiosHamburgo:
         if(coordenadacompleta == x):
            rutas.extend(['Hamburgo'])

      for y in sitiosChilchota:
         if(coordenadacompleta == y):
            rutas.extend(['Chilchota'])

      for p in sitiosNucleo:
         if(coordenadacompleta == p):
            rutas.extend(['Nucleo'])
      
      for o in sitiosParque:
         if(coordenadacompleta == o):
            rutas.extend(['Parque Hundido Abastos'])

      for q in sitiosSanAntonio:
         if(coordenadacompleta == q):
            rutas.extend(['San Antonio'])


      rutas2 = []

      for n in rutas:
         infoRuta = Rutas.objects.filter(nombre_ruta__icontains=n)

         for t in infoRuta:
            localidad = t.localidad
            ncamiones = t.ncamiones
            color = t.color
            tiempo = t.tiempo
            imagen = t.imagen
            iframe = t.iframe

            rutas2.extend([(n, localidad, color, imagen, iframe, tiempo)])        


      buscarubi = True
      return render(request, "Usuarios/ubiUsuario.html", {"nombreusuario": request.session['sesion'], "nombre": request.session['nombre'], "apellido": request.session['apellido'], "buscarubi": buscarubi, "busqueda":ubicacion, "rutas":rutas2, "cx":coordenadax, "cy":coordenaday})


   buscarubi = True
   return render(request, "Usuarios/ubiUsuario.html", {"nombreusuario": request.session['sesion'], "nombre": request.session['nombre'], "apellido": request.session['apellido'], "buscarubi": buscarubi})

#MAPAS


def mapaRutaTorreon(request):

   rutasTorreon = Rutas.objects.filter(localidad__icontains="Torreon")

   return render(request, "Usuarios/Mapas/mapaTorreon.html", {"nombreusuario": request.session['sesion'], "nombre": request.session['nombre'], "apellido": request.session['apellido'], "rutasTorreon":rutasTorreon})


def mapaRutaGomez(request):

   rutasGomez = Rutas.objects.filter(localidad__icontains="Gomez Palacio")

   return render(request, "Usuarios/Mapas/mapaGomez.html", {"nombreusuario": request.session['sesion'], "nombre": request.session['nombre'], "apellido": request.session['apellido'], "rutasGomez": rutasGomez})


def mapaRutaLerdo(request):

   rutasLerdo = Rutas.objects.filter(localidad__icontains="Lerdo")

   return render(request, "Usuarios/Mapas/mapaLerdo.html", {"nombreusuario": request.session['sesion'], "nombre": request.session['nombre'], "apellido": request.session['apellido'], "rutasLerdo": rutasLerdo})

#QUEJAS Y SUGERENCIAS.


def quejaUsuario(request):

   quejita = True

   rutasGomez = Rutas.objects.filter(localidad="Gomez Palacio")
   rutasLerdo = Rutas.objects.filter(localidad="Lerdo")
   rutasTorreon = Rutas.objects.filter(localidad__icontains="Torreon")

   #si se da clic en el boton..
   if request.method == "POST":
      quejita = True
      ruta = request.POST['ruta']
      unidad = request.POST['unidad']
      texto = request.POST['texto']

      fecha = datetime.now()

      if ruta == "l":
         bandera=True
         return render(request, "Usuarios/quejaUsuario.html", {"nombreusuario": request.session['sesion'], "nombre": request.session['nombre'], "apellido": request.session['apellido'], "arregloTorreon": rutasTorreon, "arregloGomez": rutasGomez, "arregloLerdo": rutasLerdo, "bandera":bandera, "unidad":unidad, "texto2":texto, "quejita":quejita})

      #si esta todo bien
      registroQueja = QuejasUsuarios(usuario=request.session['sesion'], nombre_ruta=ruta, unidad=unidad, fecha=fecha, texto=texto)
      registroQueja.save()

      bandera2 = True
      
      return render(request, "Usuarios/quejaUsuario.html", {"nombreusuario": request.session['sesion'], "nombre": request.session['nombre'], "apellido": request.session['apellido'], "arregloTorreon": rutasTorreon, "arregloGomez": rutasGomez, "arregloLerdo": rutasLerdo, "bandera2": bandera2, "quejita": quejita})
   
   return render(request, "Usuarios/quejaUsuario.html", {"nombreusuario": request.session['sesion'], "nombre": request.session['nombre'], "apellido": request.session['apellido'], "arregloTorreon": rutasTorreon, "arregloGomez": rutasGomez, "arregloLerdo": rutasLerdo, "quejita": quejita})


#CONSESIONARIOS ----------------------------------------------------------------------------------------------
def principalCons(request):
   principal = True
   return render(request, "Consesionario/bienCons.html", {"nombreusuario": request.session['conce'], "nombre": request.session['nombreconce'], "principal": principal})


def infoCons(request):

   infu = True
   infoCon = Concesionario.objects.filter(conce=request.session['conce'])

   for i in infoCon:
      rutaEncargada = i.nombre_ruta

   infoRuta = Rutas.objects.filter(nombre_ruta = rutaEncargada)

   return render(request, "Consesionario/infoCons.html", {"nombreusuario": request.session['conce'], "nombre": request.session['nombreconce'], "infoRuta": infoRuta, "infu":infu})


def quejasCons(request):

   queco = True

   infoCon = Concesionario.objects.filter(conce=request.session['conce'])

   for i in infoCon:
      rutaEncargada = i.nombre_ruta

   quejas = QuejasUsuarios.objects.filter(nombre_ruta=rutaEncargada)

   contador = 0

   for i in quejas:
      contador += 1
   return render(request, "Consesionario/quejasCons.html", {"nombreusuario": request.session['conce'], "nombre": request.session['nombreconce'], "rutaEncargada": rutaEncargada, "contador": contador, "queco":queco})



def usuariosCons(request):

   usuco = True
   infoCon = Concesionario.objects.filter(conce=request.session['conce'])

   for i in infoCon:
      rutaEncargada = i.nombre_ruta
   
   imagen = Rutas.objects.filter(nombre_ruta=rutaEncargada)

   for x in imagen:
      img = x.imagen

   busquedas = rutasBuscadas.objects.filter(nombre_ruta=rutaEncargada)

   contador = 0

   for i in busquedas:
      contador += 1

   return render(request, "Consesionario/usuariosCons.html", {"nombreusuario": request.session['conce'], "nombre": request.session['nombreconce'], "rutaEncargada": rutaEncargada, "contador": contador, "usuco":usuco, "img":img})


#ADMINISTRADORES ----------------------------------------------------------------------------------------------
def principalAdmin(request):

   principal = True

   return render(request, "Administrador/bienAdmin.html", {"nombreusuario": request.session['admin'], "principal":principal})


def altaRuta(request):

   alru = True
   if request.method == "POST":

      alru = True
      nombreRuta = request.POST['nombreRuta']
      numeroCamiones = request.POST['numeroCamiones']
      localidad = request.POST['localidad']
      minutos = request.POST['minutos']
      imagen2 = request.FILES.get('imgruta')
      iframe = request.POST['iframeruta']

      color = ""

      todasRutas = Rutas.objects.all()

      for u in todasRutas:

         if nombreRuta == u.nombre_ruta:
            bandera = True
            error = "Ya existe esa ruta."
            return render(request, "Administrador/altaRuta.html", {"nombreusuario": request.session['admin'], "textoerror": error, "bandera": bandera, "nombreRuta": nombreRuta, "numeroCamiones": numeroCamiones, "localidad":localidad, "minutos":minutos, "alru":alru, "iframe":iframe})
      

      if localidad == "l":
         error = "No se ha escogido la localidad de la ruta."
         bandera = True
         return render(request, "Administrador/altaRuta.html", {"nombreusuario": request.session['admin'], "textoerror": error, "bandera": bandera, "nombreRuta": nombreRuta, "numeroCamiones": numeroCamiones, "localidad": localidad, "minutos": minutos, "alru": alru, "iframe":iframe})
      
      if minutos == "":
         error = "Tiempo aproximado no valido."
         bandera = True
         return render(request, "Administrador/altaRuta.html", {"nombreusuario": request.session['admin'], "textoerror": error, "bandera": bandera, "nombreRuta": nombreRuta, "numeroCamiones": numeroCamiones, "localidad": localidad, "minutos": minutos, "alru": alru, "iframe":iframe})
      
      if minutos != "":
         minutos2 = int(minutos)

         if minutos2 < 5:
            error = "Tiempo aproximado no valido."
            bandera = True
            return render(request, "Administrador/altaRuta.html", {"nombreusuario": request.session['admin'], "textoerror": error, "bandera": bandera, "nombreRuta": nombreRuta, "numeroCamiones": numeroCamiones, "localidad": localidad, "minutos": minutos, "alru": alru, "iframe":iframe})

      if localidad == "Torreon":
         color = "Verde"

      if localidad == "Gomez Palacio":
         color = "Azul"

      if localidad == "Lerdo":
         color = "Rojo"

      bandera2 = True
      registroRuta = Rutas(nombre_ruta=nombreRuta, localidad=localidad,
                           ncamiones=numeroCamiones, color=color, tiempo=minutos, imagen=imagen2, iframe=iframe)
      registroRuta.save()

      registroAdmin = rutasAgregadas(
          nombre_ruta=nombreRuta, nombre_admin=request.session['admin'])
      registroAdmin.save()

      return render(request, "Administrador/altaRuta.html", {"nombreusuario": request.session['admin'], "bandera2": bandera2, "alru": alru})

   return render(request, "Administrador/altaRuta.html", {"nombreusuario": request.session['admin'], "alru": alru})


def altaCons(request):

   alco = True
   rutas = Rutas.objects.all()

   if request.method == "POST":

      alco = True
      usuarioCons = request.POST['usuarioCons']
      contraCons = request.POST['contraCons']
      nombreCons = request.POST['nombreCons']
      rutaCons = request.POST['rutaCons']
      correoCons = request.POST['correoCons']

      todosCons = Concesionario.objects.all()

      for u in todosCons:

         if usuarioCons == u.conce:
            bandera = True
            error = "Ya existe ese consesionario."
            return render(request, "Administrador/altaCons.html", {"nombreusuario": request.session['admin'], "textoerror": error , "rutas": rutas ,"bandera": bandera, "usuarioCons": usuarioCons, "nombreCons": nombreCons, "rutaCons": rutaCons, "correoCons": correoCons, "alco":alco})

      #si no elige ruta
      if rutaCons == "l":

         bandera = True
         error = "Ingrese la ruta"
         return render(request, "Administrador/altaCons.html", {"nombreusuario": request.session['admin'], "textoerror": error, "rutas": rutas, "bandera": bandera, "usuarioCons": usuarioCons, "nombreCons": nombreCons, "rutaCons": rutaCons, "correoCons": correoCons, "alco": alco})

      if correoCons == "":
         bandera = True
         error = "NO ha ingresado el correo electrónico."
         return render(request, "Administrador/altaCons.html", {"nombreusuario": request.session['admin'], "textoerror": error, "rutas": rutas, "bandera": bandera, "usuarioCons": usuarioCons, "nombreCons": nombreCons, "rutaCons": rutaCons, "correoCons": correoCons, "alco": alco})


      registroCons = Concesionario(conce=usuarioCons, contrasena=contraCons, nombre_conce=nombreCons, nombre_ruta=rutaCons, correo=correoCons)
      registroCons.save()

      email_remitente = settings.EMAIL_HOST_USER
      email_destino = [correoCons]
         
      asunto = "Bienvenido a Bustop!"
      mensaje = "Hola "+ nombreCons+" !. Te damos la bienvenida a Bustop! Tu nombre de usuario es: "+ usuarioCons+ ". Tu contraseña es: " + contraCons + " ."

      send_mail(asunto, mensaje, email_remitente, email_destino)

      registroAdmin = ConcAgregados(
          conce=usuarioCons, nombre_admin=request.session['admin'])
      registroAdmin.save()

      bandera2 = True
      return render(request, "Administrador/altaCons.html", {"nombreusuario": request.session['admin'], "rutas": rutas, "bandera2": bandera2, "alco": alco})

   return render(request, "Administrador/altaCons.html", {"nombreusuario": request.session['admin'], "rutas": rutas, "alco": alco})

def bajaRuta(request):

   baru = True

   rutas = Rutas.objects.all()

   rutasAdmin = rutasAgregadas.objects.all()

   lista = zip(rutas,rutasAdmin)

   if request.method == "POST":

      baru = True

      rutaEliminar = request.POST['rutaEliminar']

      r = Rutas.objects.get(nombre_ruta = rutaEliminar)

      t = rutasAgregadas.objects.get(nombre_ruta=rutaEliminar)


      r.delete()
      t.delete()

      rutas = Rutas.objects.all()

      rutasAdmin = rutasAgregadas.objects.all()

      lista = zip(rutas, rutasAdmin)

      bandera = True

      return render(request, "Administrador/bajaRuta.html", {"nombreusuario": request.session['admin'], "rutas": rutas, "rutasAdmin": rutasAdmin, "lista": lista, "bandera": bandera, "baru":baru})

   return render(request, "Administrador/bajaRuta.html", {"nombreusuario": request.session['admin'], "rutas": rutas, "rutasAdmin": rutasAdmin, "lista": lista, "baru": baru})


def bajaCons(request):

   baco = True

   consecionarios = Concesionario.objects.all()

   consAdmin = ConcAgregados.objects.all()

   lista = zip(consecionarios, consAdmin)

   if request.method == "POST":

      baco = True

      consEliminar = request.POST['consEliminar']

      r = Concesionario.objects.get(conce=consEliminar)

      t = ConcAgregados.objects.get(conce=consEliminar)


      r.delete()
      t.delete()

      consecionarios = Concesionario.objects.all()

      consAdmin = ConcAgregados.objects.all()

      lista = zip(consecionarios, consAdmin)

      bandera = True

      return render(request, "Administrador/bajaCons.html", {"nombreusuario": request.session['admin'], "con": consecionarios, "consAdmin": consAdmin, "lista": lista, "bandera": bandera, "baco":baco})

   return render(request, "Administrador/bajaCons.html", {"nombreusuario": request.session['admin'], "lista": lista, "baco": baco})


#ACTUALIZAR DATOS ----------------------------------------------------------------------------------------------
def actUsuario(request):

   if request.method == "POST":

      actusuario = request.POST['actusuario']
      actapellido = request.POST['actapellido']
      actcontrasena = request.POST['actcontrasena']
      actlocalidad = request.POST['actlocalidad']
      actcorreo = request.POST['actcorreo']

      actualizacion = Usuarios.objects.filter(usuario__icontains=request.session['sesion']).update(nombre=actusuario, apellido=actapellido, contrasena=actcontrasena, localidad=actlocalidad, correo=actcorreo)

      actualizado = True
      
      #request.session['sesion'] = nombreusuario
      request.session['nombre'] = actusuario
      request.session['apellido'] = actapellido

      datospersona = Usuarios.objects.filter(usuario__icontains=request.session['sesion'])

      if datospersona:
         #se obtienen datos de la persona para mostrarlos en los camppos.
         for dato in datospersona:
            nombre = dato.nombre
            apellido = dato.apellido
            correo = dato.correo
            contraseña = dato.contrasena
            localidad = dato.localidad

      return render(request, "Actualizar/actUsuario.html", {"nombreusuario": request.session['sesion'], "nombre": request.session['nombre'], "apellido": request.session['apellido'], "nusuario": nombre, "ausuario": apellido, "lusuario": localidad, "cusuario": correo, "cc": correo, "contra": contraseña,  "bandera": actualizado})

   datospersona = Usuarios.objects.filter(usuario__icontains=request.session['sesion'])

   if datospersona:
      #se obtienen datos de la persona para mostrarlos en los camppos.
       for dato in datospersona:
           nombre = dato.nombre
           apellido = dato.apellido
           correo = dato.correo
           contraseña = dato.contrasena
           localidad = dato.localidad

   


   return render(request, "Actualizar/actUsuario.html", {"nombreusuario": request.session['sesion'], "nombre": request.session['nombre'], "apellido": request.session['apellido'], "nusuario": nombre, "ausuario":apellido, "lusuario":localidad, "cusuario": correo, "cc": correo, "contra": contraseña})


def actCons(request):

   if request.method == "POST":

      nombreCons = request.POST['nombreCons']
      rutaCons = request.POST['rutaCons']
      correoCons = request.POST['correoCons']

      actualizacion = Concesionario.objects.filter(conce=request.session['conce']).update(
          nombre_conce=nombreCons, nombre_ruta=rutaCons, correo=correoCons)

      actualizado = True
      request.session['nombreconce'] = nombreCons

      datosCons = Concesionario.objects.filter(
            conce__icontains=request.session['conce'])

      rutas = Rutas.objects.all()

      if datosCons:
         #se obtienen datos de la persona para mostrarlos en los camppos.
         for dato in datosCons:
            nombrec = dato.nombre_conce
            ruta = dato.nombre_ruta
            correo = dato.correo

      return render(request, "Actualizar/actCons.html", {"nombreusuario": request.session['conce'], "nombre": request.session['nombreconce'], "nombrec": nombrec, "rutac": ruta, "correo": correo, "rutas": rutas, "actualizado":actualizado})

   datosCons = Concesionario.objects.filter(
       conce__icontains=request.session['conce'])

   rutas = Rutas.objects.all()

   if datosCons:
      #se obtienen datos de la persona para mostrarlos en los camppos.
       for dato in datosCons:
            nombrec = dato.nombre_conce
            ruta = dato.nombre_ruta
            correo = dato.correo
   
   return render(request, "Actualizar/actCons.html", {"nombreusuario": request.session['conce'], "nombre": request.session['nombreconce'], "nombrec": nombrec, "rutac": ruta, "correo": correo, "rutas": rutas})


def usuariosAdmin(request):

   usuarios=True

   listaUsuarios = Usuarios.objects.all()

   return render(request, "Administrador/usuariosAdmin.html", {"nombreusuario": request.session['admin'], "usuarios": usuarios, "listaUsuarios": listaUsuarios, })


#Opens up page as PDF
def verPdf(request):

   #Sacar todos los datos del conc, su ruta y sus quejas
   datosCons = Concesionario.objects.filter(
       conce__icontains=request.session['conce'])

   for d in datosCons:
      nombre = d.nombre_conce
      rutaEncargada = d.nombre_ruta

   #Sacar datos de la ruta de la que esta encargado el concesionario
   infoRuta = Rutas.objects.filter(nombre_ruta__icontains=rutaEncargada)


   #Sacar todas las quejas de esa ruta
   quejasRuta = QuejasUsuarios.objects.filter(
       nombre_ruta__icontains=rutaEncargada)

   numQuejas = 0

   unidades = []
   
   for queja in quejasRuta:
      numQuejas += 1
      n = queja.unidad

      if numQuejas >= 2:
         if n in unidades:
            esta = True
         
         else:
            esta = False

         if esta == False:
            unidades.append(n)

      elif numQuejas == 1:
         unidades.append(n)

   cont = 0
   vecesQuejas = []

   for u in unidades:
      for o in quejasRuta:
         if o.unidad == u:
            cont += 1
      vecesQuejas.append(cont)
      cont = 0


   


   #pdf
   response = HttpResponse(content_type='application/pdf')
   response['Content-Disposition'] = 'attachment; filename= Reporte Quejas de Usuarios.pdf'

   buffer = BytesIO()
   c = canvas.Canvas(buffer, pagesize=letter)

   # HEADER
   color = "#F3B416"
   c.setFillColor(color)
   c.setFont('Helvetica', 22)
   c.drawString(270,740,'Bustop')

   color = "black"
   c.setFillColor(color)
   c.setFont('Helvetica', 12)
   c.drawString(230, 725, 'Te llevamos a donde quieras.')

   hoy = datetime.now()

   fecha = str(hoy.date())

   c.setFont('Helvetica-Bold', 12)
   c.drawString(480, 740, fecha)

   c.line(460,737,560,737)

   #TITULO
   color = "#0A7D91"
   c.setFillColor(color)
   c.setStrokeColor(color)
   c.setFont('Helvetica', 24)
   c.drawString(85, 680, 'REPORTE DE QUEJAS DE USUARIOS')

   #DATOS CONCESIONARIO
   color = "black"
   c.setFillColor(color)
   c.setFont('Helvetica', 20)
   c.drawString(200, 640, 'DATOS CONCESIONARIO.')

   c.setFont('Helvetica', 12)
   c.drawString(50, 610, 'Nombre del Concesionario:')
   color = "#91140A"
   c.setFillColor(color)
   c.drawString(210, 610, nombre)
   color = "black"
   c.setFillColor(color)
   c.line(200,605,310,605)

   color = "black"
   c.setFillColor(color)
   c.setFont('Helvetica', 12)
   c.drawString(340, 610, 'Ruta a cargo:')
   color = "#91140A"
   c.setFillColor(color)
   c.drawString(440, 610, rutaEncargada)
   color = "black"
   c.setFillColor(color)
   c.line(430, 605, 510, 605)


   #DATOS DE LA RUTA 
   c.setFont('Helvetica', 20)
   c.drawString(200, 565, 'INFORMACIÓN DE RUTA.')

   styles = getSampleStyleSheet()
   styleBH = styles["Normal"]
   styleBH.alignment = TA_CENTER
   styleBH.fontSize = 12

   #columnas
   d1 = Paragraph('''Ruta''', styleBH)
   d2 = Paragraph('''Localidad''', styleBH)
   d3 = Paragraph('''N° Camiones''', styleBH)
   d4 = Paragraph('''Color''', styleBH)
   d5 = Paragraph('''Tiempo''', styleBH)
   d6 = Paragraph('''N° Quejas''', styleBH)

   #lista de datos
   data = []

   data.append([d1, d2, d3, d4, d5, d6])

   #filas
   styles = getSampleStyleSheet()
   styleN = styles["Normal"]
   styleN.alignment = TA_CENTER
   styleN.fontSize = 7

   width, height = letter

   high = 530

   for t in infoRuta:
      t1 = Paragraph(t.nombre_ruta, styleBH)
      t2 = Paragraph(t.localidad, styleBH)
      t3 = Paragraph(str(t.ncamiones), styleBH)
      t4 = Paragraph(t.color, styleBH)
      t5 = Paragraph(str(t.tiempo), styleBH)
      t6 = Paragraph(str(numQuejas), styleBH)
      
      #rutita = [t1, t.localidad, t.ncamiones, t.color, t.tiempo, numQuejas]
      # data.append(rutita)
      data.append([t1, t2, t3, t4, t5, t6])
      high = high - 18

   #escribir la tabla.
   width, height = letter  # tamaño de la hoja
   table = Table(data, colWidths=[3.2*cm, 3.2*cm,
                                  3.2*cm, 3*cm, 2*cm, 2.5*cm])
   table.setStyle(TableStyle([
      ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
      ('BOX', (0,0), (-1,-1), 0.25, colors.black),]))

   table.wrapOn(c, width,height)
   table.drawOn(c,60, high)

#TABLA DE QUEJAS POR UNIDAD.
   color = "#91140A"
   c.setFillColor(color)
   c.setFont('Helvetica', 20)
   c.drawString(150, 470, 'NÚMERO DE QUEJAS POR UNIDAD.')

   styles = getSampleStyleSheet()
   ss = styles["Normal"]
   ss.alignment = TA_CENTER
   ss.fontSize = 12

   #columnas
   r1 = Paragraph('''NÚMERO DE UNIDAD''', ss)
   r2 = Paragraph('''NÚMERO DE QUEJAS''', ss)

   #lista de datos
   data2 = []

   data2.append([r1, r2])

   width, height = letter

   high = 430

   conthigh = 0
   conthigh2 = 0

   for unidad, quejas in zip(unidades, vecesQuejas):
      conthigh += 1 

      if conthigh >= 2:
         un = Paragraph(str(unidad), ss)
         qu = Paragraph(str(quejas), ss)

         data2.append([un, qu])
         high = high - 18
         conthigh2 += 18

      elif conthigh == 1:
         un = Paragraph(str(unidad), ss)
         qu = Paragraph(str(quejas), ss)

         data2.append([un, qu])
         high = high - 18

   #escribir la tabla.
   width, height = letter  # tamaño de la hoja
   table2 = Table(data2, colWidths=[5*cm, 5*cm])
   table2.setStyle(TableStyle([
       ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
       ('BOX', (0, 0), (-1, -1), 0.25, colors.black), ]))

   table2.wrapOn(c, width, height)
   table2.drawOn(c, 180, high)


   alturaNueva = 370 - conthigh2


   #TABLA DE QUEJAS .
   color = "#91140A"
   c.setFillColor(color)
   c.setFont('Helvetica', 20)
   if conthigh == 1:
      c.drawString(190, 370, 'QUEJAS Y SUGERENCIAS.')
   elif conthigh >= 2:
      c.drawString(190, alturaNueva, 'QUEJAS Y SUGERENCIAS.')

   

   styles = getSampleStyleSheet()
   see = styles["Normal"]
   see.alignment = TA_CENTER
   see.fontSize = 12

         #columnas
   r1 = Paragraph('''USUARIO''', see)
   r2 = Paragraph('''UNIDAD''', see)
   r3 = Paragraph('''FECHA''', see)
   r4 = Paragraph('''TEXTO''', see)

         #lista de datos
   data3 = []

   data3.append([r1, r2, r3, r4])

   width, height = letter

   if conthigh == 1:
      high = 330
   elif conthigh >= 2:
      alturaNueva2 = 330 - conthigh2
      high = alturaNueva2
   

   cont2 = 0

   contalt3 = 0
   contaalt31 = 240

   for queja in quejasRuta:
      contalt3 += 1

      if contalt3 >= 3:
         f1 = Paragraph(queja.usuario, see)
         f2 = Paragraph(str(queja.unidad), see)
         f3 = Paragraph(str(queja.fecha), see)
         f4 = Paragraph(queja.texto, see)

         data3.append([f1, f2, f3, f4])
         high = high - 18
         contaalt31 += 20

      elif contalt3 == 1 or contalt3 == 2:
         f1 = Paragraph(queja.usuario, see)
         f2 = Paragraph(str(queja.unidad), see)
         f3 = Paragraph(str(queja.fecha), see)
         f4 = Paragraph(queja.texto, see)

         data3.append([f1, f2, f3, f4])
         high = high - 18

         contaalt31 = 240

         #escribir la tabla.
   width, height = letter  # tamaño de la hoja
   table3 = Table(data3, colWidths=[3*cm, 3*cm, 3*cm, 8.5*cm, ])
   table3.setStyle(TableStyle([
      ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
      ('BOX', (0, 0), (-1, -1), 0.25, colors.red), ]))

   table3.wrapOn(c, width, height)
   table3.drawOn(c, 60, high)

   coco = high - 30

   color = "black"
   c.setFillColor(color)
   c.setFont('Helvetica', 12)
   c.drawString(50, coco, 'Observaciones:')
   c.line(150, coco, 550, coco)
   c.line(50, coco-20, 550, coco-20)
   c.line(50, coco-40, 550, coco-40)
   c.line(50, coco-60, 550, coco-60)

   alturaNueva4 = coco-120
   c.setFont('Helvetica', 12)
   c.drawString(200, alturaNueva4, 'NOMBRE Y FIRMA DE CONCESIONARIO:')
   c.line(160, alturaNueva4-25, 460, alturaNueva4-25)



   c.showPage()
   c.save()

   pdf = buffer.getvalue()
   buffer.close()
   response.write(pdf)
   return response




def verPdfBusquedas(request):

   #Sacar todos los datos del conc, su ruta y sus quejas
   datosCons = Concesionario.objects.filter(
       conce__icontains=request.session['conce'])

   for d in datosCons:
      nombre = d.nombre_conce
      rutaEncargada = d.nombre_ruta

   #Sacar datos de la ruta de la que esta encargado el concesionario
   infoRuta = Rutas.objects.filter(nombre_ruta__icontains=rutaEncargada)

   #Sacar todas las quejas de esa ruta
   busquedas = rutasBuscadas.objects.filter(
       nombre_ruta__icontains=rutaEncargada)
   
   numeroDeBusquedas = 0

   for ya in busquedas:
      numeroDeBusquedas += 1
   
   todasBusquedas = rutasBuscadas.objects.all()

   numBusquedas = 0

   rutasbuscadas = []

   for bu in todasBusquedas:
      numBusquedas += 1
      n = bu.nombre_ruta

      if numBusquedas >= 2:
         if n in rutasbuscadas:
            siesta= True
         else: 
            rutasbuscadas.append(n)
      elif numBusquedas == 1:
         rutasbuscadas.append(n)

   cont = 0
   vecesBusquedas = []

   for u in rutasbuscadas:
      for o in todasBusquedas:
         if o.nombre_ruta == u:
            cont += 1
      vecesBusquedas.append(cont)
      cont = 0

   #pdf
   response = HttpResponse(content_type='application/pdf')
   response['Content-Disposition'] = 'attachment; filename= Reporte Busqueda Usuarios.pdf'

   buffer = BytesIO()
   c = canvas.Canvas(buffer, pagesize=letter)

   # HEADER
   color = "#F3B416"
   c.setFillColor(color)
   c.setFont('Helvetica', 22)
   c.drawString(270, 740, 'Bustop')

   color = "black"
   c.setFillColor(color)
   c.setFont('Helvetica', 12)
   c.drawString(230, 725, 'Te llevamos a donde quieras.')

   hoy = datetime.now()

   fecha = str(hoy.date())

   c.setFont('Helvetica-Bold', 12)
   c.drawString(480, 740, fecha)

   c.line(460, 737, 560, 737)

   #TITULO
   color = "#0A7D91"
   c.setFillColor(color)
   c.setStrokeColor(color)
   c.setFont('Helvetica', 24)
   c.drawString(125, 680, 'REPORTE DE USUARIOS EN RUTA')

   #DATOS CONCESIONARIO
   color = "black"
   c.setFillColor(color)
   c.setFont('Helvetica', 20)
   c.drawString(200, 640, 'DATOS CONCESIONARIO.')

   c.setFont('Helvetica', 12)
   c.drawString(50, 610, 'Nombre del Concesionario:')
   color = "#91140A"
   c.setFillColor(color)
   c.drawString(210, 610, nombre)
   color = "black"
   c.setFillColor(color)
   c.line(200, 605, 310, 605)

   color = "black"
   c.setFillColor(color)
   c.setFont('Helvetica', 12)
   c.drawString(340, 610, 'Ruta a cargo:')
   color = "#91140A"
   c.setFillColor(color)
   c.drawString(440, 610, rutaEncargada)
   color = "black"
   c.setFillColor(color)
   c.line(430, 605, 510, 605)
   #DATOS DE LA RUTA
   c.setFont('Helvetica', 20)
   c.drawString(200, 565, 'INFORMACIÓN DE RUTA.')

   styles = getSampleStyleSheet()
   styleBH = styles["Normal"]
   styleBH.alignment = TA_CENTER
   styleBH.fontSize = 12

   #columnas
   d1 = Paragraph('''Ruta''', styleBH)
   d2 = Paragraph('''Localidad''', styleBH)
   d3 = Paragraph('''N° Camiones''', styleBH)
   d4 = Paragraph('''Color''', styleBH)
   d5 = Paragraph('''Tiempo''', styleBH)
   d6 = Paragraph('''N° Búsquedas''', styleBH)

   #lista de datos
   data = []

   data.append([d1, d2, d3, d4, d5, d6])

   #filas
   styles = getSampleStyleSheet()
   styleN = styles["Normal"]
   styleN.alignment = TA_CENTER
   styleN.fontSize = 7

   width, height = letter

   high = 530

   for t in infoRuta:
      t1 = Paragraph(t.nombre_ruta, styleBH)
      t2 = Paragraph(t.localidad, styleBH)
      t3 = Paragraph(str(t.ncamiones), styleBH)
      t4 = Paragraph(t.color, styleBH)
      t5 = Paragraph(str(t.tiempo), styleBH)
      t6 = Paragraph(str(numeroDeBusquedas), styleBH)

      #rutita = [t1, t.localidad, t.ncamiones, t.color, t.tiempo, numQuejas]
      # data.append(rutita)
      data.append([t1, t2, t3, t4, t5, t6])
      high = high - 18

   #escribir la tabla.
   width, height = letter  # tamaño de la hoja
   table = Table(data, colWidths=[3.2*cm, 3.2*cm,
                                  3.2*cm, 3*cm, 2*cm, 2.5*cm])
   table.setStyle(TableStyle([
       ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
       ('BOX', (0, 0), (-1, -1), 0.25, colors.black), ]))

   table.wrapOn(c, width, height)
   table.drawOn(c, 60, high)

#TABLA DE QUEJAS POR UNIDAD.
   color = "#91140A"
   c.setFillColor(color)
   c.setFont('Helvetica', 20)
   c.drawString(150, 470, 'TABLA COMPARATIVA CON OTRAS RUTAS.')

   styles = getSampleStyleSheet()
   ss = styles["Normal"]
   ss.alignment = TA_CENTER
   ss.fontSize = 12

   #columnas
   r1 = Paragraph('''NOMBRE DE RUTA''', ss)
   r2 = Paragraph('''NÚMERO DE BÚSQUEDAS''', ss)

   #lista de datos
   data2 = []

   data2.append([r1, r2])

   width, height = letter

   high = 430

   conthigh = 0
   conthigh2 = 0

   for ruta, bus in zip(rutasbuscadas, vecesBusquedas):
      conthigh += 1

      if conthigh >= 2:
         un = Paragraph(str(ruta), ss)
         qu = Paragraph(str(bus), ss)

         data2.append([un, qu])
         high = high - 18
         conthigh2 += 18

      elif conthigh == 1:
         un = Paragraph(str(ruta), ss)
         qu = Paragraph(str(bus), ss)

         data2.append([un, qu])
         high = high - 18

   #escribir la tabla.
   width, height = letter  # tamaño de la hoja
   table2 = Table(data2, colWidths=[5*cm, 5*cm])
   table2.setStyle(TableStyle([
       ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
       ('BOX', (0, 0), (-1, -1), 0.25, colors.black), ]))

   table2.wrapOn(c, width, height)
   table2.drawOn(c, 180, high)

   alturaNueva = 370 - conthigh2


   color = "black"
   c.setFillColor(color)
   c.setFont('Helvetica', 12)
   c.drawString(50, alturaNueva, 'Observaciones:')
   c.line(150, alturaNueva, 550, alturaNueva)
   c.line(50, alturaNueva-20, 550, alturaNueva-20)
   c.line(50, alturaNueva-40, 550, alturaNueva-40)
   c.line(50, alturaNueva-60, 550, alturaNueva-60)

   alturaNueva4 = alturaNueva-120
   c.setFont('Helvetica', 12)
   c.drawString(200, alturaNueva4, 'NOMBRE Y FIRMA DE CONCESIONARIO:')
   c.line(160, alturaNueva4-25, 460, alturaNueva4-25)

   c.showPage()
   c.save()

   pdf = buffer.getvalue()
   buffer.close()
   response.write(pdf)
   return response










def verPdfUsuarios(request):

   listaUsuarios = Usuarios.objects.all()

   nombre = request.session['admin']

   numUsuarios = 0

   for x in listaUsuarios:
      numUsuarios+=1

   #pdf
   response = HttpResponse(content_type='application/pdf')
   response['Content-Disposition'] = 'attachment; filename= Lista de Usuarios Bustop.pdf'

   buffer = BytesIO()
   c = canvas.Canvas(buffer, pagesize=letter)

   # HEADER
   color = "#F3B416"
   c.setFillColor(color)
   c.setFont('Helvetica', 22)
   c.drawString(270, 740, 'Bustop')

   color = "black"
   c.setFillColor(color)
   c.setFont('Helvetica', 12)
   c.drawString(230, 725, 'Te llevamos a donde quieras.')

   hoy = datetime.now()

   fecha = str(hoy.date())

   c.setFont('Helvetica-Bold', 12)
   c.drawString(480, 740, fecha)

   c.line(460, 737, 560, 737)

   #TITULO
   color = "#0A7D91"
   c.setFillColor(color)
   c.setStrokeColor(color)
   c.setFont('Helvetica', 24)
   c.drawString(125, 680, 'REPORTE DE LISTA DE USUARIOS')

   #DATOS CONCESIONARIO
   color = "black"
   c.setFillColor(color)
   c.setFont('Helvetica', 20)
   c.drawString(200, 640, 'DATOS DE USUARIOS.')

   c.setFont('Helvetica', 12)
   c.drawString(50, 610, 'Nombre del Administrador:')
   color = "#91140A"
   c.setFillColor(color)
   c.drawString(210, 610, nombre)
   color = "black"
   c.setFillColor(color)
   c.line(200, 605, 310, 605)

   color = "black"
   c.setFillColor(color)
   c.setFont('Helvetica', 12)
   c.drawString(340, 610, 'Número de usuarios:')
   color = "#91140A"
   c.setFillColor(color)
   c.drawString(480, 610, str(numUsuarios))
   color = "black"
   c.setFillColor(color)
   c.line(475, 605, 500, 605)
   #DATOS DE LA RUTA
   c.setFont('Helvetica', 20)
   c.drawString(200, 565, 'LISTA DE USUARIOS EN BUSTOP.')

   styles = getSampleStyleSheet()
   styleBH = styles["Normal"]
   styleBH.alignment = TA_CENTER
   styleBH.fontSize = 12

   #columnas
   d1 = Paragraph('''Nombre de Usuario''', styleBH)
   d2 = Paragraph('''Nombre''', styleBH)
   d3 = Paragraph('''Apellido''', styleBH)
   d4 = Paragraph('''Localidad''', styleBH)
   d5 = Paragraph('''Correo''', styleBH)
   d6 = Paragraph('''Fecha de Nac.''', styleBH)

   #lista de datos
   data = []

   data.append([d1, d2, d3, d4, d5, d6])

   #filas
   styles = getSampleStyleSheet()
   styleN = styles["Normal"]
   styleN.alignment = TA_CENTER
   styleN.fontSize = 7

   width, height = letter

   high = 490
   co = 0
   co2 = 0
   for t in listaUsuarios:
      co +=1

      if co >= 2:
         t1 = Paragraph(t.usuario, styleBH)
         t2 = Paragraph(t.nombre, styleBH)
         t3 = Paragraph(t.apellido, styleBH)
         t4 = Paragraph(t.localidad, styleBH)
         t5 = Paragraph(t.correo, styleBH)
         t6 = Paragraph(str(t.nacimiento), styleBH)
         data.append([t1, t2, t3, t4, t5, t6])
         high = high - 18
         co2 += 18

      elif co == 1:
         t1 = Paragraph(t.usuario, styleBH)
         t2 = Paragraph(t.nombre, styleBH)
         t3 = Paragraph(t.apellido, styleBH)
         t4 = Paragraph(t.localidad, styleBH)
         t5 = Paragraph(t.correo, styleBH)
         t6 = Paragraph(str(t.nacimiento), styleBH)
         data.append([t1, t2, t3, t4, t5, t6])
         high = high - 18

   #escribir la tabla.
   width, height = letter  # tamaño de la hoja
   table = Table(data, colWidths=[3*cm, 2.5*cm,
                                  2.5*cm, 2.5*cm, 5*cm, 4*cm])
   table.setStyle(TableStyle([
       ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
       ('BOX', (0, 0), (-1, -1), 0.25, colors.black), ]))

   table.wrapOn(c, width, height)
   table.drawOn(c, 40, high)

   if co >= 2:
      alturaNueva = 420 + co2
   elif co == 1:
      alturaNueva = 420

   color = "black"
   c.setFillColor(color)
   c.setFont('Helvetica', 12)
   c.drawString(50, alturaNueva, 'Observaciones:')
   c.line(150, alturaNueva, 550, alturaNueva)
   c.line(50, alturaNueva-20, 550, alturaNueva-20)
   c.line(50, alturaNueva-40, 550, alturaNueva-40)
   c.line(50, alturaNueva-60, 550, alturaNueva-60)

   alturaNueva4 = alturaNueva-120
   c.setFont('Helvetica', 12)
   c.drawString(200, alturaNueva4, 'NOMBRE Y FIRMA DE ADMINISTRADOR:')
   c.line(160, alturaNueva4-25, 460, alturaNueva4-25)

   c.showPage()
   c.save()

   pdf = buffer.getvalue()
   buffer.close()
   response.write(pdf)
   return response
