import zipfile
import os
from datetime import datetime

def generate_web_app():
    output_dir = "generated_app"
    os.makedirs(output_dir, exist_ok=True)

    # generate files
    generate_dockerfile(output_dir)
    html = generate_html(features)

    with open(f"{output_dir}/index.html", "w") as f:
        f.write(html)

    shutil.copy("model.pkl", f"{output_dir}/model.pkl")
    shutil.copy("features.pkl", f"{output_dir}/features.pkl")
    shutil.copy("app.py", f"{output_dir}/app.py")

    zip_name = f"deployment_app_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"

    with zipfile.ZipFile(zip_name, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(output_dir):
            for file in files:
                full_path = os.path.join(root, file)
                zipf.write(full_path, arcname=os.path.relpath(full_path, output_dir))

    return zip_name
