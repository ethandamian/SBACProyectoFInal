# SBAC - Sistema Básico de Administración de Configuración

SBAC es un sistema de control de versiones simplificado, inspirado en Git, diseñado para fines educativos y proyectos personales. Permite rastrear cambios en archivos, crear versiones (commits), gestionar ramas y etiquetas, y comparar diferentes versiones de tus archivos.

## Instalación

1.  **Clona el repositorio:**

    ```bash
    git clone https://github.com/ethandamian/SBACProyectoFInal
    ```
    ```bash
    cd SBACProyectoFInal
    ```
2.  **Haz el script `sbac` ejecutable:**

    ```bash
    chmod +x sbac
    ```

## Configuración

Antes de empezar a usar SBAC, es recomendable configurar el nombre de autor que se usará para los commits. Puedes hacerlo estableciendo la variable de entorno `USER` en tu sistema operativo.  Si no se establece, el autor por defecto será "unknown".

## Uso

SBAC se utiliza a través de la línea de comandos con el script `sbac`. A continuación, se detallan los comandos disponibles:

### `init`

Inicializa un nuevo repositorio SBAC en el directorio actual.

```bash
./sbac init
```

Este comando crea un directorio .sbac (oculto) que contiene la estructura interna del repositorio.


### `add`

Agrega uno o más archivos al área de preparación (staging area).

```bash
./sbac add <archivo1> <archivo2> ...
```

Ejemplos:

```bash
./sbac add mi_archivo.txt
```
```bash
./sbac add *.py
```
```bash
./sbac add directorio/otro_archivo.txt
```

Si un archivo no existe, SBAC mostrará un mensaje de error.

### `status`

Muestra el estado del árbol de trabajo, indicando archivos en el área de preparación (staged) y archivos no rastreados (untracked).

```bash
./sbac status
```

### `commit`

Guarda los cambios del área de preparación en el repositorio, creando un nuevo commit.

```bash
./sbac commit -m "Mensaje descriptivo del commit"
```

El mensaje del commit es obligatorio y debe describir los cambios realizados.

### `log`

Muestra el historial de commits, comenzando por el más reciente.

```bash
./sbac log
```

Para cada commit, se muestra el hash, autor, fecha y mensaje.

### `branch`

Gestiona las ramas del repositorio. Tiene tres sub-comandos:

Crear una rama:

```bash
./sbac branch -c <nombre_de_la_rama> [-s <punto_de_inicio>]
```

Crea una nueva rama. Opcionalmente, puedes especificar un punto de inicio (commit, tag o rama existente) con la opción -s. Si no se especifica, la rama se crea a partir del commit actual.

Ejemplos:

```bash
./sbac branch -c develop (crea una rama llamada "develop" desde el commit actual)
```
```bash      
./sbac branch -c feature1 -s <hash_de_commit> (crea una rama llamada "feature1" desde un commit específico)
```

Eliminar una rama:

```bash
./sbac branch -d <nombre_de_la_rama>
```

Elimina una rama existente. No puedes eliminar la rama "master" ni la rama en la que te encuentras actualmente.

Listar las ramas:

```bash
./sbac branch -l
```
Muestra una lista de todas las ramas disponibles. La rama actual está marcada con un asterisco (*).

### `checkout`

Cambia a una rama, commit o tag específico.

```bash
./sbac checkout <rama|commit|tag>
```
Ejemplos:

```bash
./sbac checkout develop (cambia a la rama "develop")
```
```bash
./sbac checkout <hash_de_commit> (cambia al commit especificado)
```
```bash
./sbac checkout v1.0 (cambia al tag "v1.0")
```
Si cambias a un commit directamente (desvinculando HEAD de una rama), SBAC mostrará un mensaje indicando que HEAD está "detached".

## `tag`

Crea una etiqueta (tag/línea base) para marcar un commit específico.

```bash
./sbac tag <nombre_de_la_etiqueta>
```
Crea una etiqueta en el commit actual.

## `list-tags`

Lista todas las etiquetas disponibles.

```bash
./sbac list-tags
```

## `diff`

Muestra las diferencias entre dos commits.

```bash
./sbac diff <commit1> <commit2>
```

Compara los archivos que se modificaron entre los dos commits. Muestra las líneas añadidas y eliminadas.

## `diff-tags`

Muestra las diferencias entre los commits a los que apuntan dos tags.

```bash
./sbac diff-tags <tag1> <tag2>
```

## Estructura del Repositorio SBAC

El directorio .sbac contiene la siguiente estructura:

objects: Almacena los contenidos de los archivos y los metadatos de los commits en forma de objetos.

refs: Contiene referencias a los commits, como las ramas y los tags.

heads: Contiene archivos, uno por cada rama, que apuntan al último commit en esa rama.

tags: Contiene archivos, uno por cada tag, que apuntan al commit etiquetado.

HEAD: Apunta a la rama actual o a un commit específico.

index: Almacena el estado del área de preparación (staging area).

config: Almacena la configuración del repositorio, como el nombre del autor.

## Limitaciones

SBAC es una implementación simplificada y tiene las siguientes limitaciones:

No soporta ramas remotas.

No soporta merge.

No soporta conflictos.

No soporta la gestión de usuarios y permisos.

No ofrece las mismas optimizaciones de almacenamiento que Git.
