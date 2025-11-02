# src/catalog/tasks.py

from celery import shared_task
from .models import Autor
import time

@shared_task
def generate_author_report(author_id: str):
    """
    Simula una tarea pesada de generación de reporte (tarda 10 seg).
    """
    print(f"Iniciando reporte para el autor: {author_id}...")
    
    try:
        # La tarea necesita consultar la DB
        autor = Autor.objects.get(id=author_id)
        
        # Simulación de trabajo pesado 
        time.sleep(10) 
        
        print(f"¡REPORTE COMPLETADO! Autor: {autor.full_name}")
        return f"Reporte para {autor.full_name} generado."
    except Autor.DoesNotExist:
        print(f"Error: Autor con ID {author_id} no encontrado.")
        return "Error: Autor no encontrado."