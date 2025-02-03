# views.py
import json
import os
from django.db.models import Q
from django.shortcuts import render
from django.core.paginator import Paginator
from django.db import connections
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string
from django.urls import reverse
from django.http import HttpResponse
from weasyprint import HTML, CSS
from decimal import Decimal
import tempfile
from django.conf import settings
from django.core.mail import EmailMessage
from datetime import datetime
from .models import Proveedor, Quedan, facturas_quedan, quedan_pago_state
from datetime import date
from django.db import transaction

def obtener_id_proveedor(nit=None, nrc=None):
    """
    Función para obtener el ID del proveedor según NIT o NRC.
    :param nit: Número de Identificación Tributaria (NIT)
    :param nrc: Número de Registro de Contribuyente (NRC)
    :return: ID del proveedor o None si no se encuentra
    """
    try:
        print(f"Buscando proveedor con NIT: {nit} y NRC: {nrc}")  # Imprime para depuración
        
        if nit:
            proveedor = Proveedor.objects.get(nit=nit)
        elif nrc:
            proveedor = Proveedor.objects.get(nrc=nrc)
        else:
            return None  # Ningún parámetro fue proporcionado
        
        return proveedor.id
    except Proveedor.DoesNotExist:
        print(f"No se encontró proveedor con NIT: {nit} o NRC: {nrc}")  # Imprime para depuración
        return None  # No se encontró el proveedor

#funcion para guardar los datos de los proveedores
def guardar_proveedor(nombre, apellido, nombre_empresa, nit, nrc, telefono_empresa, correo_empresa, direccion_empresa, telefono, direccion, fecha_alta, fecha_baja, estado):
    # Verificar si ya existe un proveedor con el mismo NIT o correo
    proveedor_existente = Proveedor.objects.filter(nit=nit).exists() or Proveedor.objects.filter(correo_empresa=correo_empresa).exists()

    if proveedor_existente:
        return JsonResponse({
            'success': False,
            'message': 'El proveedor ya está registrado con el mismo NIT o correo electrónico.'
        })

    # Crear y guardar el nuevo proveedor
    proveedor = Proveedor(
        nombre=nombre,
        apellido=apellido,
        nombre_empresa=nombre_empresa,
        nit=nit,
        nrc=nrc,
        telefono_empresa=telefono_empresa,
        correo_empresa=correo_empresa,
        direccion_empresa=direccion_empresa,
        telefono=telefono,
        direccion=direccion,
        fecha_alta=fecha_alta,
        fecha_baja=fecha_baja,
        estado=estado
    )
    proveedor.save()

    return JsonResponse({
        'success': True,
        'message': 'Proveedor guardado exitosamente.'
    })

#funcion para guardar los quedan generados.
def guardar_quedan(proveedor_id, numero_quedan, fecha_entrega, comentario_quedan, cant_facturas, estado_enviado, ultima_fecha_pago, fecha_alta, fecha_baja):
    quedan_existe = Quedan.objects.filter(numero_quedan = numero_quedan, estado_enviado=True).exists()

    if quedan_existe:
        return JsonResponse({
            'success': False,
            'message': 'El quedan ya está registrado con el mismo número o estado de envío.'
        })
    
    try:        
        #crear y guardar el nuevo quedan
        quedan = Quedan(
            proveedor_id = proveedor_id,
            numero_quedan=numero_quedan,
            fecha_entrega=fecha_entrega,
            comentario_quedan=comentario_quedan,
            cant_facturas=cant_facturas,
            estado_enviado=estado_enviado,
            ultima_fecha_pago=ultima_fecha_pago,
            fecha_alta=fecha_alta,
            fecha_baja=fecha_baja
        )
        quedan.save()

        return JsonResponse({
            'success': True,
            'id':quedan.id,
            'message': 'Quedan guardado exitosamente.'
        })
    except Exception as e:
        return{
            'success': False,
            'message': 'Error al guardar el quedan: '+ str(e)
        }

def guardar_factura(proveedor_id, quedan_id, tipo_doc, num_doc, fecha_doc, suma_efect, porcentaje_ret_iva, porcentaje_percep, total_pagar, porcentaje_iva):
    try:
        # Validar si el proveedor y el quedan existen
        #proveedor = Proveedor.objects.filter(id=proveedor_id).first()
        quedan = Quedan.objects.filter(id=quedan_id).first()

        # if not proveedor:
        #     return {
        #         'success': False,
        #         'message': 'El proveedor con ID {} no existe.'.format(proveedor_id)
        #     }
        if not quedan:
            return {
                'success': False,
                'message': 'El quedan con ID {} no existe.'.format(quedan_id)
            }

        # Guardar la factura
        with transaction.atomic():
            factura = facturas_quedan(
                proveedor_id=proveedor_id,
                quedan_id=quedan_id,
                tipo_doc=tipo_doc,
                num_doc=num_doc,
                fecha_doc=fecha_doc,
                suma_efect=suma_efect,
                porcentaje_ret_iva=porcentaje_ret_iva,
                porcentaje_percep=porcentaje_percep,
                total_pagar=total_pagar,
                porcentaje_iva=porcentaje_iva
            )
            factura.save()

        return {
            'success': True,
            'message': 'Factura guardada exitosamente.'
        }
    except Exception as e:
        return {
            'success': False,
            'message': 'Error al guardar la factura: {}'.format(str(e))
        }
    
#funcion para gaurdar un estado de pago de los quedan
def guardar_estado_pago(quedan_id, fecha_pago, monto_pago, estado_pago):
    #verificar si el quedan existe
    quedan_existe = Quedan.objects.filter(id = quedan_id).exists()
    #guardar el estado de pago del quedan en el caso de que xista el proveedor
    if quedan_existe:
        estado_pago_quedan = quedan_pago_state(
            quedan_id = quedan_id,
            fecha_pago = fecha_pago,
            monto_pago = monto_pago,
            estado_pago = estado_pago
            )
        estado_pago_quedan.save()
        return JsonResponse({
            'success': True,
            'message': 'Estado de pago guardado exitosamente.'
            })
    else:
        return JsonResponse({
            'success': False,
            'message': 'El quedan no existe.'
            })

#funcion para obtener los estados de pago de los quedan
def obtener_estados_pago(quedan_id):
    #verificar si el quedan existe
    quedan_existe = Quedan.objects.filter(id = quedan_id).exists()
    #obtener los estados de pago del quedan en el caso de que xista el prov
    if quedan_existe:
        estado_pago_quedan = quedan_pago_state.objects.filter(quedan_id = quedan_id)
        return JsonResponse({
            'success': True,
            'data': list(estado_pago_quedan.values())
            })
    else:
        return JsonResponse({
            'success': False,
            'message': 'El quedan no existe.'
            })


@login_required
def listar_quedans_enviados(request):
    quedans = Quedan.objects.filter(estado_enviado=True).order_by('numero_quedan')

    paginator = Paginator(quedans, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'quedans/listar_quedans_enviados.html', {'page_obj':page_obj})

# @login_required
# def listar_quedans_enviados(request):
#     if request.method == 'POST':
#         query = """
#             SELECT mcoTipoDoc, mcoNumDoc, mcoFecha, mcoSumasAfecto, mcoPorcentRetIVA, mcoPorcentPercep, mcoTotalAPagarManual, mcoPorcentIVA 
#             FROM olCompras.dbo.maeCompras 
#             WHERE mqdnId = %s
#         """

@login_required
# LISTAR y SINCRONIZAR PROVEEDORES DESDE SQLSERVER
def listar_proveedores(request):
    # Obtener todos los proveedores activos
    proveedores = Proveedor.objects.filter(estado=True).order_by('nombre')
    # Crear un objeto Paginator. Vamos a mostrar 10 proveedores por página.
    paginator = Paginator(proveedores, 10)
    # Obtener el número de página actual de la solicitud
    page_number = request.GET.get('page')
    # Obtener los proveedores para la página actual
    page_obj = paginator.get_page(page_number)
    # Renderizar la plantilla con los proveedores paginados
    return render(request, 'proveedores/lista_proveedores.html', {'page_obj': page_obj})

#Funcion para sincronizar proveedores de brilo en la db de INTRACOE
@login_required
def sincronizar_proveedores(request):
    if request.method == 'POST':  # Verifica si la solicitud es POST
        query = """
            SELECT 
                prvNombre AS nombre, 
                prvNomComercial AS nombre_empresa, 
                prvNit AS nit, 
                prvRegistroIva AS nrc, 
                prvTelefono AS telefono_empresa, 
                prvEmail AS correo_empresa, 
                prvDireccion AS direccion_empresa, 
                prvCelular AS telefono, 
                prvDireccion AS direccion, 
                prvFecHoraUltModif AS fecha_alta, 
                prvActivo AS estado
            FROM olComun.dbo.Proveedores
            WHERE prvActivo = 1
        """

        with connections['brilo_sqlserver'].cursor() as cursor:
            try:
                cursor.execute(query)
                resultados = cursor.fetchall()
            except Exception as e:
                print(f"Error al ejecutar la consulta: {e}")
                return JsonResponse({'success': False, 'message': 'Error en la consulta SQL'}, status=500)

        nuevos = 0
        actualizados = 0
        
        for row in resultados:
            try:
                nombre, nombre_empresa, nit, nrc, telefono_empresa, correo_empresa, direccion_empresa, telefono, direccion, fecha_alta, estado = row
                fecha_alta = fecha_alta or date.today()
                fecha_baja = None
            except Exception as e:
                print(f"Error al procesar la fila {row}: {e}")
                continue

            try:
                proveedor, creado = Proveedor.objects.update_or_create(
                    nit=nit,
                    defaults={
                        'nombre': nombre,
                        'nombre_empresa': nombre_empresa,
                        'nrc': nrc,
                        'telefono_empresa': telefono_empresa,
                        'correo_empresa': correo_empresa,
                        'direccion_empresa': direccion_empresa,
                        'telefono': telefono,
                        'direccion': direccion,
                        'fecha_alta': fecha_alta,
                        'fecha_baja': fecha_baja,
                        'estado': estado,
                    }
                )
                if creado:
                    nuevos += 1
                else:
                    actualizados += 1
            except Exception as e:
                print(f"Error al guardar o actualizar el proveedor {nit}: {e}")
                continue
        
        # Obtener todos los proveedores activos
        proveedores = Proveedor.objects.filter(estado=True).order_by('nombre')
        
        # Retornar la plantilla con los datos
        return render(request, 'proveedores/lista_proveedores.html', {
            'proveedores': proveedores,
            'nuevos': nuevos,
            'actualizados': actualizados,
        })

    # Si la solicitud no es POST, simplemente retornar la lista de proveedores
    return listar_proveedores(request)


###################################################################################################################

@login_required
def listar_quedans(request):
    proveedor_nombre = request.GET.get('proveedor_nombre', '').strip()  # Nombre del proveedor (opcional)
    fecha_quedan = request.GET.get('fecha_quedan', '').strip()  # Fecha de quedan en formato 'YYYY-MM-DD' (opcional)

    with connections['brilo_sqlserver'].cursor() as cursor:
        # Construir la consulta base con alias
        query = """
            SELECT q.mqdnId, q.mqdnNumero, q.prvId, q.mqdnFecha, q.mqdnFechaPago, q.mqdnComentarios, p.prvNombre
            FROM olCompras.dbo.maeQuedans AS q
            INNER JOIN olComun.dbo.Proveedores AS p ON q.prvId = p.prvId
        """
        
        # Filtrar según los criterios de búsqueda
        where_clauses = []
        params = []
        
        # Agregar filtros a la consulta si se proporcionan parámetros de búsqueda
        if proveedor_nombre:
            where_clauses.append("p.prvNombre LIKE %s")
            params.append(f"%{proveedor_nombre}%")
        
        if fecha_quedan:
            where_clauses.append("q.mqdnFecha = %s")
            params.append(fecha_quedan)

        if where_clauses:
            query += " WHERE " + " AND ".join(where_clauses)

        # Ordenar por fecha
        query += " ORDER BY q.mqdnFecha DESC"

        # Ejecutar la consulta con filtros
        cursor.execute(query, params)
        quedans = cursor.fetchall()

        # Paginación de resultados
        paginator = Paginator(quedans, 20)  # 20 elementos por página
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        # Preparar contexto con los resultados y los criterios de búsqueda
        context = {
            'page_obj': page_obj,
            'proveedor_nombre': proveedor_nombre,
            'fecha_quedan': fecha_quedan,
        }

    return render(request, 'quedans/listar_quedans.html', context)

@login_required
def generar_pdf_quedan(request, mqdn_id):
    with connections['brilo_sqlserver'].cursor() as cursor:
        # Consultar datos del quedan
        cursor.execute("SELECT mqdnNumero, mqdnFecha, mqdnFechaPago, mqdnComentarios, prvId FROM olCompras.dbo.maeQuedans WHERE mqdnId = %s", [mqdn_id])
        quedan = cursor.fetchone()
        
        # Consultar proveedor
        cursor.execute("SELECT prvNombre FROM olComun.dbo.Proveedores WHERE prvId = %s", [quedan[4]])
        proveedor = cursor.fetchone()

        # Consultar detalles del quedan, ahora incluye mcoPorcentRetIVA
        cursor.execute("""
            SELECT mcoTipoDoc, mcoNumDoc, mcoFecha, mcoSumasAfecto, mcoPorcentRetIVA, mcoPorcentPercep, mcoTotalAPagarManual, mcoPorcentIVA 
            FROM olCompras.dbo.maeCompras 
            WHERE mqdnId = %s
        """, [mqdn_id])
        detalles = cursor.fetchall()

        # Inicializar variables de acumulación
        total_pago = Decimal(0)
        iva_total = Decimal(0)
        percep_total = Decimal(0)
        retencion_total = Decimal(0)  # Variable para la retención total

        # Lista para almacenar los detalles procesados
        detalles_procesados = []

        # Iterar sobre los detalles para acumular los valores
        for detalle in detalles:
            # Validar que el valor no sea None antes de convertirlo a Decimal
            suma_afecto = Decimal(detalle[3]) if detalle[3] is not None else Decimal(0.00)
            por_iva = Decimal(detalle[7]) if detalle[7] is not None else Decimal(0.13)  # Valor por defecto 0.13 si el IVA es None
            por_percep = Decimal(detalle[5]) if detalle[5] is not None else Decimal(0.00)
            por_retencion = Decimal(detalle[4]) if detalle[4] is not None else Decimal(0.00)  # Retención

            # Calcular IVA, Percepción y Retención
            iva = suma_afecto * por_iva
            percep = suma_afecto * por_percep
            retencion = suma_afecto * por_retencion  # Calcular la retención

            # Acumular el total de cada factura (ahora incluyendo la retención)
            if por_percep > 0:
                total_pago += suma_afecto + iva + percep - retencion  # Restar la retención
            else:
                total_pago += suma_afecto + iva - retencion  # Restar la retención

            # Acumular IVA, Percepción y Retención (para mostrar en el template si es necesario)
            iva_total += iva
            percep_total += percep
            retencion_total += retencion  # Acumular la retención

            # Guardar el detalle procesado en la lista
            detalles_procesados.append({
                'tipo_doc': detalle[0],
                'num_doc': detalle[1],
                'fecha': detalle[2],
                'suma_afecto': suma_afecto,
                'iva': iva,
                'percep': percep,
                'retencion': retencion,  # Agregar la retención
                'total': suma_afecto + iva + percep - retencion if por_percep > 0 else suma_afecto + iva - retencion,  # Incluir retención
            })

    # Renderizar el template HTML a string
    html_content = render_to_string('quedans/quedan_template.html', {
        'quedan': quedan,
        'proveedor': proveedor,
        'detalles': detalles_procesados,
        'total_pago': total_pago,
        'iva_total': iva_total,
        'percep_total': percep_total,
        'retencion_total': retencion_total,  # Pasar el total de retención al template
    })

    # Establecer tamaño de página personalizado y márgenes
    css = CSS(string='''@page { size: A4 landscape; margin: 1cm; }''')

    # Generar el PDF
    pdf = HTML(string=html_content).write_pdf(stylesheets=[css])

    # Enviar el PDF como respuesta
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="quedan_{quedan[1]}.pdf"'
    return response

@login_required
def enviar_quedan(request, mqdn_id):
    
    with connections['brilo_sqlserver'].cursor() as cursor:
        # Consultar datos del quedan
        cursor.execute("SELECT mqdnNumero, mqdnFecha, mqdnFechaPago, mqdnComentarios, prvId FROM olCompras.dbo.maeQuedans WHERE mqdnId = %s", [mqdn_id])
        quedan = cursor.fetchone()
        
        # Consultar proveedor
        cursor.execute("SELECT prvNombre, prvEmailRepLegal, prvNit, prvRegistroIva FROM olComun.dbo.Proveedores WHERE prvId = %s", [quedan[4]])
        proveedor = cursor.fetchone()

        # Consultar detalles del quedan
        cursor.execute("""
            SELECT mcoTipoDoc, mcoNumDoc, mcoFecha, mcoSumasAfecto, mcoPorcentRetIVA, mcoPorcentPercep, mcoTotalAPagarManual, mcoPorcentIVA 
            FROM olCompras.dbo.maeCompras 
            WHERE mqdnId = %s
        """, [mqdn_id])
        detalles = cursor.fetchall()

        # Variables para el cálculo de totales
        total_pago = Decimal(0)
        iva_total = Decimal(0)
        percep_total = Decimal(0)
        retencion_total = Decimal(0)

        detalles_procesados = []
        for detalle in detalles:
            suma_afecto = Decimal(detalle[3]) if detalle[3] is not None else Decimal(0.00)
            por_iva = Decimal(detalle[7]) if detalle[7] is not None else Decimal(0.13)
            por_percep = Decimal(detalle[5]) if detalle[5] is not None else Decimal(0.00)
            por_retencion = Decimal(detalle[4]) if detalle[4] is not None else Decimal(0.00)

            iva = suma_afecto * por_iva
            percep = suma_afecto * por_percep
            retencion = suma_afecto * por_retencion

            total_factura = suma_afecto + iva + percep - retencion if por_percep > 0 else suma_afecto + iva - retencion
            total_pago += total_factura

            iva_total += iva
            percep_total += percep
            retencion_total += retencion

            detalles_procesados.append({
                'tipo_doc': detalle[0],
                'num_doc': detalle[1],
                'fecha': detalle[2],
                'suma_afecto': suma_afecto,
                'iva': iva,
                'percep': percep,
                'retencion': retencion,
                'total': total_factura,
            })

    # Obtener el NIT o NRC del proveedor desde la consulta SQL
    nit_proveedor = proveedor[2]  # Cambiar por el dato obtenido
    nrc_proveedor = proveedor[3]  # Cambiar por el dato obtenido

    # Llamar a la función para obtener el ID del proveedor
    proveedor_id = obtener_id_proveedor(nit=nit_proveedor, nrc=nrc_proveedor)
    print(f"Proveedor ID obtenido: {proveedor_id}")

    if not proveedor_id:
        return JsonResponse({
            'success': False,
            'message': 'El proveedor no fue encontrado en la base de datos.'
        })
    #guardar el quedan con la funcion guardar_quedan
    
    # Llamar a la función guardar_quedan
    response_guardar_quedan = guardar_quedan(
        proveedor_id=proveedor_id,  # ID del proveedor
        numero_quedan=quedan[0],  # Número del quedan
        fecha_entrega=quedan[1],  # Fecha de entrega
        comentario_quedan=quedan[3],  # Comentario del quedan
        cant_facturas=len(detalles_procesados),  # Cantidad de facturas
        estado_enviado=True,  # Estado de envío
        ultima_fecha_pago=quedan[2],  # Última fecha de pago
        fecha_alta=datetime.now(),  # Fecha de alta
        fecha_baja=None  # Fecha de baja (si aplica)
    )

    # Convertir el contenido de JsonResponse a un diccionario de Python
    response_data = json.loads(response_guardar_quedan.content)
    print(f"Respuesta de guardar_quedan: {response_data}")

    # Validar el éxito en el guardado
    if not response_data.get('success', False):
        return JsonResponse({
            'success': False,
            'error': 'No se pudo guardar el quedan.',
            'message': response_data.get('message', 'Error desconocido.')
        })

    # Obtener el ID del quedan
    id_quedan = response_data.get('id')  # Usar el diccionario convertido
    if not id_quedan:
        return JsonResponse({
            'success': False,
            'message': 'No se pudo obtener el ID del quedan guardado.'
        })

    # Imprimir para depuración
    print(f"ID del quedan guardado: {id_quedan}")

    # Guardar la factura en la base de datos
    guardar_factura_response = guardar_factura(
        proveedor_id=proveedor_id,
        quedan_id=id_quedan,
        tipo_doc=detalle[0],
        num_doc=detalle[1],
        fecha_doc=detalle[2],
        suma_efect=suma_afecto,
        porcentaje_ret_iva=por_retencion,
        porcentaje_percep=por_percep,
        total_pagar=total_factura,
        porcentaje_iva=por_iva
    )

    # Validar la respuesta de guardar_factura
    if not guardar_factura_response.get('success', False):
        return JsonResponse({
            'success': False,
            'message': f"Error al guardar la factura: {guardar_factura_response.get('message', 'Error desconocido.')}"
        })

    # Renderizar el template HTML
    html_content = render_to_string('quedans/quedan_template.html', {
        'quedan': quedan,
        'proveedor': proveedor,
        'detalles': detalles_procesados,
        'total_pago': total_pago,
        'iva_total': iva_total,
        'percep_total': percep_total,
        'retencion_total': retencion_total,
    })

    # Establecer los estilos CSS para el PDF
    css = CSS(string='''@page { size: A4 landscape; margin: 1cm; }''')
    pdf = HTML(string=html_content).write_pdf(stylesheets=[css])

    # Guardar el PDF temporalmente
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as pdf_file:
        pdf_file.write(pdf)
        pdf_file_path = pdf_file.name

    # Construir el asunto y el mensaje del correo
    subject = f'Quedan No. {quedan[0]} - {proveedor[0]}'
    message = (
        f'Estimado, adjunto encontrará el PDF con los detalles del quedan.\n\n'
        f'Quedan No.: {quedan[0]}\n'
        f'Cantidad de documentos: {len(detalles_procesados)}\n'
        f'Total a pagar: ${total_pago:.2f}\n\n'
        f'Saludos cordiales,\n'
        f'Departamento de Contabilidad'
    )

    # Crear el nombre del archivo con el formato solicitado
    file_name = f"QUEDAN NUM {quedan[0]} - {proveedor[0]}.pdf"

    # Crear el objeto EmailMessage
    email = EmailMessage(
        subject=subject,
        body=message,
        from_email=settings.EMAIL_HOST_USER_QUEDAN,
        to=[proveedor[1]],  # Correo del proveedor
    )

    # Adjuntar el archivo PDF al correo
    with open(pdf_file_path, 'rb') as pdf_attachment:
        email.attach(file_name, pdf_attachment.read(), 'application/pdf')
    
    # Enviar el correo
    email.send()

    # Eliminar el archivo temporal después de enviarlo
    os.remove(pdf_file_path)
    # Responder con un mensaje de éxito
    return JsonResponse({
        'success': True,
        'message': 'Quedan enviado exitosamente.',
        'modal_data': {
            'numero_quedan': quedan[0],
            'proveedor_nombre': proveedor[0],
            'proveedor_email': proveedor[1]
        }
    })

@login_required
def enviar_quedan_hoy(request):
    # Obtener la fecha actual
    today = datetime.today().date()

    with connections['brilo_sqlserver'].cursor() as cursor:
        # Consultar todos los quedan del día actual
        cursor.execute("""
            SELECT mqdnId, mqdnNumero, mqdnFecha, mqdnFechaPago, mqdnComentarios, prvId 
            FROM olCompras.dbo.maeQuedans 
            WHERE CAST(mqdnFecha AS DATE) = %s
        """, [today])
        quedans = cursor.fetchall()

        for quedan in quedans:
            # Consultar proveedor
            cursor.execute("SELECT prvNombre, prvEmailRepLegal FROM olComun.dbo.Proveedores WHERE prvId = %s", [quedan[5]])
            proveedor = cursor.fetchone()

            # Consultar detalles del quedan
            cursor.execute("""
                SELECT mcoTipoDoc, mcoNumDoc, mcoFecha, mcoSumasAfecto, mcoPorcentRetIVA, mcoPorcentPercep, 
                       mcoTotalAPagarManual, mcoPorcentIVA 
                FROM olCompras.dbo.maeCompras 
                WHERE mqdnId = %s
            """, [quedan[0]])
            detalles = cursor.fetchall()

            # Variables para el cálculo de totales
            total_pago = Decimal(0)
            iva_total = Decimal(0)
            percep_total = Decimal(0)
            retencion_total = Decimal(0)

            detalles_procesados = []
            for detalle in detalles:
                suma_afecto = Decimal(detalle[3]) if detalle[3] is not None else Decimal(0.00)
                por_iva = Decimal(detalle[7]) if detalle[7] is not None else Decimal(0.13)
                por_percep = Decimal(detalle[5]) if detalle[5] is not None else Decimal(0.00)
                por_retencion = Decimal(detalle[4]) if detalle[4] is not None else Decimal(0.00)

                iva = suma_afecto * por_iva
                percep = suma_afecto * por_percep
                retencion = suma_afecto * por_retencion

                total_factura = suma_afecto + iva + percep - retencion if por_percep > 0 else suma_afecto + iva - retencion
                total_pago += total_factura

                iva_total += iva
                percep_total += percep
                retencion_total += retencion

                detalles_procesados.append({
                    'tipo_doc': detalle[0],
                    'num_doc': detalle[1],
                    'fecha': detalle[2],
                    'suma_afecto': suma_afecto,
                    'iva': iva,
                    'percep': percep,
                    'retencion': retencion,
                    'total': total_factura,
                })

            # Renderizar el template HTML para el PDF
            html_content = render_to_string('quedans/quedan_template.html', {
                'quedan': quedan,
                'proveedor': proveedor,
                'detalles': detalles_procesados,
                'total_pago': total_pago,
                'iva_total': iva_total,
                'percep_total': percep_total,
                'retencion_total': retencion_total,
            })

            # Establecer los estilos CSS para el PDF
            css = CSS(string='''@page { size: A4 landscape; margin: 1cm; }''')
            pdf = HTML(string=html_content).write_pdf(stylesheets=[css])

            # Guardar el PDF temporalmente
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as pdf_file:
                pdf_file.write(pdf)
                pdf_file_path = pdf_file.name

            # Construir el asunto y el mensaje del correo
            subject = f'Quedan No. {quedan[1]} - {proveedor[0]}'
            message = (
                f'Estimado, adjunto encontrará el PDF con los detalles del quedan.\n\n'
                f'Quedan No.: {quedan[1]}\n'
                f'Cantidad de documentos: {len(detalles_procesados)}\n'
                f'Total a pagar: ${total_pago:.2f}\n\n'
                f'Saludos cordiales,\n'
                f'Departamento de Contabilidad'
            )

            # Crear el nombre del archivo con el formato solicitado
            file_name = f"QUEDAN NUM {quedan[1]} - {proveedor[0]}.pdf"

            # Crear el objeto EmailMessage
            email = EmailMessage(
                subject=subject,
                body=message,
                from_email=settings.EMAIL_HOST_USER_QUEDAN,
                to=[proveedor[1]],  # Correo del proveedor
            )

            # Adjuntar el archivo PDF al correo
            with open(pdf_file_path, 'rb') as pdf_attachment:
                email.attach(file_name, pdf_attachment.read(), 'application/pdf')

            # Enviar el correo
            email.send()

            # Eliminar el archivo temporal después de enviarlo
            os.remove(pdf_file_path)

    # Responder con un mensaje de éxito
    return HttpResponse("Se enviaron todos los quedans generados el día de hoy.", content_type="text/plain")
