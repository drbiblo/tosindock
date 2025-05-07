TosinDock

TosinDock is a lightweight, web-based protein–ligand docking interface powered by AutoDock Vina and built using Streamlit. It is designed for students, biochemists, and researchers with no coding experience to perform docking tasks easily.

Features

• Upload ligand in .sdf and convert to .pdbqt
• Upload protein in .pdb and convert to .pdbqt
• Automatically generate docking box based on the protein size
• Visualize multiple binding poses with an interactive 3D viewer
• Download the following:
 - Top pose as protein–ligand complex in .pdb
 - All poses as individual protein–ligand complexes
 - Original docking log and score table

Technologies Used

Python, Streamlit, AutoDock Vina, Open Babel, Py3Dmol, RDKit, BioPython

Deployment Options

Can be deployed using:
• Streamlit Cloud
• Replit
• A custom Linux server

About the Developer

Created by Tosin — a biochemist and molecular docking enthusiast with a passion for making computational tools accessible to everyone.

Project Structure

litedock/
 ├── app.py (Streamlit app)
 ├── requirements.txt (Python dependencies)
 ├── input/ (File uploads and processed files)
 └── README.txt (This description)

How to Run

Clone the repo:
 git clone https://github.com/drbiblo/tosindock.git

Navigate into the folder:
 cd tosindock

Install requirements:
 pip install -r requirements.txt

Run the app:
 streamlit run app.py

Make sure AutoDock Vina and Open Babel are installed and added to your system’s PATH.

Contact

For feedback, issues, or collaborations, reach out through the GitHub page or inside the Streamlit interface.

TosinDock – Protein–Ligand Docking Made Simple