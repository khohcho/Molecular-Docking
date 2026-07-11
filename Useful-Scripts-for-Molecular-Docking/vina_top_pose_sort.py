import os
import glob

def parse_vina_logs(directory="."):
    results = []
    # Find all .log files in the directory
    log_files = glob.glob(os.path.join(directory, "*.log"))

    for file_path in log_files:
        filename = os.path.basename(file_path)
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                
            # Find the dashed line where the Vina scoring table starts
            for i, line in enumerate(lines):
                if line.startswith("-----+------------+----------+----------"):
                    # The line immediately after the dashed line is the best pose (Mode 1)
                    if i + 1 < len(lines):
                        top_pose_line = lines[i+1].strip()
                        parts = top_pose_line.split()
                        
                        # The second column in the Vina output is the affinity score
                        if len(parts) >= 2:
                            energy = float(parts[1])
                            results.append((filename, energy))
                    break  # Score found, no need to read the rest of the lines
                    
        except Exception as e:
            print(f"Error: Could not read {filename}. ({e})")

    # Sort the results by energy score (lowest/most negative at the top)
    results.sort(key=lambda x: x[1])
    return results

if __name__ == "__main__":
    # Tabloyu bir metin bloğu olarak hazırlayalım
    output_lines = []
    output_lines.append(f"\n{'Ligand Log File':<35} | {'Best Score (kcal/mol)'}")
    output_lines.append("-" * 65)
    
    sorted_results = parse_vina_logs()
    
    if not sorted_results:
        output_lines.append("No valid Vina .log files found in the directory.")
    else:
        for filename, energy in sorted_results:
            output_lines.append(f"{filename:<35} | {energy:>10.2f}")
            
    output_lines.append("-" * 65)
    output_lines.append(f"A total of {len(sorted_results)} ligands were analyzed.\n")
    
    # Hazırlanan tabloyu tek bir string haline getir
    final_output = "\n".join(output_lines)
    
    # 1. Ekrana (Terminal/PowerShell) yazdır
    print(final_output)
    
    # 2. results.txt dosyasına kaydet
    try:
        with open("results.txt", "w", encoding="utf-8") as f:
            f.write(final_output)
        print(">>> Başarı: Tablo aynı zamanda 'results.txt' dosyasına kaydedildi!")
    except Exception as e:
        print(f">>> Hata: results.txt dosyası oluşturulamadı. ({e})")