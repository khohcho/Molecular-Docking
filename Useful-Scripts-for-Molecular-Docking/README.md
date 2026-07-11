These scripts handle the critical pre-docking phase, ensuring partial charges are preserved and atom types are correctly assigned for force-field compatibility.

**`prepare_ligands.py`**
* **What it does:** A CLI wrapper for the AutoDockTools (ADT) engine. It converts bulk `.mol2` libraries to `.pdbqt` format without opening the ADT graphical interface.
* **Key Advantage:** Strictly preserves existing quantum partial charges (e.g., from Maestro or ESP calculations) by bypassing default Gasteiger recalculations, while correctly merging non-polar hydrogens.
* **Customization (MGLTools Flags):** Run via terminal. You can modify the `adt_python` and `adt_script` paths inside the file to point to your local MGLTools installation. By default, the script uses the `"-C", "-A checkhydrogens", "-U nphs_lps"` flags to preserve your custom charges. If you wish to calculate standard Gasteiger charges instead, you can simply remove the `-C` flag inside the script.
* **Other Useful Flags You Can Modify in the Script:**
  * `-C`: Do not add charges (Removes this to calculate Gasteiger charges automatically).
  * `-A`: Type of repairs to make (e.g., `bonds_hydrogens`, `checkhydrogens`, or `None`).
  * `-U`: Cleanup type (e.g., `nphs_lps` to merge non-polar hydrogens and lone pairs, which is standard for Vina/AD-GPU).
  * `-p`: Preserve input charges on a specific atom type (e.g., `-p Zn`).

**`detect_atom_types.py`**
* **What it does:** Scans an entire directory of `.pdbqt` ligands and extracts every unique atom type present in the dataset.
* **Key Advantage:** Essential for AutoDock-GPU users. Before running AD-GPU, you must generate a `.dpf` (Docking Parameter File) template that explicitly lists all atom types. Missing a single atom type in a massive library causes a fatal runtime error. This script prevents that crash by giving you the exact atom type array to paste into your `.dpf`.

**`fix_linear_groups.py`**
* **What it does:** Fixes geometric topology errors in rigid linear pharmacophores (like azido groups or alkynes).
* **Key Advantage:** Standard parameterization often misassigns atom types in linear groups, causing them to bend unnaturally during simulations. This script geometrically detects linear structures (distance < 1.65 Å) and strictly enforces the correct `NA - N - NA` typings to preserve structural rigidity.
* **Customization:** You can modify `CENTER_ATOM_TYPE`, `FLANKING_ATOM_TYPE`, and `DISTANCE_TOLERANCE` at the top of the script to target different linear chemical groups.

---

## Post-Docking Geometric Filters

Standard scoring functions (binding affinity) often rank poses highly even if they bind in irrelevant regions of the active site. These scripts filter `.pdbqt` outputs based on absolute 3D spatial geometry, ensuring the ligand is exactly where it needs to be (e.g., near a catalytic residue or metal cofactor).

**Configuration Note for All Filters:** Before running these scripts, open them in a text editor and modify the following core variables to match your specific protein-ligand system:
* `PRIMARY_TARGET_COORDS`: The X, Y, Z coordinates of your catalytic center (e.g., a reactive nucleophile or Mg2+ ions).
* `ANCHOR_ATOM_TYPE`: The atomic symbol of your ligand's reactive warhead or key pharmacophore (e.g., `"P"`, `"S"`, `"F"`).
* `THRESHOLDS`: A list of acceptable distance limits (in Ångströms) between the anchor and the target.

**`pose_filter_basic.py`**
* **What it does:** Scans all docking outputs and isolates poses where the designated `ANCHOR_ATOM` is located within the defined spatial threshold of the `PRIMARY_TARGET_COORDS`.
* **Use Case:** Discarding "false positive" high-scoring ligands that failed to reach the deepest part of the binding pocket.
* **Output Limit:** Automatically generates a report of the top 50 valid poses (configurable via `BASE_TOP_N`) that satisfy the criteria, regardless of whether multiple poses belong to the same ligand.

**`pose_filter_unique.py`**
* **What it does:** Similar to the basic filter, but prevents data redundancy. It yields only the top-scoring unique ligand scaffolds that meet the distance constraints (ignoring alternative poses of the same ligand once one passes).
* **Output Limit:** Continues scanning the ranked docking results until it successfully identifies exactly 50 *unique* ligands (configurable via `TOP_N_UNIQUE`), ensuring maximum scaffold diversity in your final selection. Automatically extracts and copies the successful `.pdbqt` files into a new directory.

**`pose_filter_multitarget.py`**
* **What it does:** The most rigorous dual-constraint filter. It validates that the pose satisfies the primary anchor distance and successfully projects a secondary functional group into an adjacent sub-pocket or allosteric site.
* **Customization:** Requires configuring `SECONDARY_TARGET_COORD` and `SECONDARY_THRESH` inside the script to define the secondary spatial constraint.
* **Output Limit:** Features a built-in toggle (`ONLY_UNIQUE_LIGANDS` and `TOP_N_LIMIT`). You can configure it to either extract *every* valid pose that hits both targets, or strictly limit the output to the top 50 unique ligand scaffolds. Automatically extracts and copies the successful `.pdbqt` files into a new directory.

**`sort.py`**
This script automatically scans the current directory for Vina-GPU output files (`.log`), extracts the best binding affinity scores (Mode 1), and sorts the results from the lowest (best) to highest energy. It prints a clean table to the terminal and simultaneously saves it as a `results.txt` file in the same directory.

**Note:** If you are using standard AutoDock Vina instead of Vina-GPU, your output files might be saved with a `.txt` extension. In that case, simply open the Python script and change the `*.log` extension to `*.txt` in the search parameters.
