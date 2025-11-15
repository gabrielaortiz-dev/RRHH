"""
Aplicación Flask principal para el sistema de RRHH.
"""
from flask import Flask, jsonify, request
from flask_cors import CORS
from database import get_db, init_db
from models.user import User
from models.empleado import Empleado
from models.contrato import Contrato
from models.asistencia import Asistencia
from models.capacitacion import Capacitacion
from models.evaluacion import Evaluacion
from models.nomina import Nomina
from models.vacacion_permiso import VacacionPermiso
from config import get_config

# Crear la aplicación Flask
app = Flask(__name__)

# Cargar configuración según el entorno
config_class = get_config()
app.config.from_object(config_class)
config_class.init_app(app)

# Configurar CORS con los orígenes permitidos
CORS(app, origins=app.config['CORS_ORIGINS'])


@app.route('/api/health', methods=['GET'])
def health_check():
    """Endpoint para verificar el estado del servidor."""
    return jsonify({
        'status': 'ok',
        'message': 'Backend funcionando correctamente'
    }), 200


@app.route('/api/database/init', methods=['POST'])
def initialize_database():
    """Endpoint para inicializar la base de datos."""
    try:
        init_db()
        return jsonify({
            'status': 'success',
            'message': 'Base de datos inicializada correctamente'
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/api/database/test', methods=['GET'])
def test_database():
    """Endpoint para probar la conexión a la base de datos."""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = [row[0] for row in cursor.fetchall()]
            return jsonify({
                'status': 'success',
                'message': 'Conexión a la base de datos exitosa',
                'tables': tables
            }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Error al conectar con la base de datos: {str(e)}'
        }), 500


# ==================== RUTAS DE USUARIOS ====================

@app.route('/api/users', methods=['GET'])
def get_users():
    """Obtiene todos los usuarios."""
    try:
        users = User.get_all()
        return jsonify({
            'status': 'success',
            'data': users,
            'count': len(users)
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Error al obtener usuarios: {str(e)}'
        }), 500


@app.route('/api/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """Obtiene un usuario por su ID."""
    try:
        user = User.get_by_id(user_id)
        if user:
            return jsonify({
                'status': 'success',
                'data': user
            }), 200
        else:
            return jsonify({
                'status': 'error',
                'message': 'Usuario no encontrado'
            }), 404
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Error al obtener usuario: {str(e)}'
        }), 500


@app.route('/api/users', methods=['POST'])
def create_user():
    """Crea un nuevo usuario."""
    try:
        data = request.get_json()
        
        # Validar datos requeridos
        if not data:
            return jsonify({
                'status': 'error',
                'message': 'No se proporcionaron datos'
            }), 400
        
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        
        if not username or not email or not password:
            return jsonify({
                'status': 'error',
                'message': 'Faltan datos requeridos: username, email, password'
            }), 400
        
        # Validar formato de email básico
        if '@' not in email:
            return jsonify({
                'status': 'error',
                'message': 'El formato del email no es válido'
            }), 400
        
        # Crear el usuario
        user = User.create(username, email, password)
        
        return jsonify({
            'status': 'success',
            'message': 'Usuario creado correctamente',
            'data': user
        }), 201
        
    except ValueError as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Error al crear usuario: {str(e)}'
        }), 500


@app.route('/api/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    """Actualiza un usuario existente."""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'status': 'error',
                'message': 'No se proporcionaron datos'
            }), 400
        
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        
        # Validar formato de email si se proporciona
        if email and '@' not in email:
            return jsonify({
                'status': 'error',
                'message': 'El formato del email no es válido'
            }), 400
        
        # Actualizar el usuario
        user = User.update(user_id, username=username, email=email, password=password)
        
        if user:
            return jsonify({
                'status': 'success',
                'message': 'Usuario actualizado correctamente',
                'data': user
            }), 200
        else:
            return jsonify({
                'status': 'error',
                'message': 'Usuario no encontrado'
            }), 404
        
    except ValueError as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Error al actualizar usuario: {str(e)}'
        }), 500


@app.route('/api/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    """Elimina un usuario."""
    try:
        deleted = User.delete(user_id)
        
        if deleted:
            return jsonify({
                'status': 'success',
                'message': 'Usuario eliminado correctamente'
            }), 200
        else:
            return jsonify({
                'status': 'error',
                'message': 'Usuario no encontrado'
            }), 404
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Error al eliminar usuario: {str(e)}'
        }), 500


# ==================== RUTAS DE EMPLEADOS (Nueva estructura) ====================

@app.route('/api/empleados', methods=['POST'])
def create_empleado():
    """Crea un nuevo empleado (tabla Empleados)."""
    try:
        data = request.get_json()
        
        # Validar datos requeridos
        if not data:
            return jsonify({
                'status': 'error',
                'message': 'No se proporcionaron datos'
            }), 400
        
        nombre = data.get('nombre')
        apellido = data.get('apellido')
        
        if not nombre or not apellido:
            return jsonify({
                'status': 'error',
                'message': 'Faltan datos requeridos: nombre, apellido'
            }), 400
        
        # Obtener datos opcionales
        fecha_nacimiento = data.get('fecha_nacimiento')
        genero = data.get('genero')
        estado_civil = data.get('estado_civil')
        direccion = data.get('direccion')
        telefono = data.get('telefono')
        correo = data.get('correo')
        fecha_ingreso = data.get('fecha_ingreso')
        estado = data.get('estado')
        id_departamento = data.get('id_departamento')
        id_puesto = data.get('id_puesto')
        
        # Convertir IDs a int si se proporcionan
        if id_departamento is not None:
            try:
                id_departamento = int(id_departamento)
            except (ValueError, TypeError):
                return jsonify({
                    'status': 'error',
                    'message': 'id_departamento debe ser un número entero'
                }), 400
        
        if id_puesto is not None:
            try:
                id_puesto = int(id_puesto)
            except (ValueError, TypeError):
                return jsonify({
                    'status': 'error',
                    'message': 'id_puesto debe ser un número entero'
                }), 400
        
        # Crear el empleado
        empleado = Empleado.create(
            nombre=nombre,
            apellido=apellido,
            fecha_nacimiento=fecha_nacimiento,
            genero=genero,
            estado_civil=estado_civil,
            direccion=direccion,
            telefono=telefono,
            correo=correo,
            fecha_ingreso=fecha_ingreso,
            estado=estado,
            id_departamento=id_departamento,
            id_puesto=id_puesto
        )
        
        return jsonify({
            'status': 'success',
            'message': 'Empleado creado correctamente',
            'data': empleado
        }), 201
        
    except ValueError as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Error al crear empleado: {str(e)}'
        }), 500


@app.route('/api/empleados', methods=['GET'])
def get_empleados():
    """Obtiene todos los empleados (tabla Empleados)."""
    try:
        empleados = Empleado.get_all()
        return jsonify({
            'status': 'success',
            'data': empleados,
            'count': len(empleados)
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Error al obtener empleados: {str(e)}'
        }), 500


@app.route('/api/empleados/<int:empleado_id>', methods=['GET'])
def get_empleado(empleado_id):
    """Obtiene un empleado por su ID (tabla Empleados)."""
    try:
        empleado = Empleado.get_by_id(empleado_id)
        if empleado:
            return jsonify({
                'status': 'success',
                'data': empleado
            }), 200
        else:
            return jsonify({
                'status': 'error',
                'message': 'Empleado no encontrado'
            }), 404
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Error al obtener empleado: {str(e)}'
        }), 500


@app.route('/api/empleados/<int:empleado_id>', methods=['PUT'])
def update_empleado(empleado_id):
    """Actualiza un empleado existente (tabla Empleados)."""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'status': 'error',
                'message': 'No se proporcionaron datos'
            }), 400
        
        # Convertir IDs a int si se proporcionan
        if 'id_departamento' in data and data['id_departamento'] is not None:
            try:
                data['id_departamento'] = int(data['id_departamento'])
            except (ValueError, TypeError):
                return jsonify({
                    'status': 'error',
                    'message': 'id_departamento debe ser un número entero'
                }), 400
        
        if 'id_puesto' in data and data['id_puesto'] is not None:
            try:
                data['id_puesto'] = int(data['id_puesto'])
            except (ValueError, TypeError):
                return jsonify({
                    'status': 'error',
                    'message': 'id_puesto debe ser un número entero'
                }), 400
        
        # Actualizar el empleado
        empleado = Empleado.update(
            empleado_id,
            nombre=data.get('nombre'),
            apellido=data.get('apellido'),
            fecha_nacimiento=data.get('fecha_nacimiento'),
            genero=data.get('genero'),
            estado_civil=data.get('estado_civil'),
            direccion=data.get('direccion'),
            telefono=data.get('telefono'),
            correo=data.get('correo'),
            fecha_ingreso=data.get('fecha_ingreso'),
            estado=data.get('estado'),
            id_departamento=data.get('id_departamento'),
            id_puesto=data.get('id_puesto')
        )
        
        if empleado:
            return jsonify({
                'status': 'success',
                'message': 'Empleado actualizado correctamente',
                'data': empleado
            }), 200
        else:
            return jsonify({
                'status': 'error',
                'message': 'Empleado no encontrado'
            }), 404
        
    except ValueError as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Error al actualizar empleado: {str(e)}'
        }), 500


@app.route('/api/empleados/<int:empleado_id>', methods=['DELETE'])
def delete_empleado(empleado_id):
    """Elimina un empleado (tabla Empleados)."""
    try:
        deleted = Empleado.delete(empleado_id)
        
        if deleted:
            return jsonify({
                'status': 'success',
                'message': 'Empleado eliminado correctamente'
            }), 200
        else:
            return jsonify({
                'status': 'error',
                'message': 'Empleado no encontrado'
            }), 404
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Error al eliminar empleado: {str(e)}'
        }), 500


# ==================== RUTAS DE CONTRATOS ====================

@app.route('/api/contratos', methods=['POST'])
def create_contrato():
    """Crea un nuevo contrato."""
    try:
        data = request.get_json()
        
        # Validar datos requeridos
        if not data:
            return jsonify({
                'status': 'error',
                'message': 'No se proporcionaron datos'
            }), 400
        
        id_empleado = data.get('id_empleado')
        
        if id_empleado is None:
            return jsonify({
                'status': 'error',
                'message': 'Falta dato requerido: id_empleado'
            }), 400
        
        # Convertir id_empleado a int
        try:
            id_empleado = int(id_empleado)
        except (ValueError, TypeError):
            return jsonify({
                'status': 'error',
                'message': 'id_empleado debe ser un número entero'
            }), 400
        
        # Obtener datos opcionales
        tipo_contrato = data.get('tipo_contrato')
        fecha_inicio = data.get('fecha_inicio')
        fecha_fin = data.get('fecha_fin')
        salario = data.get('salario')
        condiciones = data.get('condiciones')
        
        # Convertir salario a float si se proporciona
        if salario is not None:
            try:
                salario = float(salario)
            except (ValueError, TypeError):
                return jsonify({
                    'status': 'error',
                    'message': 'salario debe ser un número'
                }), 400
        
        # Crear el contrato
        contrato = Contrato.create(
            id_empleado=id_empleado,
            tipo_contrato=tipo_contrato,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            salario=salario,
            condiciones=condiciones
        )
        
        return jsonify({
            'status': 'success',
            'message': 'Contrato creado correctamente',
            'data': contrato
        }), 201
        
    except ValueError as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Error al crear contrato: {str(e)}'
        }), 500


@app.route('/api/contratos', methods=['GET'])
def get_contratos():
    """Obtiene todos los contratos."""
    try:
        contratos = Contrato.get_all()
        return jsonify({
            'status': 'success',
            'data': contratos,
            'count': len(contratos)
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Error al obtener contratos: {str(e)}'
        }), 500


@app.route('/api/contratos/<int:contrato_id>', methods=['GET'])
def get_contrato(contrato_id):
    """Obtiene un contrato por su ID."""
    try:
        contrato = Contrato.get_by_id(contrato_id)
        if contrato:
            return jsonify({
                'status': 'success',
                'data': contrato
            }), 200
        else:
            return jsonify({
                'status': 'error',
                'message': 'Contrato no encontrado'
            }), 404
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Error al obtener contrato: {str(e)}'
        }), 500


@app.route('/api/contratos/empleado/<int:empleado_id>', methods=['GET'])
def get_contratos_by_empleado(empleado_id):
    """Obtiene todos los contratos de un empleado."""
    try:
        contratos = Contrato.get_by_empleado(empleado_id)
        return jsonify({
            'status': 'success',
            'data': contratos,
            'count': len(contratos)
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Error al obtener contratos del empleado: {str(e)}'
        }), 500


@app.route('/api/contratos/<int:contrato_id>', methods=['PUT'])
def update_contrato(contrato_id):
    """Actualiza un contrato existente."""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'status': 'error',
                'message': 'No se proporcionaron datos'
            }), 400
        
        # Convertir id_empleado a int si se proporciona
        if 'id_empleado' in data and data['id_empleado'] is not None:
            try:
                data['id_empleado'] = int(data['id_empleado'])
            except (ValueError, TypeError):
                return jsonify({
                    'status': 'error',
                    'message': 'id_empleado debe ser un número entero'
                }), 400
        
        # Convertir salario a float si se proporciona
        if 'salario' in data and data['salario'] is not None:
            try:
                data['salario'] = float(data['salario'])
            except (ValueError, TypeError):
                return jsonify({
                    'status': 'error',
                    'message': 'salario debe ser un número'
                }), 400
        
        # Actualizar el contrato
        contrato = Contrato.update(
            contrato_id,
            id_empleado=data.get('id_empleado'),
            tipo_contrato=data.get('tipo_contrato'),
            fecha_inicio=data.get('fecha_inicio'),
            fecha_fin=data.get('fecha_fin'),
            salario=data.get('salario'),
            condiciones=data.get('condiciones')
        )
        
        if contrato:
            return jsonify({
                'status': 'success',
                'message': 'Contrato actualizado correctamente',
                'data': contrato
            }), 200
        else:
            return jsonify({
                'status': 'error',
                'message': 'Contrato no encontrado'
            }), 404
        
    except ValueError as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Error al actualizar contrato: {str(e)}'
        }), 500


@app.route('/api/contratos/<int:contrato_id>', methods=['DELETE'])
def delete_contrato(contrato_id):
    """Elimina un contrato."""
    try:
        deleted = Contrato.delete(contrato_id)
        
        if deleted:
            return jsonify({
                'status': 'success',
                'message': 'Contrato eliminado correctamente'
            }), 200
        else:
            return jsonify({
                'status': 'error',
                'message': 'Contrato no encontrado'
            }), 404
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Error al eliminar contrato: {str(e)}'
        }), 500


# ==================== RUTAS DE ASISTENCIAS ====================

@app.route('/api/asistencias', methods=['POST'])
def create_asistencia():
    """Crea una nueva asistencia."""
    try:
        data = request.get_json()
        if not data or data.get('id_empleado') is None:
            return jsonify({'status': 'error', 'message': 'id_empleado es requerido'}), 400
        
        id_empleado = int(data['id_empleado'])
        asistencia = Asistencia.create(
            id_empleado=id_empleado,
            fecha=data.get('fecha'),
            hora_entrada=data.get('hora_entrada'),
            hora_salida=data.get('hora_salida'),
            observaciones=data.get('observaciones')
        )
        return jsonify({'status': 'success', 'message': 'Asistencia creada correctamente', 'data': asistencia}), 201
    except ValueError as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Error al crear asistencia: {str(e)}'}), 500

@app.route('/api/asistencias', methods=['GET'])
def get_asistencias():
    """Obtiene todas las asistencias."""
    try:
        asistencias = Asistencia.get_all()
        return jsonify({'status': 'success', 'data': asistencias, 'count': len(asistencias)}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Error al obtener asistencias: {str(e)}'}), 500

@app.route('/api/asistencias/<int:asistencia_id>', methods=['GET'])
def get_asistencia(asistencia_id):
    """Obtiene una asistencia por su ID."""
    try:
        asistencia = Asistencia.get_by_id(asistencia_id)
        if asistencia:
            return jsonify({'status': 'success', 'data': asistencia}), 200
        return jsonify({'status': 'error', 'message': 'Asistencia no encontrada'}), 404
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Error al obtener asistencia: {str(e)}'}), 500

@app.route('/api/asistencias/empleado/<int:empleado_id>', methods=['GET'])
def get_asistencias_by_empleado(empleado_id):
    """Obtiene todas las asistencias de un empleado."""
    try:
        asistencias = Asistencia.get_by_empleado(empleado_id)
        return jsonify({'status': 'success', 'data': asistencias, 'count': len(asistencias)}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Error al obtener asistencias: {str(e)}'}), 500

@app.route('/api/asistencias/<int:asistencia_id>', methods=['PUT'])
def update_asistencia(asistencia_id):
    """Actualiza una asistencia."""
    try:
        data = request.get_json()
        asistencia = Asistencia.update(asistencia_id,
            id_empleado=int(data['id_empleado']) if 'id_empleado' in data else None,
            fecha=data.get('fecha'),
            hora_entrada=data.get('hora_entrada'),
            hora_salida=data.get('hora_salida'),
            observaciones=data.get('observaciones')
        )
        if asistencia:
            return jsonify({'status': 'success', 'message': 'Asistencia actualizada correctamente', 'data': asistencia}), 200
        return jsonify({'status': 'error', 'message': 'Asistencia no encontrada'}), 404
    except ValueError as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Error al actualizar asistencia: {str(e)}'}), 500

@app.route('/api/asistencias/<int:asistencia_id>', methods=['DELETE'])
def delete_asistencia(asistencia_id):
    """Elimina una asistencia."""
    try:
        deleted = Asistencia.delete(asistencia_id)
        if deleted:
            return jsonify({'status': 'success', 'message': 'Asistencia eliminada correctamente'}), 200
        return jsonify({'status': 'error', 'message': 'Asistencia no encontrada'}), 404
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Error al eliminar asistencia: {str(e)}'}), 500


# ==================== RUTAS DE CAPACITACIONES ====================

@app.route('/api/capacitaciones', methods=['POST'])
def create_capacitacion():
    """Crea una nueva capacitación."""
    try:
        data = request.get_json()
        if not data or data.get('id_empleado') is None:
            return jsonify({'status': 'error', 'message': 'id_empleado es requerido'}), 400
        
        capacitacion = Capacitacion.create(
            id_empleado=int(data['id_empleado']),
            nombre_curso=data.get('nombre_curso'),
            institucion=data.get('institucion'),
            fecha_inicio=data.get('fecha_inicio'),
            fecha_fin=data.get('fecha_fin'),
            certificado=data.get('certificado', False)
        )
        return jsonify({'status': 'success', 'message': 'Capacitación creada correctamente', 'data': capacitacion}), 201
    except ValueError as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Error al crear capacitación: {str(e)}'}), 500

@app.route('/api/capacitaciones', methods=['GET'])
def get_capacitaciones():
    """Obtiene todas las capacitaciones."""
    try:
        capacitaciones = Capacitacion.get_all()
        return jsonify({'status': 'success', 'data': capacitaciones, 'count': len(capacitaciones)}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Error al obtener capacitaciones: {str(e)}'}), 500

@app.route('/api/capacitaciones/<int:capacitacion_id>', methods=['GET'])
def get_capacitacion(capacitacion_id):
    """Obtiene una capacitación por su ID."""
    try:
        capacitacion = Capacitacion.get_by_id(capacitacion_id)
        if capacitacion:
            return jsonify({'status': 'success', 'data': capacitacion}), 200
        return jsonify({'status': 'error', 'message': 'Capacitación no encontrada'}), 404
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Error al obtener capacitación: {str(e)}'}), 500

@app.route('/api/capacitaciones/empleado/<int:empleado_id>', methods=['GET'])
def get_capacitaciones_by_empleado(empleado_id):
    """Obtiene todas las capacitaciones de un empleado."""
    try:
        capacitaciones = Capacitacion.get_by_empleado(empleado_id)
        return jsonify({'status': 'success', 'data': capacitaciones, 'count': len(capacitaciones)}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Error al obtener capacitaciones: {str(e)}'}), 500

@app.route('/api/capacitaciones/<int:capacitacion_id>', methods=['PUT'])
def update_capacitacion(capacitacion_id):
    """Actualiza una capacitación."""
    try:
        data = request.get_json()
        capacitacion = Capacitacion.update(capacitacion_id,
            id_empleado=int(data['id_empleado']) if 'id_empleado' in data else None,
            nombre_curso=data.get('nombre_curso'),
            institucion=data.get('institucion'),
            fecha_inicio=data.get('fecha_inicio'),
            fecha_fin=data.get('fecha_fin'),
            certificado=data.get('certificado')
        )
        if capacitacion:
            return jsonify({'status': 'success', 'message': 'Capacitación actualizada correctamente', 'data': capacitacion}), 200
        return jsonify({'status': 'error', 'message': 'Capacitación no encontrada'}), 404
    except ValueError as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Error al actualizar capacitación: {str(e)}'}), 500

@app.route('/api/capacitaciones/<int:capacitacion_id>', methods=['DELETE'])
def delete_capacitacion(capacitacion_id):
    """Elimina una capacitación."""
    try:
        deleted = Capacitacion.delete(capacitacion_id)
        if deleted:
            return jsonify({'status': 'success', 'message': 'Capacitación eliminada correctamente'}), 200
        return jsonify({'status': 'error', 'message': 'Capacitación no encontrada'}), 404
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Error al eliminar capacitación: {str(e)}'}), 500


# ==================== RUTAS DE EVALUACIONES ====================

@app.route('/api/evaluaciones', methods=['POST'])
def create_evaluacion():
    """Crea una nueva evaluación."""
    try:
        data = request.get_json()
        if not data or data.get('id_empleado') is None:
            return jsonify({'status': 'error', 'message': 'id_empleado es requerido'}), 400
        
        evaluacion = Evaluacion.create(
            id_empleado=int(data['id_empleado']),
            fecha=data.get('fecha'),
            evaluador=data.get('evaluador'),
            puntaje=int(data['puntaje']) if 'puntaje' in data and data['puntaje'] is not None else None,
            observaciones=data.get('observaciones')
        )
        return jsonify({'status': 'success', 'message': 'Evaluación creada correctamente', 'data': evaluacion}), 201
    except ValueError as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Error al crear evaluación: {str(e)}'}), 500

@app.route('/api/evaluaciones', methods=['GET'])
def get_evaluaciones():
    """Obtiene todas las evaluaciones."""
    try:
        evaluaciones = Evaluacion.get_all()
        return jsonify({'status': 'success', 'data': evaluaciones, 'count': len(evaluaciones)}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Error al obtener evaluaciones: {str(e)}'}), 500

@app.route('/api/evaluaciones/<int:evaluacion_id>', methods=['GET'])
def get_evaluacion(evaluacion_id):
    """Obtiene una evaluación por su ID."""
    try:
        evaluacion = Evaluacion.get_by_id(evaluacion_id)
        if evaluacion:
            return jsonify({'status': 'success', 'data': evaluacion}), 200
        return jsonify({'status': 'error', 'message': 'Evaluación no encontrada'}), 404
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Error al obtener evaluación: {str(e)}'}), 500

@app.route('/api/evaluaciones/empleado/<int:empleado_id>', methods=['GET'])
def get_evaluaciones_by_empleado(empleado_id):
    """Obtiene todas las evaluaciones de un empleado."""
    try:
        evaluaciones = Evaluacion.get_by_empleado(empleado_id)
        return jsonify({'status': 'success', 'data': evaluaciones, 'count': len(evaluaciones)}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Error al obtener evaluaciones: {str(e)}'}), 500

@app.route('/api/evaluaciones/<int:evaluacion_id>', methods=['PUT'])
def update_evaluacion(evaluacion_id):
    """Actualiza una evaluación."""
    try:
        data = request.get_json()
        evaluacion = Evaluacion.update(evaluacion_id,
            id_empleado=int(data['id_empleado']) if 'id_empleado' in data else None,
            fecha=data.get('fecha'),
            evaluador=data.get('evaluador'),
            puntaje=int(data['puntaje']) if 'puntaje' in data and data['puntaje'] is not None else None,
            observaciones=data.get('observaciones')
        )
        if evaluacion:
            return jsonify({'status': 'success', 'message': 'Evaluación actualizada correctamente', 'data': evaluacion}), 200
        return jsonify({'status': 'error', 'message': 'Evaluación no encontrada'}), 404
    except ValueError as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Error al actualizar evaluación: {str(e)}'}), 500

@app.route('/api/evaluaciones/<int:evaluacion_id>', methods=['DELETE'])
def delete_evaluacion(evaluacion_id):
    """Elimina una evaluación."""
    try:
        deleted = Evaluacion.delete(evaluacion_id)
        if deleted:
            return jsonify({'status': 'success', 'message': 'Evaluación eliminada correctamente'}), 200
        return jsonify({'status': 'error', 'message': 'Evaluación no encontrada'}), 404
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Error al eliminar evaluación: {str(e)}'}), 500


# ==================== RUTAS DE NÓMINA ====================

@app.route('/api/nomina', methods=['POST'])
def create_nomina():
    """Crea un nuevo registro de nómina."""
    try:
        data = request.get_json()
        if not data or data.get('id_empleado') is None:
            return jsonify({'status': 'error', 'message': 'id_empleado es requerido'}), 400
        
        nomina = Nomina.create(
            id_empleado=int(data['id_empleado']),
            mes=int(data['mes']) if 'mes' in data and data['mes'] is not None else None,
            anio=int(data['anio']) if 'anio' in data and data['anio'] is not None else None,
            salario_base=float(data['salario_base']) if 'salario_base' in data and data['salario_base'] is not None else None,
            bonificaciones=float(data['bonificaciones']) if 'bonificaciones' in data and data['bonificaciones'] is not None else None,
            deducciones=float(data['deducciones']) if 'deducciones' in data and data['deducciones'] is not None else None,
            salario_neto=float(data['salario_neto']) if 'salario_neto' in data and data['salario_neto'] is not None else None,
            fecha_pago=data.get('fecha_pago')
        )
        return jsonify({'status': 'success', 'message': 'Registro de nómina creado correctamente', 'data': nomina}), 201
    except ValueError as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Error al crear registro de nómina: {str(e)}'}), 500

@app.route('/api/nomina', methods=['GET'])
def get_nomina():
    """Obtiene todos los registros de nómina."""
    try:
        nomina = Nomina.get_all()
        return jsonify({'status': 'success', 'data': nomina, 'count': len(nomina)}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Error al obtener registros de nómina: {str(e)}'}), 500

@app.route('/api/nomina/<int:nomina_id>', methods=['GET'])
def get_nomina_by_id(nomina_id):
    """Obtiene un registro de nómina por su ID."""
    try:
        nomina = Nomina.get_by_id(nomina_id)
        if nomina:
            return jsonify({'status': 'success', 'data': nomina}), 200
        return jsonify({'status': 'error', 'message': 'Registro de nómina no encontrado'}), 404
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Error al obtener registro de nómina: {str(e)}'}), 500

@app.route('/api/nomina/empleado/<int:empleado_id>', methods=['GET'])
def get_nomina_by_empleado(empleado_id):
    """Obtiene todos los registros de nómina de un empleado."""
    try:
        nomina = Nomina.get_by_empleado(empleado_id)
        return jsonify({'status': 'success', 'data': nomina, 'count': len(nomina)}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Error al obtener registros de nómina: {str(e)}'}), 500

@app.route('/api/nomina/<int:nomina_id>', methods=['PUT'])
def update_nomina(nomina_id):
    """Actualiza un registro de nómina."""
    try:
        data = request.get_json()
        nomina = Nomina.update(nomina_id,
            id_empleado=int(data['id_empleado']) if 'id_empleado' in data else None,
            mes=int(data['mes']) if 'mes' in data and data['mes'] is not None else None,
            anio=int(data['anio']) if 'anio' in data and data['anio'] is not None else None,
            salario_base=float(data['salario_base']) if 'salario_base' in data and data['salario_base'] is not None else None,
            bonificaciones=float(data['bonificaciones']) if 'bonificaciones' in data and data['bonificaciones'] is not None else None,
            deducciones=float(data['deducciones']) if 'deducciones' in data and data['deducciones'] is not None else None,
            salario_neto=float(data['salario_neto']) if 'salario_neto' in data and data['salario_neto'] is not None else None,
            fecha_pago=data.get('fecha_pago')
        )
        if nomina:
            return jsonify({'status': 'success', 'message': 'Registro de nómina actualizado correctamente', 'data': nomina}), 200
        return jsonify({'status': 'error', 'message': 'Registro de nómina no encontrado'}), 404
    except ValueError as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Error al actualizar registro de nómina: {str(e)}'}), 500

@app.route('/api/nomina/<int:nomina_id>', methods=['DELETE'])
def delete_nomina(nomina_id):
    """Elimina un registro de nómina."""
    try:
        deleted = Nomina.delete(nomina_id)
        if deleted:
            return jsonify({'status': 'success', 'message': 'Registro de nómina eliminado correctamente'}), 200
        return jsonify({'status': 'error', 'message': 'Registro de nómina no encontrado'}), 404
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Error al eliminar registro de nómina: {str(e)}'}), 500


# ==================== RUTAS DE VACACIONES Y PERMISOS ====================

@app.route('/api/vacaciones-permisos', methods=['POST'])
def create_vacacion_permiso():
    """Crea un nuevo registro de vacación o permiso."""
    try:
        data = request.get_json()
        if not data or data.get('id_empleado') is None:
            return jsonify({'status': 'error', 'message': 'id_empleado es requerido'}), 400
        
        permiso = VacacionPermiso.create(
            id_empleado=int(data['id_empleado']),
            tipo=data.get('tipo'),
            fecha_solicitud=data.get('fecha_solicitud'),
            fecha_inicio=data.get('fecha_inicio'),
            fecha_fin=data.get('fecha_fin'),
            estado=data.get('estado'),
            observaciones=data.get('observaciones')
        )
        return jsonify({'status': 'success', 'message': 'Vacación/Permiso creado correctamente', 'data': permiso}), 201
    except ValueError as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Error al crear vacación/permiso: {str(e)}'}), 500

@app.route('/api/vacaciones-permisos', methods=['GET'])
def get_vacaciones_permisos():
    """Obtiene todos los registros de vacaciones y permisos."""
    try:
        permisos = VacacionPermiso.get_all()
        return jsonify({'status': 'success', 'data': permisos, 'count': len(permisos)}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Error al obtener vacaciones/permisos: {str(e)}'}), 500

@app.route('/api/vacaciones-permisos/<int:permiso_id>', methods=['GET'])
def get_vacacion_permiso(permiso_id):
    """Obtiene un registro de vacación/permiso por su ID."""
    try:
        permiso = VacacionPermiso.get_by_id(permiso_id)
        if permiso:
            return jsonify({'status': 'success', 'data': permiso}), 200
        return jsonify({'status': 'error', 'message': 'Vacación/Permiso no encontrado'}), 404
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Error al obtener vacación/permiso: {str(e)}'}), 500

@app.route('/api/vacaciones-permisos/empleado/<int:empleado_id>', methods=['GET'])
def get_vacaciones_permisos_by_empleado(empleado_id):
    """Obtiene todos los registros de vacaciones/permisos de un empleado."""
    try:
        permisos = VacacionPermiso.get_by_empleado(empleado_id)
        return jsonify({'status': 'success', 'data': permisos, 'count': len(permisos)}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Error al obtener vacaciones/permisos: {str(e)}'}), 500

@app.route('/api/vacaciones-permisos/<int:permiso_id>', methods=['PUT'])
def update_vacacion_permiso(permiso_id):
    """Actualiza un registro de vacación/permiso."""
    try:
        data = request.get_json()
        permiso = VacacionPermiso.update(permiso_id,
            id_empleado=int(data['id_empleado']) if 'id_empleado' in data else None,
            tipo=data.get('tipo'),
            fecha_solicitud=data.get('fecha_solicitud'),
            fecha_inicio=data.get('fecha_inicio'),
            fecha_fin=data.get('fecha_fin'),
            estado=data.get('estado'),
            observaciones=data.get('observaciones')
        )
        if permiso:
            return jsonify({'status': 'success', 'message': 'Vacación/Permiso actualizado correctamente', 'data': permiso}), 200
        return jsonify({'status': 'error', 'message': 'Vacación/Permiso no encontrado'}), 404
    except ValueError as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Error al actualizar vacación/permiso: {str(e)}'}), 500

@app.route('/api/vacaciones-permisos/<int:permiso_id>', methods=['DELETE'])
def delete_vacacion_permiso(permiso_id):
    """Elimina un registro de vacación/permiso."""
    try:
        deleted = VacacionPermiso.delete(permiso_id)
        if deleted:
            return jsonify({'status': 'success', 'message': 'Vacación/Permiso eliminado correctamente'}), 200
        return jsonify({'status': 'error', 'message': 'Vacación/Permiso no encontrado'}), 404
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Error al eliminar vacación/permiso: {str(e)}'}), 500


if __name__ == '__main__':
    # Inicializar la base de datos al arrancar
    init_db()
    
    # Iniciar el servidor usando la configuración del entorno
    app.run(
        debug=app.config['DEBUG'],
        host=app.config['HOST'],
        port=app.config['PORT']
    )

