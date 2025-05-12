# Ecualizador de 5 Bandas

Un ecualizador de audio interactivo con 5 bandas de frecuencia y visualización en tiempo real, desarrollado en Python con Tkinter y Matplotlib.

## Características

- Generador de señales con 3 componentes ajustables (frecuencia y amplitud)
- Ecualizador de 5 bandas con rangos de frecuencia definidos:
  - Banda 1: 0-100 Hz
  - Banda 2: 101-200 Hz
  - Banda 3: 201-300 Hz
  - Banda 4: 301-400 Hz
  - Banda 5: 401-500 Hz
- Visualización en tiempo real de señales en:
  - Dominio del tiempo
  - Dominio de la frecuencia (FFT)
- Interfaz gráfica intuitiva con actualización instantánea al modificar parámetros

## Requisitos

- Python 3.x
- NumPy
- Matplotlib
- tkinter
- SciPy

## Instalación

1. Clona este repositorio:

   ```
   git clone https://github.com/tu-usuario/equalizer.git
   cd equalizer
   ```

2. Instala las dependencias:
   ```
   pip install numpy matplotlib scipy
   ```

## Uso

Ejecuta el programa principal:

```
python main.py
```

- Ajusta las frecuencias y amplitudes de los componentes de la señal usando los sliders
- Activa o desactiva las bandas del ecualizador mediante las casillas de verificación
- Observa los cambios en tiempo real en las gráficas de tiempo y frecuencia

## Estructura del proyecto

- `main.py`: Punto de entrada del programa
- `ui.py`: Interfaz gráfica de usuario
- `signal_generator.py`: Generador de señales
- `filters.py`: Implementación de los filtros del ecualizador
- `mixer.py`: Mezclador de señales filtradas

## Licencia

[MIT](LICENSE)
