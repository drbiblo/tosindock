import os
import subprocess
from pathlib import Path
import streamlit as st

# Set Streamlit page config
st.set_page_config(layout="wide")
st.title("🧬 LiteDock - Enhanced Protein-Ligand Docking App")

# Create required folders
Path("input").mkdir(exist_ok=True)
Path("output").mkdir(exist_ok=True)
Path("utils").mkdir(exist_ok=True)

# 1. Download vina and vina_split binaries if not present
vina_url = "https://github.com/ccsb-scripps/AutoDock-Vina/releases/download/v1.2.5/vina_1.2.5_linux_x86_64.tar.gz"
vina_tar = "utils/vina.tar.gz"

if not Path("utils/vina").exists():
    st.info("📥 Downloading AutoDock Vina...")
    subprocess.run(["wget", vina_url, "-O", vina_tar])
    subprocess.run(["tar", "-xzf", vina_tar, "-C", "utils"])
    subprocess.run(["chmod", "+x", "utils/vina", "utils/vina_split"])

# 2. Download MGLTools Linux version and extract python2.7 & script
mgl_python = "utils/mgltools/MGLToolsPckgs/AutoDockTools/Utilities24/prepare_receptor4.py"
mgl_dir = "utils/mgltools"

if not Path(mgl_python).exists():
    st.info("📥 Downloading MGLTools...")
    subprocess.run(["wget", "https://files.docking.org/mgltools/mgltools_x86_64Linux2_1.5.7.tar.gz", "-O", "utils/mgltools.tar.gz"])
    subprocess.run(["tar", "-xzf", "utils/mgltools.tar.gz", "-C", "utils"])
    subprocess.run(["chmod", "+x", f"{mgl_dir}/bin/python2.7"])

# 3. Upload ligand (SDF)
ligand_file = st.file_uploader("Upload Ligand (.sdf)", type=["sdf"])
if ligand_file:
    ligand_path = os.path.join("input", ligand_file.name)
    with open(ligand_path, "wb") as f:
        f.write(ligand_file.read())
    
    st.success(f"Ligand {ligand_file.name} uploaded.")

    # Convert ligand to PDBQT using Open Babel
    ligand_pdbqt = ligand_path.replace(".sdf", ".pdbqt")
    try:
        st.info("⚙️ Converting ligand using Open Babel...")
        result = subprocess.run(["obabel", ligand_path, "-O", ligand_pdbqt], capture_output=True, text=True)
        if result.returncode != 0:
            st.error("❌ Open Babel conversion failed.")
            st.code(result.stderr)
        else:
            st.success("✅ Ligand converted to PDBQT.")
            with open(ligand_pdbqt, "rb") as f:
                st.download_button("Download Ligand PDBQT", f, file_name=os.path.basename(ligand_pdbqt))
    except Exception as e:
        st.error(f"Open Babel crashed: {e}")

# 4. Upload protein (PDB)
protein_file = st.file_uploader("Upload Protein (.pdb)", type=["pdb"])
if protein_file:
    protein_input = os.path.join("input", protein_file.name)
    with open(protein_input, "wb") as f:
        f.write(protein_file.read())

    st.success(f"Protein {protein_file.name} uploaded.")

    protein_output = protein_input.replace(".pdb", ".pdbqt")
    prep_script = os.path.join(mgl_dir, "MGLToolsPckgs/AutoDockTools/Utilities24/prepare_receptor4.py")
    try:
        st.info("⚙️ Converting protein using MGLTools...")
        subprocess.run(
            [f"{mgl_dir}/bin/python2.7", prep_script, "-r", protein_input, "-o", protein_output],
            check=True
        )
        st.success("✅ Protein converted to PDBQT.")
        with open(protein_output, "rb") as f:
            st.download_button("Download Protein PDBQT", f, file_name=os.path.basename(protein_output))
    except Exception as e:
        st.error(f"❌ Protein conversion failed.")
        st.code(str(e))
