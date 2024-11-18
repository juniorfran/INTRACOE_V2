import requests
from django.shortcuts import render
from django.http import JsonResponse

def autenticacion(request):
    # Límite de intentos de autenticación permitidos
    max_attempts = 2
    
    # Inicializar contador de intentos en la sesión si no existe
    if "auth_attempts" not in request.session:
        request.session["auth_attempts"] = 0
    
    # Verificar si se alcanzó el máximo de intentos permitidos
    if request.session["auth_attempts"] >= max_attempts:
        print("Se alcanzó el límite de intentos permitidos")
        return JsonResponse({
            "status": "error",
            "message": "Se alcanzó el límite de intentos de autenticación permitidos",
        }, status=403)  # Código 403: Forbidden

    if request.method == "POST":
        # Obtener credenciales del formulario
        user = request.POST.get("user")  # Usuario enviado desde el formulario
        pwd = request.POST.get("pwd")    # Contraseña enviada desde el formulario

        # URL de autenticación
        auth_url = "https://api.dtes.mh.gob.sv/seguridad/auth"
        
        # Headers para la solicitud
        headers = {
            "User-Agent": "MiAplicacionDjango/1.0",
            "Content-Type": "application/x-www-form-urlencoded",
        }

        # Datos para el cuerpo de la solicitud
        data = {
            "user": user,
            "pwd": pwd,
        }

        # Imprimir datos de depuración
        print("URL de autenticación:", auth_url)
        print("Headers:", headers)
        print("Datos enviados:", data)
        print("Intento actual de autenticación:", request.session["auth_attempts"] + 1)

        try:
            # Realizar solicitud POST a la URL de autenticación
            response = requests.post(auth_url, headers=headers, data=data)
            print("Código de respuesta:", response.status_code)
            print("Respuesta de la API:", response.text)
            
            # Intentar convertir la respuesta en JSON
            response_data = response.json()
            print("Datos JSON de respuesta:", response_data)

            # Incrementar el contador de intentos de autenticación
            request.session["auth_attempts"] += 1
            request.session.modified = True  # Asegura que los cambios en la sesión se guarden

            # Procesar respuesta en caso de éxito
            if response.status_code == 200 and response_data.get("status") == "OK":
                # Resetear el contador de intentos si autenticación fue exitosa
                request.session["auth_attempts"] = 0
                token = response_data["body"].get("token")
                roles = response_data["body"].get("roles", [])
                token_type = response_data.get("tokenType", "Bearer")

                print("Autenticación exitosa. Token obtenido:", token)
                print("Roles asignados:", roles)
                print("Tipo de Token:", token_type)

                # Retornar token y otros detalles al frontend
                return JsonResponse({
                    "status": "success",
                    "token": f"{token_type} {token}",
                    "roles": roles,
                })

            else:
                # Error en autenticación, se suma un intento
                print("Error en autenticación:", response_data)
                return JsonResponse({
                    "status": "error",
                    "message": response_data.get("message", "Error en autenticación"),
                    "error": response_data.get("error", "No especificado"),
                }, status=400)

        except requests.exceptions.RequestException as e:
            # Error de conexión con el servicio
            print("Error de conexión con el servicio de autenticación:", e)
            return JsonResponse({
                "status": "error",
                "message": "Error de conexión con el servicio de autenticación",
                "details": str(e),
            }, status=500)

    # Si el método es GET, renderizar el formulario
    return render(request, "autenticacion.html")
