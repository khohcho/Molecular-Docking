import os
import glob

def parse_all_vina_poses(directory="."):
    results = []
    # Find all .log files in the directory
    log_files = glob.glob(os.path.join(directory, "*.log"))

    for file_path in log_files:
        filename = os.path.basename(file_path)
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                
            table_started = False
            
            # Find the dashed line where the Vina scoring table starts
            for line in lines:
                if line.startswith("-----+------------+----------+----------"):
                    table_started = True
                    continue  # Move to the next line where the actual data starts
                
                # If we are inside the table, extract all poses
                if table_started:
                    stripped_line = line.strip()
                    
                    # If we hit an empty line, the table is finished
                    if not stripped_line:
                        break
                    
                    parts = stripped_line.split()
                    
                    # Ensure the line has data and starts with a pose (mode) number
                    if len(parts) >= 2 and parts[0].isdigit():
                        mode = int(parts[0])
                        energy = float(parts[1])
                        # Append a tuple containing filename, mode, and energy
                        results.append((filename, mode, energy))
                        
        except Exception as e:
            print(f"Error: Could not read {filename}. ({e})")

    # Sort the global results by energy score (lowest/most negative at the top)
    results.sort(key=lambda x: x[2])
    return results

if __name__ == "__main__":
    # Prepare the output as a text block
    output_lines = []
    output_lines.append(f"\n{'Ligand Log File':<35} | {'Mode':<6} | {'Score (kcal/mol)'}")
    output_lines.append("-" * 65)
    
    sorted_results = parse_all_vina_poses()
    
    if not sorted_results:
        output_lines.append("No valid Vina .log files found in the directory.")
    else:
        # Unpack the 3 elements: filename, mode, and energy
        for filename, mode, energy in sorted_results:
            output_lines.append(f"{filename:<35} | {mode:<6} | {energy:>14.2f}")
            
    output_lines.append("-" * 65)
    output_lines.append(f"A total of {len(sorted_results)} poses were extracted and sorted.\n")
    
    # Join all lines into a single string
    final_output = "\n".join(output_lines)
    
    # 1. Print to the Terminal/PowerShell
    print(final_output)
    
    # 2. Save to results.txt
    try:
        with open("results.txt", "w", encoding="utf-8") as f:
            f.write(final_output)
        print(">>> Success: The global leaderboard has been saved to 'results.txt'!")
    except Exception as e:
        print(f">>> Error: Could not create results.txt file. ({e})")