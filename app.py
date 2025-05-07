import streamlit as st
import os
import subprocess
from pathlib import Path
import py3Dmol
from Bio.PDB import PDBParser
from streamlit.components.v1 import html
import glob

st.set_page_config(layout="wide")
st.title("🧬 LiteDock - Enhanced Protein-Ligand Docking App")

Path("input").mkdir(exist_ok=True)

if "docking_done" not in st.session_state:
    st.session_state.docking_done = False

# Ensure vina and prepare_receptor exist
vina_path = Path("utils/vina")
vina_split_path = Path("utils/vina_split")
prepare_receptor_script = Path("utils/prepare_receptor4.py")

for path in [vina_path, vina_split_path]:
    if path.exists():
        subprocess.run(["chmod", "+x", str(path)])
    else:
        st.error(f"❌ Required file missing: {path}")

# Step 1: Ligand Conversion
st.header("Step 1: Upload Ligand (.sdf) → Convert to PDBQT")
ligand_sdf = st.file_uploader("Upload Ligand File (.sdf)", type=["sdf"])
if ligand_sdf:
    ligand_input = "input/ligand_input.sdf"
    ligand_output = "input/ligand_converted.pdbqt"
    with open(ligand_input, "wb") as f:
        f.write(ligand_sdf.read())
    st.success("✅ Ligand .sdf uploaded!")
    if st.button("Convert Ligand to PDBQT"):
        with st.spinner("Converting ligand using Open Babel..."):
            result = subprocess.run(["obabel", ligand_input, "-O", ligand_output, "--gen3d"],
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if result.returncode == 0 and Path(ligand_output).exists():
                with open(ligand_output, "rb") as f:
                    st.download_button("Download Ligand PDBQT", f, "ligand_converted.pdbqt")
                st.success("✅ Ligand conversion successful!")
            else:
                st.error("❌ Ligand conversion failed.")
                st.code(result.stderr)

# Step 2: Protein Conversion
st.header("Step 2: Upload Protein (.pdb) → Convert to PDBQT (MGLTools)")
protein_pdb = st.file_uploader("Upload Protein File (.pdb)", type=["pdb"])
if protein_pdb:
    protein_input = "input/protein_input.pdb"
    protein_output = "input/protein_converted.pdbqt"
    with open(protein_input, "wb") as f:
        f.write(protein_pdb.read())
    st.success("✅ Protein .pdb uploaded!")
    if st.button("Convert Protein to PDBQT"):
        with st.spinner("Running MGLTools receptor preparation..."):
            if prepare_receptor_script.exists():
                result = subprocess.run(["python2", str(prepare_receptor_script), "-r", protein_input, "-o", protein_output, "-A", "hydrogens"],
                                        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                if result.returncode == 0 and Path(protein_output).exists():
                    with open(protein_output, "rb") as f:
                        st.download_button("Download Protein PDBQT", f, "protein_converted.pdbqt")
                    st.success("✅ Protein conversion successful!")
                else:
                    st.error("❌ Protein conversion failed.")
                    st.code(result.stderr)
            else:
                st.error("❌ Missing prepare_receptor4.py in utils/")

# Step 3: Docking
st.header("Step 3: Upload Converted Files and Run Docking")
ligand_pdbqt = st.file_uploader("Upload Converted Ligand (.pdbqt)", type=["pdbqt"], key="ligand_final")
protein_pdbqt = st.file_uploader("Upload Converted Protein (.pdbqt)", type=["pdbqt"], key="protein_final")

if ligand_pdbqt and protein_pdbqt:
    ligand_final = "input/final_ligand.pdbqt"
    protein_final = "input/final_protein.pdbqt"
    with open(ligand_final, "wb") as f:
        f.write(ligand_pdbqt.read())
    with open(protein_final, "wb") as f:
        f.write(protein_pdbqt.read())

    st.subheader("📍 Automatically Generating Docking Box")
    parser = PDBParser(QUIET=True)
    structure = parser.get_structure("protein", "input/protein_input.pdb")
    coords = [atom.coord for atom in structure.get_atoms()]
    xs, ys, zs = zip(*coords)
    cx, cy, cz = sum(xs)/len(xs), sum(ys)/len(ys), sum(zs)/len(zs)
    sx, sy, sz = max(xs)-min(xs)+10, max(ys)-min(ys)+10, max(zs)-min(zs)+10

    st.write(f"Center: ({cx:.2f}, {cy:.2f}, {cz:.2f})")
    st.write(f"Size: x={sx:.2f}, y={sy:.2f}, z={sz:.2f}")

    st.subheader("📦 Docking Grid Preview")
    with open("input/protein_input.pdb") as f:
        pdb_text = f.read()
    view = py3Dmol.view(width=700, height=500)
    view.addModel(pdb_text, "pdb")
    view.setStyle({"cartoon": {"color": "spectrum"}})
    view.addBox({"center": {"x": cx, "y": cy, "z": cz}, "dimensions": {"w": sx, "h": sy, "d": sz}, "color": "red", "opacity": 0.3})
    view.zoomTo()
    html(view._make_html(), height=500)

    if st.button("🚀 Run Docking"):
        output_pdbqt = "input/docked_output.pdbqt"
        log_file = "input/docking_log.txt"
        subprocess.run([
            str(vina_path),
            "--receptor", protein_final,
            "--ligand", ligand_final,
            "--center_x", str(cx), "--center_y", str(cy), "--center_z", str(cz),
            "--size_x", str(sx), "--size_y", str(sy), "--size_z", str(sz),
            "--out", output_pdbqt, "--log", log_file
        ], check=True)
        st.session_state.docking_done = True

if st.session_state.docking_done:
    subprocess.run([str(vina_split_path), "--input", "input/docked_output.pdbqt", "--ligand", "input/pose_out"], check=True)
    pose_files = sorted(glob.glob("input/pose_out*.pdbqt"))
    if not pose_files:
        st.error("❌ No poses were generated by vina_split.")
    else:
        st.info(f"🔢 {len(pose_files)} binding poses detected.")
        st.subheader("📄 Vina Log Output")
        with open("input/docking_log.txt") as f:
            for line in f.readlines():
                st.text(line.strip())
        st.subheader("📊 Binding Scores Table")
        scores = []
        for line in open("input/docking_log.txt"):
            if "REMARK VINA RESULT:" in line:
                parts = line.split()
                if len(parts) > 3:
                    scores.append(float(parts[3]))
        for i, score in enumerate(scores):
            st.write(f"Pose {i+1}: {score} kcal/mol")

        st.subheader("🔬 Binding Poses Viewer")
        selected_pose_index = st.selectbox("Select Pose", list(range(1, len(pose_files)+1)))
        selected_file = pose_files[selected_pose_index - 1]

        with open("input/final_protein.pdbqt") as f:
            prot = f.read()
        with open(selected_file) as f:
            lig = f.read()

        view = py3Dmol.view(width=700, height=500)
        view.addModel(prot, "pdbqt")
        view.setStyle({"cartoon": {"color": "spectrum"}})
        view.addModel(lig, "pdbqt")
        view.setStyle({"model": 1}, {"stick": {}, "sphere": {"scale": 0.3}})
        view.zoomTo()
        html(view._make_html(), height=500)

        st.subheader("📥 Download Docked Complexes")
        combined_dir = "input/complex_poses"
        os.makedirs(combined_dir, exist_ok=True)
        combined_files = []
        for i, pose_file in enumerate(pose_files):
            complex_out = os.path.join(combined_dir, f"complex_pose_{i+1}.pdb")
            with open(complex_out, "w") as fout:
                fout.write(open("input/protein_input.pdb").read())
                fout.write(open(pose_file).read())
            combined_files.append(complex_out)

        zip_path = "input/all_complex_poses.zip"
        subprocess.run(["zip", "-j", zip_path] + combined_files)
        with open(zip_path, "rb") as f:
            st.download_button("📦 Download All Complex Poses (ZIP)", f, "all_complex_poses.zip")

        top_pose = pose_files[0]
        combined_pdbqt = "input/top_complex_pose.pdbqt"
        with open("input/final_protein.pdbqt") as fprot, open(top_pose) as flig, open(combined_pdbqt, "w") as fout:
            fout.write(fprot.read())
            fout.write(flig.read())

        top_complex_pdb = "input/top_complex_pose.pdb"
        subprocess.run(["obabel", combined_pdbqt, "-O", top_complex_pdb], check=True)
        with open(top_complex_pdb, "rb") as f:
            st.download_button("🏆 Download Top Pose Complex (PDB)", f, "top_pose_complex.pdb")
