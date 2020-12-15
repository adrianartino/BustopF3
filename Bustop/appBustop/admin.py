from django.contrib import admin

from appBustop.models import Usuarios, Rutas, Admin, Concesionario, QuejasUsuarios, rutasBuscadas, rutasAgregadas, ConcAgregados
# Register your models here.
class UsuariosAdmin(admin.ModelAdmin):
    list_display=("usuario", "nombre", "apellido", "localidad")
    search_fields = ("usuario", "nombre", "apellido", "localidad")
    list_filter = ("localidad","nacimiento",)
    date_hierarchy = "nacimiento"

class RutasAdmin(admin.ModelAdmin):
    list_display = ("nombre_ruta", "color", "tiempo")
    search_fields = ("nombre_ruta",)
    list_filter = ("nombre_ruta", "color",)

class AdminAdmin(admin.ModelAdmin):
    list_display = ("nombre_admin",)
    search_fields = ("nombre_admin",)


class ConcesionarioAdmin(admin.ModelAdmin):
    list_display = ("conce", "nombre_conce", "nombre_ruta")
    search_fields = ("conce", "nombre_conce", "nombre_ruta")
    list_filter = ("nombre_ruta",)


class QuejasAdmin(admin.ModelAdmin):
    list_display = ("usuario", "nombre_ruta", "fecha")
    search_fields = ("usuario", "nombre_ruta", "fecha")
    list_filter = ("nombre_ruta", "fecha")
    date_hierarchy = "fecha"


class rutasBuscadasAdmin(admin.ModelAdmin):
    list_display = ("usuario", "nombre_ruta")
    search_fields = ("usuario", "nombre_ruta")
    list_filter = ("nombre_ruta",)


class rutasAgregadasAdmin(admin.ModelAdmin):
    list_display = ("nombre_ruta", "nombre_admin")
    search_fields = ("nombre_ruta", "nombre_admin")
    list_filter = ("nombre_admin",)


class ConcAgregadosAdmin(admin.ModelAdmin):
    list_display = ("conce", "nombre_admin")
    search_fields = ("conce", "nombre_admin")
    list_filter = ("nombre_admin",)


admin.site.register(Usuarios, UsuariosAdmin)
admin.site.register(Rutas, RutasAdmin)
admin.site.register(Admin, AdminAdmin)
admin.site.register(Concesionario, ConcesionarioAdmin)
admin.site.register(QuejasUsuarios, QuejasAdmin)
admin.site.register(rutasBuscadas, rutasBuscadasAdmin)
admin.site.register(rutasAgregadas, rutasAgregadasAdmin)
admin.site.register(ConcAgregados, ConcAgregadosAdmin)
