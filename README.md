# Instrucciones de instalación y ejecución

## 1. Crear un entorno virtual

Para crear un entorno virtual en tu proyecto, ejecuta el siguiente comando dependiendo del sistema operativo que estés utilizando:

### Bash (Linux/macOS)
```bash
python -m venv env
```

### PowerShell (Windows)
```powershell
python -m venv env
```

### CMD (Windows)
```cmd
python -m venv env
```

## 2. Activar el entorno virtual

Una vez creado el entorno virtual, actívalo según el sistema operativo:

### Bash (Linux/macOS)
```bash
source env/Scripts/activate
```

### PowerShell (Windows)
```powershell
.\env\Scripts\Activate.ps1
```

### CMD (Windows)
```cmd
.\env\Scripts\activate
```

## 3. Instalar las dependencias

Después de activar el entorno virtual, instala las dependencias del proyecto ejecutando el siguiente comando:

```bash
pip install -r requirements.txt
```

## 4. Ejecutar la aplicación

Para ejecutar la aplicación principal, utiliza el siguiente comando:

```bash
python app.py
```

## 5. Realizar pruebas de manera estática

Si necesitas realizar pruebas de manera estática, puedes ejecutar el siguiente comando:

```bash
python consumir.py
```
