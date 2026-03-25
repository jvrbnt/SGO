from database import LocalSession
import models

def seed_demo_users():
    db = LocalSession()
    try:
        print("--- Cargando Usuarios de Prueba ---")
        # 1. Técnico de prueba
        if not db.query(models.Technician).filter(models.Technician.email == "admin@mina.es").first():
            admin = models.Technician(
                first_name="Javier",
                last_name="Admin",
                email="admin@mina.es",
                hashed_password="admin", 
                profile_picture="https://cdn-icons-png.flaticon.com/512/4086/4086679.png"
            )
            db.add(admin)

        # 2. Cliente de prueba
        if not db.query(models.Client).filter(models.Client.email == "cliente@csic.es").first():
            cliente = models.Client(
                first_name="Miguel",
                last_name="Investigador",
                email="cliente@csic.es",
                hashed_password="password123",
                entity="CSIC",
                profile_picture="https://static.vecteezy.com/system/resources/thumbnails/021/353/308/small/user-icon-for-website-and-mobile-apps-png.png"
            )
            db.add(cliente)
        
        db.commit()
        print("ÉXITO: Usuarios demo cargados (sin tocar el catálogo).")
    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_demo_users()