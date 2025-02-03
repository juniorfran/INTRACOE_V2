import requests
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from .serializers import AuthResponseSerializer

class AutenticacionAPIView(APIView):
    # Límite de intentos de autenticación permitidos
    max_attempts = 2

    def post(self, request):
        # Inicializar contador de intentos en la sesión si no existe
        if "auth_attempts" not in request.session:
            request.session["auth_attempts"] = 0
        
        # Verificar si se alcanzó el máximo de intentos permitidos
        if request.session["auth_attempts"] >= self.max_attempts:
            return Response({
                "status": "error",
                "message": "Se alcanzó el límite de intentos de autenticación permitidos",
            }, status=status.HTTP_403_FORBIDDEN)  # Código 403: Forbidden

        user = request.data.get("user")  # Usuario enviado desde el cuerpo de la solicitud
        pwd = request.data.get("pwd")    # Contraseña enviada desde el cuerpo de la solicitud

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

        try:
            # Realizar solicitud POST a la URL de autenticación
            response = requests.post(auth_url, headers=headers, data=data)
            
            # Intentar convertir la respuesta en JSON
            response_data = response.json()

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

                return Response({
                    "status": "success",
                    "token": f"{token_type} {token}",
                    "roles": roles,
                })

            else:
                return Response({
                    "status": "error",
                    "message": response_data.get("message", "Error en autenticación"),
                    "error": response_data.get("error", "No especificado"),
                }, status=status.HTTP_400_BAD_REQUEST)

        except requests.exceptions.RequestException as e:
            # Error de conexión con el servicio
            return Response({
                "status": "error",
                "message": "Error de conexión con el servicio de autenticación",
                "details": str(e),
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
