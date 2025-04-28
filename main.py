from database import create_database, remove_duplicates

if __name__ == "__main__":
    create_database()
    remove_duplicates()
    print("База готова — можно запускать import/update.")
