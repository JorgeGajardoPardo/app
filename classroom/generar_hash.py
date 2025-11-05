from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()

# Cambia esta línea por la contraseña que quieras encriptar
password_plana = "sdo"

# Genera el hash
hash_generado = bcrypt.generate_password_hash(password_plana).decode('utf-8')

print("Hash generado:")
print(hash_generado)
