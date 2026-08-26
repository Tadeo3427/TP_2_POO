class MantenimientoError(Exception):
    """
    Excepción base para los errores de nuestro sistema de mantenimiento.
    Todas nuestras excepciones personalizadas heredan de esta clase.
    """
    pass


class CampoVacioError(MantenimientoError):
    """Se lanza cuando se intenta ingresar un campo obligatorio en blanco."""
    pass


class TareaNoEncontradaError(MantenimientoError):
    """Se lanza cuando se busca un número de OT que no existe en el sistema."""
    pass


class TareaNoModificableError(MantenimientoError):
    """Se lanza al intentar editar o cancelar una tarea que ya está finalizada o cancelada."""
    pass