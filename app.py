from flask import Flask, render_template, request, redirect, url_for, session
import pymysql

from config import *

app = Flask(__name__)
app.secret_key = "chrono_2026"

# =====================================
# LOGIN
# =====================================

@app.route("/", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        correo = request.form["correo"]
        password = request.form["password"]

        try:

            conexion = pymysql.connect(
                host=DB_HOST,
                user=DB_USER,
                password=DB_PASSWORD,
                database=DB_NAME
            )

            cursor = conexion.cursor()

            sql = """
            SELECT
                u.id_usuario,
                u.nombre,
                r.nombre
            FROM usuarios u
            INNER JOIN roles r
                ON u.id_rol = r.id_rol
            WHERE u.correo = %s
            AND u.password = %s
            """

            cursor.execute(sql, (correo, password))

            usuario = cursor.fetchone()

            conexion.close()

            if usuario:

                session["usuario_id"] = usuario[0]
                session["nombre"] = usuario[1]
                session["rol"] = usuario[2]

            rol = usuario[2]

            if rol == "Administrador":
                return redirect(url_for("admin"))

            elif rol == "Planeador":
                    return redirect(url_for("planeador"))

            elif rol == "Coordinador":
                    return redirect(url_for("coordinador"))

            elif rol == "Docente":
                    return redirect(url_for("docente"))

            return "Usuario o contraseña incorrectos"

        except Exception as e:
            return f"Error: {str(e)}"

    return render_template("login.html")


# =====================================
# DASHBOARD ADMINISTRADOR
# =====================================

@app.route("/admin")
def admin():
    return render_template("admin/dashboard.html")


# =====================================
# DASHBOARD PLANEADOR
# =====================================

@app.route("/planeador")
def planeador():
    return render_template("planeador/dashboard.html")


# =====================================
# DASHBOARD COORDINADOR
# =====================================

@app.route("/coordinador")
def coordinador():
    return render_template("coordinador/dashboard.html")


# =====================================
# DASHBOARD DOCENTE
# =====================================

@app.route("/docente")
def docente():
    return render_template("docente/dashboard.html")


# =====================================
# GESTIÓN DE DOCENTES
# =====================================

@app.route("/docentes", methods=["GET", "POST"])
def docentes():

    conexion = pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )

    cursor = conexion.cursor()

    if request.method == "POST":

        numero_empleado = request.form["numero_empleado"]
        nombre = request.form["nombre"]
        apellido_paterno = request.form["apellido_paterno"]
        apellido_materno = request.form["apellido_materno"]
        correo = request.form["correo"]

        sql = """
        INSERT INTO docentes
        (
            numero_empleado,
            nombre,
            apellido_paterno,
            apellido_materno,
            correo_institucional
        )
        VALUES
        (%s,%s,%s,%s,%s)
        """

        cursor.execute(
            sql,
            (
                numero_empleado,
                nombre,
                apellido_paterno,
                apellido_materno,
                correo
            )
        )

        conexion.commit()

    cursor.execute("""
        SELECT
            u.id_usuario,
            u.nombre,
            u.correo,
            u.activo
        FROM usuarios u
        INNER JOIN roles r
            ON u.id_rol = r.id_rol
        WHERE r.nombre = 'Docente'
        ORDER BY u.id_usuario ASC
    """)

    docentes = cursor.fetchall()

    conexion.close()

    return render_template(
        "admin/docentes.html",
        docentes=docentes
    )

# =====================================
# GESTION DE USUARIOS
# =====================================

@app.route("/usuarios", methods=["GET", "POST"])
def usuarios():

    conexion = pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )

    cursor = conexion.cursor()

    if request.method == "POST":

        nombre = request.form["nombre"]
        correo = request.form["correo"]
        password = request.form["password"]
        rol = request.form["rol"]
        activo = request.form["activo"]

        sql = """
        INSERT INTO usuarios
        (
            nombre,
            correo,
            password,
            id_rol,
            activo
        )
        VALUES
        (%s,%s,%s,%s,%s)
        """

        cursor.execute(
            sql,
            (
                nombre,
                correo,
                password,
                rol,
                activo
            )
        )

        conexion.commit()

    cursor.execute("""
        SELECT
            u.id_usuario,
            u.nombre,
            u.correo,
            r.nombre,
            u.activo
        FROM usuarios u
        INNER JOIN roles r
            ON u.id_rol = r.id_rol
        ORDER BY u.id_usuario DESC
    """)

    usuarios = cursor.fetchall()

    cursor.execute("""
        SELECT
            id_rol,
            nombre
        FROM roles
    """)

    roles = cursor.fetchall()

    conexion.close()

    return render_template(
        "admin/usuarios.html",
        usuarios=usuarios,
        roles=roles
    )

@app.route("/editar_usuario/<int:id>", methods=["GET","POST"])
def editar_usuario(id):

    conexion = pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )

    cursor = conexion.cursor()

    if request.method == "POST":

        nombre = request.form["nombre"]
        correo = request.form["correo"]
        activo = request.form["activo"]

        cursor.execute("""
            UPDATE usuarios
            SET nombre=%s,
                correo=%s,
                activo=%s
            WHERE id_usuario=%s
        """,
        (
            nombre,
            correo,
            activo,
            id
        ))

        conexion.commit()

        conexion.close()

        return redirect("/usuarios")

    cursor.execute("""
        SELECT
            id_usuario,
            nombre,
            correo,
            id_rol,
            activo
        FROM usuarios
        WHERE id_usuario=%s
    """,(id,))

    usuario = cursor.fetchone()

    conexion.close()

    return render_template(
        "admin/editar_usuario.html",
        usuario=usuario
    )

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/")

# =====================================
# GESTION DE MATERIAS
# =====================================

@app.route("/materias", methods=["GET", "POST"])
def materias():

    conexion = pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )

    cursor = conexion.cursor()

    if request.method == "POST":

        clave = request.form["clave"]
        nombre = request.form["nombre"]
        horas_teoricas = request.form["horas_teoricas"]
        horas_practicas = request.form["horas_practicas"]
        semestre = request.form["semestre"]

        cursor.execute("""
        INSERT INTO materias
        (
            clave,
            nombre,
            horas_teoricas,
            horas_practicas,
            semestre
        )
        VALUES
        (%s,%s,%s,%s,%s)
        """,
        (
            clave,
            nombre,
            horas_teoricas,
            horas_practicas,
            semestre
        ))

        conexion.commit()

    cursor.execute("""
        SELECT
            id_materia,
            clave,
            nombre,
            horas_teoricas,
            horas_practicas,
            semestre
        FROM materias
        ORDER BY id_materia DESC
    """)

    materias = cursor.fetchall()

    conexion.close()

    return render_template(
        "admin/materias.html",
        materias=materias
    )

# =====================================
# EDITAR MATERIA
# =====================================

@app.route("/editar_materia/<int:id>", methods=["GET", "POST"])
def editar_materia(id):

    conexion = pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )

    cursor = conexion.cursor()

    if request.method == "POST":

        clave = request.form["clave"]
        nombre = request.form["nombre"]
        horas_teoricas = request.form["horas_teoricas"]
        horas_practicas = request.form["horas_practicas"]
        semestre = request.form["semestre"]

        cursor.execute("""
            UPDATE materias
            SET clave=%s,
                nombre=%s,
                horas_teoricas=%s,
                horas_practicas=%s,
                semestre=%s
            WHERE id_materia=%s
        """,
        (
            clave,
            nombre,
            horas_teoricas,
            horas_practicas,
            semestre,
            id
        ))

        conexion.commit()

        conexion.close()

        return redirect("/materias")

    cursor.execute("""
        SELECT
            id_materia,
            clave,
            nombre,
            horas_teoricas,
            horas_practicas,
            semestre
        FROM materias
        WHERE id_materia=%s
    """, (id,))

    materia = cursor.fetchone()

    conexion.close()

    return render_template(
        "admin/editar_materia.html",
        materia=materia
    )

# =====================================
# ELIMINAR MATERIA
# =====================================

@app.route("/eliminar_materia/<int:id>")
def eliminar_materia(id):

    conexion = pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )

    cursor = conexion.cursor()

    cursor.execute("""
        DELETE FROM materias
        WHERE id_materia=%s
    """, (id,))

    conexion.commit()

    conexion.close()

    return redirect("/materias")

# =====================================
# GESTION DE AULAS
# =====================================

@app.route("/aulas", methods=["GET", "POST"])
def aulas():

    conexion = pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )

    cursor = conexion.cursor()

    if request.method == "POST":

        edificio = request.form["edificio"]
        aula = request.form["aula"]
        capacidad = request.form["capacidad"]
        tipo = request.form["tipo"]

        cursor.execute("""
            INSERT INTO aulas
            (
                edificio,
                aula,
                capacidad,
                tipo
            )
            VALUES
            (%s,%s,%s,%s)
        """,
        (
            edificio,
            aula,
            capacidad,
            tipo
        ))

        conexion.commit()

    cursor.execute("""
        SELECT
            id_aula,
            edificio,
            aula,
            capacidad,
            tipo
        FROM aulas
        ORDER BY id_aula DESC
    """)

    aulas = cursor.fetchall()

    conexion.close()

    return render_template(
        "admin/aulas.html",
        aulas=aulas
    )

@app.route("/editar_aula/<int:id>", methods=["GET","POST"])
def editar_aula(id):

    conexion = pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )

    cursor = conexion.cursor()

    if request.method == "POST":

        edificio = request.form["edificio"]
        aula = request.form["aula"]
        capacidad = request.form["capacidad"]
        tipo = request.form["tipo"]

        cursor.execute("""
            UPDATE aulas
            SET edificio=%s,
                aula=%s,
                capacidad=%s,
                tipo=%s
            WHERE id_aula=%s
        """,
        (
            edificio,
            aula,
            capacidad,
            tipo,
            id
        ))

        conexion.commit()

        conexion.close()

        return redirect("/aulas")

    cursor.execute("""
        SELECT
            id_aula,
            edificio,
            aula,
            capacidad,
            tipo
        FROM aulas
        WHERE id_aula=%s
    """,(id,))

    aula = cursor.fetchone()

    conexion.close()

    return render_template(
        "admin/editar_aula.html",
        aula=aula
    )

# =====================================
# INICIO DE LA APP
# =====================================

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )
