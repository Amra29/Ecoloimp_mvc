import os
from app import create_app, db
from app.models.models import Reporte, Asignacion, Tecnico, Usuario

app = create_app()


def check_database_integrity():
    """Analiza la base de datos en busca de registros huérfanos y otras inconsistencias."""
    with app.app_context():
        print("--- Iniciando Verificación de Integridad de la Base de Datos ---")
        
        # --- Verificación 1: Reportes con asignacion_id inválido ---
        reportes_huerfanos = []
        for reporte in Reporte.query.all():
            if reporte.asignacion is None:
                reportes_huerfanos.append(reporte)
        
        if reportes_huerfanos:
            print(f"\n[!] Se encontraron {len(reportes_huerfanos)} reportes con 'asignacion_id' inválido (huérfanos):")
            for r in reportes_huerfanos:
                print(f"  - Reporte ID: {r.id}, Asignacion ID: {r.asignacion_id} (no existe)")
        else:
            print("\n[OK] No se encontraron reportes con asignaciones inválidas.")

        # --- Verificación 2: Asignaciones con tecnico_id inválido ---
        asignaciones_huerfanas = []
        for asignacion in Asignacion.query.all():
            if asignacion.tecnico is None:
                asignaciones_huerfanas.append(asignacion)

        if asignaciones_huerfanas:
            print(f"\n[!] Se encontraron {len(asignaciones_huerfanas)} asignaciones con 'tecnico_id' inválido (huérfanas):")
            for a in asignaciones_huerfanas:
                print(f"  - Asignacion ID: {a.id}, Tecnico ID: {a.tecnico_id} (no existe)")
        else:
            print("\n[OK] No se encontraron asignaciones con técnicos inválidos.")

        # --- Verificación 3: Perfiles de Técnico sin Usuario asociado ---
        tecnicos_sin_usuario = []
        for tecnico in Tecnico.query.all():
            if tecnico.usuario is None:
                tecnicos_sin_usuario.append(tecnico)

        if tecnicos_sin_usuario:
            print(f"\n[!] Se encontraron {len(tecnicos_sin_usuario)} perfiles de técnico con 'usuario_id' inválido (huérfanos):")
            for t in tecnicos_sin_usuario:
                print(f"  - Tecnico ID: {t.id}, Usuario ID: {t.usuario_id} (no existe)")
        else:
            print("\n[OK] No se encontraron perfiles de técnico sin usuario.")

        # --- Verificación 4: Usuarios con rol 'tecnico' sin perfil de Técnico ---
        usuarios_tecnicos_sin_perfil = []
        usuarios_tecnicos = Usuario.query.filter_by(rol='tecnico').all()
        for usuario in usuarios_tecnicos:
            if usuario.tecnico_profile is None:
                usuarios_tecnicos_sin_perfil.append(usuario)

        if usuarios_tecnicos_sin_perfil:
            print(f"\n[!] Se encontraron {len(usuarios_tecnicos_sin_perfil)} usuarios con rol 'tecnico' sin perfil de técnico asociado:")
            for u in usuarios_tecnicos_sin_perfil:
                print(f"  - Usuario ID: {u.id}, Nombre: {u.nombre}, Email: {u.email}")
        else:
            print("\n[OK] Todos los usuarios con rol 'tecnico' tienen un perfil de técnico asociado.")

        print("\n--- Verificación de Integridad Finalizada ---")

        # --- Opción de Limpieza (ejecutar con precaución) ---
        if reportes_huerfanos or asignaciones_huerfanas or tecnicos_sin_usuario:
            print("\n*** SE ENCONTRARON INCONSISTENCIAS CRÍTICAS ***")
            respuesta = input("¿Desea intentar eliminar los registros huérfanos? (s/n): ").lower()
            if respuesta == 's':
                print("\n--- Iniciando Limpieza de Registros Huérfanos ---")
                with db.session.begin_nested():
                    try:
                        for r in reportes_huerfanos:
                            print(f"Eliminando Reporte ID: {r.id}")
                            db.session.delete(r)
                        for a in asignaciones_huerfanas:
                            print(f"Eliminando Asignacion ID: {a.id}")
                            db.session.delete(a)
                        for t in tecnicos_sin_usuario:
                            print(f"Eliminando Tecnico ID: {t.id}")
                            db.session.delete(t)
                        db.session.commit()
                        print("\n[OK] Limpieza completada. Por favor, reinicie la aplicación.")
                    except Exception as e:
                        db.session.rollback()
                        print(f"\n[ERROR] Ocurrió un error durante la limpieza: {e}")
            else:
                print("\nLimpieza cancelada. Los registros inconsistentes no fueron modificados.")

if __name__ == '__main__':
    check_database_integrity()
