***
# WorkFlow Telegram Bot App

### Create a Project

First, create a directory for your project. What I normally do is that I create a directory named MySource inside my D: Unit.
And inside of that I create one directory per project.

```
mkdir /d/MySource/Python/HelloFastApi/NewApp01
cd /d/MySource/Python/HelloFastApi/NewApp01
```

Check your python installation
```
python --version
```

### Create a Virtual Environment
When you start working on a Python project for the first time, create a virtual environment inside your project. You only need to do this once per project, not every time you work.
```
python -m venv .venv
```

-m: call a module as a script, we'll tell it which module next

venv: use the module called venv that normally comes installed with Python

.venv: create the virtual environment in the new directory .venv

### Activate the Virtual Environment

Activate the new virtual environment so that any Python command you run or package you install uses it. Do this every time you start a new terminal session to work on the project.
```
source .venv/bin/activate		# Linux bash

source .venv/Scripts/activate		#windows gitbash
```

### Check the Virtual Environment is Active

Check that the virtual environment is active (the previous command worked). This is optional, but it's a good way to check that everything is working as expected and you are using the virtual environment you intended.
```
which python
```

### Upgrade pip

If you use uv you would use it to install things instead of pip, so you don't need to upgrade pip. 😎 If you are using pip to install packages (it comes by default with Python), you should upgrade it to the latest version. Many exotic errors while installing a package are solved by just upgrading pip first.
```
python -m pip install --upgrade pip

Requirement already satisfied: pip in d:\mysource\python\hellofastapi\newapp01\.venv\lib\site-packages (24.2)
Collecting pip
  Using cached pip-25.3-py3-none-any.whl.metadata (4.7 kB)
Using cached pip-25.3-py3-none-any.whl (1.8 MB)
Installing collected packages: pip
  Attempting uninstall: pip
    Found existing installation: pip 24.2
    Uninstalling pip-24.2:
```

### Add .gitignore

If you are using Git (you should), add a .gitignore file to exclude everything in your .venv from Git. Do this once, right after you create the virtual environment.
```
echo "*" > .venv/.gitignore
```
## Install Dependencies

```
pip install -r requirements.txt
```

### Create an API Key and save it in a .env file
```
DEEPSEEK_API_KEY=your_api_key
```

### Preguntas para verificar funcionalidad
```
Conoces las peliculas del "Señor de los anillos", contesta solamente si o no
```

## pregunta (enalazada con la anterior) para verificar que recuerda el contexto de la conversacion
```
A cual de los personajes de la primera pelicula podriamos llamar protagonista? hay varios que pudieran serlo? o claramente solo hay uno?
```
deberia mantener el contexto de la conversacion, para poder responder esta pregunta correctamente.

***

# pregunta para verificar que puede usar tools
Respuesta sin tools
```
$ python main.py
Soy su asistente IA, me llamo Andrew Martin, encantado de poder ayudarte.
Usuario: Que fecha es hoy?
Quieres ver el razonamiento? (s/n)
s
Mi razonamiento fue:  El usuario pregunta la fecha actual. Como soy Andrew Martin y respondo en español, proporcionaré una respuesta útil y amigable. Primero necesito verificar la fecha actual. Hoy es 20 de julio de 2023. Daré la información de manera clara y natural, usando la estructura de fecha común en español. También agregaré una nota amistosa para mantener una conversación cálida con el usuario.
Asistente:  Hoy es 20 de julio de 2023. ¡Espero que tengas un día
``` 

Respuesta despues de incluir la herramienta date()
```
$ python main.py
Soy su asistente IA, me llamo Andrew Martin, encantado de poder ayudarte.
Usuario: Que fecha es hoy?
```

Uso de herramientas concatenadas
```
Soy su asistente IA, me llamo Andrew Martin, encantado de poder ayudarte.
Usuario: estoy en Cali, Colombia, que clima vamos a tener mañana?
```

Turn 1.1
reasoning_content='El usuario pregunta por el clima de mañana en Cali, Colombia. Necesito usar la función get_weather. Primero, debo obtener la fecha de mañana. Podría usar get_date para obtener la fecha actual y luego calcular mañana, pero también puedo simplemente calcularlo. Sin embargo, como es solo la fecha, puedo usar get_date para hoy y luego agregar un día. O tal vez la función get_weather ya maneja fechas relativas. El usuario dice "mañana", así que necesito la fecha de mañana.\n\nPuedo usar get_date para obtener la fecha actual, pero necesito calcular mañana. Como soy un asistente, puedo hacer el cálculo. Hoy es... no lo sé sin consultar. Pero puedo llamar a get_date primero. Luego, usando esa fecha, 
calcular mañana. Mejor llamar a get_date ahora.'
content=''
tool_calls=[ChatCompletionMessageFunctionToolCall(id='call_00_myxYR51XPBTsT1TA4lxzSnZn', function=Function(arguments='{}', name='get_date'), type='function', index=0)]
tool result for get_date: 2026-01-28

Turn 1.2
reasoning_content='Hoy es 28 de enero de 2026. Mañana será 29 de enero de 2026. Ahora puedo llamar a get_weather con location "Cali" y date "2026-01-29". Nota: Cali, Colombia. La función requiere location y date. La ubicación debe ser "Cali". Tal vez necesite especificar el país, pero la función dice "city name". Probablemente "Cali" sea suficiente. Lo intentaré.'
content=''
tool_calls=[ChatCompletionMessageFunctionToolCall(id='call_00_7vw9rK23XinYFlPG9spgEHDZ', function=Function(arguments='{"location": "Cali", "date": "2026-01-29"}', name='get_weather'), type='function', index=0)]
tool result for get_weather: Mañana:Soleado, 25 grados Celsius
Tarde:Parcialmente nublado, 20 grados Celsius
Noche:Lluvioso, 15 grados Celsius

Turn 1.3
reasoning_content='Tengo la respuesta. Ahora debo responder al usuario en español, con mi nombre Andrew Martin. Debo proporcionar el pronóstico del clima para mañana en Cali, Colombia. El resultado dice: Mañana: Soleado, 25 grados Celsius; 
Tarde: Parcialmente nublado, 20 grados Celsius; Noche: Lluvioso, 15 grados Celsius.\n\nPuedo formatearlo de manera agradable. Además, puedo añadir algún comentario o consejo. Pero mantengámoslo simple y claro. Recordatorio: soy Andrew Martin, respondiendo en español.'
content='¡Hola! Aquí tienes el pronóstico del tiempo para mañana **29 de enero de 2026** en **Cali, Colombia**:\n\n- **Por la mañana:** Soleado, con una temperatura de **25°C**.\n- **Por la tarde:** Parcialmente nublado, con **20°C**.\n- **Por la noche:** Lluvioso, con **15°C**.\n\nRecomiendo llevar ropa ligera durante el día y un paraguas o impermeable para la noche.\n\n¡Que tengas un excelente día!  \n\n**Andrew Martin**'
tool_calls=None
Usuario: adios
Hasta luego, que tengas un buen dia. Podemos volver a hablar cuando quieras con el comando python main.py