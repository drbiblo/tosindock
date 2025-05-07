import os
import subprocess
from pathlib import Path
import streamlit as st

# Paths to utilities
vina_path = Path("utils/vina")
vina_split_path = Path("utils/vina_split")
prepare_receptor_script = Path("utils/prepare_receptor4.py")

# Make vina and vina_split executable if they exist
if vina_path.exists() and vina_split_path.exists():
    subprocess.run(["chmod", "+x", str(vina_path), str(vina_split_path)])
else:
    st.error("❌ 'vina' or 'vina_split' not found in utils/. Please upload them and make them executable.")

# Upload Ligand
ligand_sdf = st.file_uploader("Upload Ligand (.sdf)", type=["sdf"])
if ligand_sdf:
    with open("ligand.sdf", "wb") as f:
        f.write(ligand_sdf.read())
    st.info("📦 Converting ligand to PDBQT using Open Babel...")
    result = subprocess.run(["obabel", "ligand.sdf", "-O", "ligand.pdbqt"],
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode == 0 and Path("ligand.pdbqt").exists():
        st.success("✅ Ligand converted to PDBQT.")
        with open("ligand.pdbqt", "rb") as f:
            st.download_button("Download Ligand PDBQT", f, "ligand.pdbqt")
    else:
        st.error("❌ Open Babel failed to convert ligand.")
        st.code(result.stderr)

# Upload Protein
protein_pdb = st.file_uploader("Upload Protein (.pdb)", type=["pdb"])
if protein_pdb:
    with open("protein.pdb", "wb") as f:
        f.write(protein_pdb.read())
    st.info("🛠 Preparing protein using MGLTools...")
    if prepare_receptor_script.exists():
        result = subprocess.run(["python2", str(prepare_receptor_script), "-r", "protein.pdb", "-o", "protein.pdbqt"],
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode == 0 and Path("protein.pdbqt").exists():
            st.success("✅ Protein converted to PDBQT.")
            with open("protein.pdbqt", "rb") as f:
                st.download_button("Download Protein PDBQT", f, "protein.pdbqt")
        else:
            st.error("❌ Protein conversion failed.")
            st.code(result.stderr)
    else:
        st.error("❌ prepare_receptor4.py not found in utils/")

# Docking section
if Path("ligand.pdbqt").exists() and Path("protein.pdbqt").exists() and vina_path.exists():
    st.subheader("🚀 Run Docking")
    center_x = st.number_input("Center X", value=0.0)
    center_y = st.number_input("Center Y", value=0.0)
    center_z = st.number_input("Center Z", value=0.0)
    size_x = st.number_input("Size X", value=20.0)
    size_y = st.number_input("Size Y", value=20.0)
    size_z = st.number_input("Size Z", value=20.0)

    if st.button("Start Docking"):
        st.info("⚙️ Running docking with AutoDock Vina...")
        docking_command = [
            str(vina_path),
            "--receptor", "protein.pdbqt",
            "--ligand", "ligand.pdbqt",
            "--center_x", str(center_x),
            "--center_y", str(center_y),
            "--center_z", str(center_z),
            "--size_x", str(size_x),
            "--size_y", str(size_y),
            "--size_z", str(size_z),
            "--out", "docked_output.pdbqt",
            "--log", "docking_log.txt"
        ]

        result = subprocess.run(docking_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        if result.returncode == 0 and Path("docked_output.pdbqt").exists():
            st.success("✅ Docking completed!")
            with open("docked_output.pdbqt", "rb") as f:
                st.download_button("Download Docked Output", f, "docked_output.pdbqt")
            with open("docking_log.txt", "r") as log:
                st.text("📄 Docking Log:\n" + log.read())
        else:
            st.error("❌ Docking failed.")
            st.code(result.stderr)

