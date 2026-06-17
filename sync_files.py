import os
import shutil

# List of apps to mirror
APPS = ['clientes', 'facturas', 'materia_prima', 'pedidos', 'productos', 'proveedores', 'reportes', 'reservas', 'usuarios', 'static', 'templates']

def sync_file(rel_path):
    rel_path = rel_path.replace('\\', '/')
    src = os.path.join(os.getcwd(), rel_path)
    if not os.path.isfile(src):
        print(f"Source file does not exist: {src}")
        return

    # Mirror to MATPI/[rel_path]
    dest1 = os.path.join(os.getcwd(), 'MATPI', rel_path)
    os.makedirs(os.path.dirname(dest1), exist_ok=True)
    shutil.copy2(src, dest1)
    print(f"Synced to {os.path.relpath(dest1)}")

    # Mirror to MATPI/MATPI/[rel_path]
    dest2 = os.path.join(os.getcwd(), 'MATPI', 'MATPI', rel_path)
    os.makedirs(os.path.dirname(dest2), exist_ok=True)
    shutil.copy2(src, dest2)
    print(f"Synced to {os.path.relpath(dest2)}")

def sync_all_in_dir(rel_dir):
    abs_dir = os.path.join(os.getcwd(), rel_dir)
    if not os.path.isdir(abs_dir):
        return
    for root, _, files in os.walk(abs_dir):
        for f in files:
            full_path = os.path.join(root, f)
            rel_path = os.path.relpath(full_path, os.getcwd())
            # Skip if already inside MATPI
            if rel_path.startswith('MATPI'):
                continue
            sync_file(rel_path)

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        for arg in sys.argv[1:]:
            sync_file(arg)
    else:
        print("Please specify relative file path to sync, or run with specific files.")
