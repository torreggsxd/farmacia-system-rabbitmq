from getpass import getpass
from werkzeug.security import generate_password_hash


def main():
    contrasena = getpass("Contraseña nueva: ")

    if not contrasena:
        raise SystemExit("La contraseña no puede estar vacía.")

    confirmacion = getpass("Repite la contraseña: ")

    if contrasena != confirmacion:
        raise SystemExit("Las contraseñas no coinciden.")

    print("\nCopia este hash completo en MariaDB:\n")
    print(generate_password_hash(contrasena))


if __name__ == "__main__":
    main()