import streamlit as st
import os
import shutil
import subprocess

st.set_page_config(page_title="Media Processing Pipeline", layout="wide")
st.title("🎛️ Media Pipeline Control & Storage Center")

# Path variables matching our Docker volumes setup
BASE_DATA_DIR = "/app/data"
PC_DOWNLOADS_PATH = os.getenv("PC_DOWNLOADS_DIR", "/downloads")

FOLDERS = {
    "1_zip_input": os.path.join(BASE_DATA_DIR, "1_zip_input"),
    "2_ripper_input": os.path.join(BASE_DATA_DIR, "2_ripper_input"),
    "3_converter_input": os.path.join(BASE_DATA_DIR, "3_converter_input"),
    "4_final_output": os.path.join(BASE_DATA_DIR, "4_final_output"),
    "pc_downloads": PC_DOWNLOADS_PATH
}

# Ensure all workspace folders physically exist
for path in FOLDERS.values():
    os.makedirs(path, exist_ok=True)

# ----------------------------------------------------
# SYSTEM OPERATIONS: Centralized File Routing Functions
# ----------------------------------------------------
def auto_route_files():
    moved_items = []
    for folder_name, folder_path in FOLDERS.items():
        if folder_name == "4_final_output":
            continue
        for file in os.listdir(folder_path):
            if file in [".gitkeep", ".DS_Store"]:
                continue
            file_path = os.path.join(folder_path, file)
            if os.path.isdir(file_path):
                continue
                
            file_lower = file.lower()
            target_folder = None
            
            if file_lower.endswith('.zip'):
                target_folder = "1_zip_input"
            elif file_lower.endswith(('.mkv', '.mp4', '.avi', '.mov')):
                target_folder = "2_ripper_input"
            elif file_lower.endswith(('.sup', '.srt', '.sub', '.ass')):
                target_folder = "3_converter_input"
                
            if target_folder and target_folder != folder_name:
                dest_path = os.path.join(FOLDERS[target_folder], file)
                shutil.move(file_path, dest_path)
                moved_items.append(f"Moved '{file}' from [{folder_name}] -> [{target_folder}]")
    return moved_items

def manual_bulk_route(source_folder_name, target_folder_name):
    source_path = FOLDERS[source_folder_name]
    target_path = FOLDERS[target_folder_name]
    moved_count = 0
    
    if source_folder_name == target_folder_name:
        return -1

    for file in os.listdir(source_path):
        if file in [".gitkeep", ".DS_Store"]:
            continue
        current_file_path = os.path.join(source_path, file)
        destination_file_path = os.path.join(target_path, file)
        if os.path.isfile(current_file_path):
            shutil.move(current_file_path, destination_file_path)
            moved_count += 1
    return moved_count

# ----------------------------------------------------
# UI SECTION 1: Global File Operations (Upload & Bulk Delete)
# ----------------------------------------------------
st.header("🛠️ Storage Management")

with st.expander("🛠️ Storage Management (Upload & Cleanup)", expanded=False):
    upload_col, delete_col = st.columns(2)

    with upload_col:
            st.markdown("### 📥 Local PC Import")
            path_to_watch = FOLDERS["pc_downloads"]
            
            # 1. ALWAYS initialize the list first
            all_found_files = []
            
            # 2. Check if the path exists
            if os.path.exists(path_to_watch):
                # Scan recursively
                for root, dirs, files in os.walk(path_to_watch):
                    for file in files:
                        if not file.startswith('.'):
                            full_path = os.path.join(root, file)
                            relative_path = os.path.relpath(full_path, path_to_watch)
                            all_found_files.append(relative_path)
                
                # 3. Only show UI if files were found
                if all_found_files:
                    selected_files = st.multiselect("Select files to import:", all_found_files)
                    
                    # Filter out the download folder from the target options
                    pipeline_folders = {k: v for k, v in FOLDERS.items() if k != "pc_downloads"}
                    target_folder = st.selectbox(
                        "Import into:", 
                        list(pipeline_folders.keys()),
                        format_func=lambda x: x.replace('_', ' ').title()
                    )
                    
                    if st.button("🚀 Fast Import (Move)", type="primary", use_container_width=True):
                        for rel_p in selected_files:
                            src = os.path.join(path_to_watch, rel_p)
                            filename = os.path.basename(rel_p) 
                            dest = os.path.join(FOLDERS[target_folder], filename)
                            
                            if os.path.exists(src):
                                shutil.move(src, dest)
                        st.success(f"Moved {len(selected_files)} items.")
                        st.rerun()
                else:
                    st.info(f"No files found in {path_to_watch}")
            else:
                st.error(f"Directory {path_to_watch} not found. Check Docker volume mapping.")
                
    with delete_col:
        st.markdown("### 🧹 Bulk Cleanup")
        
        target_del_folder = st.selectbox("Select folder to clean:", list(FOLDERS.keys()), key="bulk_del_selector")
        
        # 1. Get the list of files
        all_del_files = os.listdir(FOLDERS[target_del_folder])
        clean_del_files = [f for f in all_del_files if f not in [".gitkeep", ".DS_Store"]]
        
        # 2. Add "Select All" checkbox
        select_all = st.checkbox(f"Select all {len(clean_del_files)} files", key=f"all_{target_del_folder}")
        
        # 3. Multiselect logic
        if select_all:
            selected_to_delete = st.multiselect("Files to remove:", clean_del_files, default=clean_del_files)
        else:
            selected_to_delete = st.multiselect("Files to remove:", clean_del_files)
        
        # 4. Action Button
        if st.button("Delete Selected Items", type="secondary", use_container_width=True):
            if selected_to_delete:
                for file_to_del in selected_to_delete:
                    # Extra fail-safe check
                    if file_to_del != ".gitkeep":
                        file_path = os.path.join(FOLDERS[target_del_folder], file_to_del)
                        if os.path.exists(file_path):
                            os.remove(file_path)
                
                st.success(f"Successfully deleted {len(selected_to_delete)} files.")
                st.rerun()
            else:
                st.info("No files selected for deletion.")

st.markdown("---")

# ----------------------------------------------------
# UI SECTION 2: File Location Explorer & Smart Routing
# ----------------------------------------------------
st.header("📂 Real-time File Location & Organizer")

# Automation trigger row
col_btn1, _ = st.columns([2, 3])
with col_btn1:
    if st.button("🤖 Run Auto-Smart Router", type="secondary", help="Sorts files by extension instantly"):
        actions_taken = auto_route_files()
        if actions_taken:
            st.success(f"Successfully auto-routed {len(actions_taken)} files!")
            st.rerun()
        else:
            st.info("Everything is already in the correct service folder.")

st.markdown("##")
pipeline_folders = {k: v for k, v in FOLDERS.items() if k != "pc_downloads"}

# Render 4 column layout tracking physical media locations
cols = st.columns(len(pipeline_folders))
for idx, (folder_name, folder_path) in enumerate(pipeline_folders.items()):
    with cols[idx]:
        st.subheader(f"{folder_name.replace('_', ' ').title()}")
        
        # Get list of clean files (filtering out system files from the UI list view)
        all_files = os.listdir(folder_path)
        visible_files = [f for f in all_files if f not in [".gitkeep", ".DS_Store"] and os.path.isfile(os.path.join(folder_path, f))]
        
        # Render the physical file list
        if visible_files:
            st.caption(f"Count: {len(visible_files)} items")
            for f in visible_files:
        # Create a small grid for the filename and a delete button
                file_col, del_col = st.columns([0.85, 0.15])
                file_col.text(f"📄 {f}")
                if del_col.button("🗑️", key=f"quick_del_{folder_name}_{f}"):
                    os.remove(os.path.join(folder_path, f))
                    st.rerun()
        else:
            st.markdown("*Folder is empty*")
            
        st.markdown(" ")
        
        # --- FIXED UI: Manual Tools Panel is OUTSIDE the "if visible_files" block ---
        # This guarantees it's always visible on screen!
        with st.expander("💼 Manual Folder Tools", expanded=True):
            destination = st.selectbox("Target Destination", list(FOLDERS.keys()), key=f"dest_{folder_name}", index=min(idx+1, 3))
            
            # Single file moving dropdown configuration
            if visible_files:
                selected_file = st.selectbox("Select file", visible_files, key=f"sel_{folder_name}")
                if st.button("Move Selected File", key=f"btn_single_{folder_name}", use_container_width=True):
                    shutil.move(os.path.join(folder_path, selected_file), os.path.join(FOLDERS[destination], selected_file))
                    st.rerun()
            else:
                st.caption("No individual files to move")
                
            st.markdown("---")
            
            # Bulk migration trigger
            if st.button("🚨 Empty all items to target", key=f"btn_all_{folder_name}", use_container_width=True):
                total_moved = manual_bulk_route(folder_name, destination)
                if total_moved == -1:
                    st.error("Source and destination cannot be identical.")
                elif total_moved > 0:
                    st.success(f"Migrated {total_moved} files safely!")
                    st.rerun()
                else:
                    st.warning("No files found to migrate.")

st.markdown("---")


# ----------------------------------------------------
# UI SECTION 3: Dynamic Execution Switchboard
# ----------------------------------------------------
st.header("⚙️ Pipeline Execution Control")

col_left, col_right = st.columns(2)
with col_left:
    st.markdown("### 1. Choose Stages")
    run_extractor = st.checkbox("🔄 Step 1: Extract Zip Files", value=False)
    run_ripper = st.checkbox("✂️ Step 2: Subtitle Ripper", value=False)
    run_converter = st.checkbox("🔤 Step 3: SUP to SRT Converter", value=False)
    run_renamer = st.checkbox("✍️ Step 4: Media Renamer", value=False)

with col_right:
    st.markdown("### 2. Properties Settings")
    file_type = st.text_input("Extractor Filter (e.g. mkv)", value="mkv", disabled=not run_extractor)
    name_prefix = st.text_input("Series Name Prefix", value="MyShow", disabled=not run_renamer)
    default_season = st.number_input("Default Season", min_value=1, value=2, step=1, disabled=not run_renamer)
    language = st.selectbox("Language Mapping", ["en", "no", "de", "fr", "es"], index=0, disabled=not (run_converter or run_renamer))

if st.button("🚀 Execute Selected Pipeline Steps", type="primary", use_container_width=True):
    if not any([run_extractor, run_ripper, run_converter, run_renamer]):
        st.warning("Please choose at least one step above before clicking run.")
    else:
        status_area = st.empty()
        
        if run_extractor:
            status_area.info("Processing step 1: Extracting...")
            env_vars = {**os.environ, "FILE_TYPE": file_type, "INPUT_DIR": FOLDERS["1_zip_input"], "OUTPUT_DIR": FOLDERS["2_ripper_input"]}
            res = subprocess.run(["python", "/app/file_extractor/extract_script.py"], capture_output=True, text=True, env=env_vars)
            st.code(res.stdout)
            if res.stderr: st.error(res.stderr)
            
        if run_ripper:
            status_area.info("Processing step 2: Ripping titles...")
            env_vars = {**os.environ, "INPUT_DIR": FOLDERS["2_ripper_input"], "OUTPUT_DIR": FOLDERS["3_converter_input"]}
            res = subprocess.run(["python", "/app/sub_ripper/ripper_script.py"], capture_output=True, text=True, env=env_vars)
            st.code(res.stdout)
            if res.stderr: st.error(res.stderr)

        if run_converter:
            status_area.info("Processing step 3: Converting tracks...")
            env_vars = {
                **os.environ, 
                "IMPORT_DIR": FOLDERS["3_converter_input"], 
                "OUTPUT_DIR": FOLDERS["4_final_output"],
                "LANGUAGE": language  # <-- Added language forwarding here
            }
            res = subprocess.run(["python", "/app/sup_srt_converter/converter_script.py"], capture_output=True, text=True, env=env_vars)
            st.code(res.stdout)
            if res.stderr: st.error(res.stderr)

        if run_renamer:
            status_area.info("Processing step 4: Renaming items...")
            env_vars = {
                **os.environ, 
                "TARGET_DIR": FOLDERS["4_final_output"], 
                "NAME_PREFIX": name_prefix, 
                "DEFAULT_SEASON": str(default_season), 
                "LANGUAGE": language,
                "PYTHONPATH": "/app/media_renamer"
            }
            res = subprocess.run(["python", "/app/media_renamer/renamer_script.py"], cwd="/app/media_renamer", env=env_vars, capture_output=True, text=True)
            st.code(res.stdout)
            if res.stderr: st.error(res.stderr)

        status_area.success("Selected operations executed successfully!")
        st.rerun()