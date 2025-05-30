#!/usr/bin/env python3
"""
Complete Timed Workflow Runner
Shows accurate timing for the entire process
"""

import subprocess
import time
from datetime import datetime
import os
from pathlib import Path


def run_command(cmd, description):
    """Run a command and return timing info"""
    print(f"\n{'='*60}")
    print(f"Step: {description}")
    print(f"{'='*60}")
    
    start_time = time.time()
    start_dt = datetime.now()
    
    print(f"Started at: {start_dt.strftime('%H:%M:%S.%f')[:-3]}")
    print(f"Command: {cmd}\n")
    
    # Run the command
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    end_time = time.time()
    end_dt = datetime.now()
    duration = end_time - start_time
    
    print(f"\nCompleted at: {end_dt.strftime('%H:%M:%S.%f')[:-3]}")
    print(f"Duration: {duration:.2f} seconds")
    
    if result.returncode != 0:
        print(f"ERROR: {result.stderr}")
    else:
        # Extract key info from output
        if "rows" in result.stdout:
            for line in result.stdout.split('\n'):
                if "rows" in line or "Coverage:" in line or "Output:" in line:
                    print(f"  → {line.strip()}")
    
    return duration, result.returncode == 0


def main():
    """Run the complete workflow with timing"""
    
    # Change to project root directory (two levels up from orchestration/)
    project_dir = Path(__file__).parent.parent.parent
    os.chdir(project_dir)
    
    print("\n" + "="*60)
    print("COMPLETE MEDIA PLAN WORKFLOW - TIMED EXECUTION")
    print("="*60)
    print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    total_start = time.time()
    
    # Create output directory
    output_dir = "output/timed_workflow_test"
    os.makedirs(output_dir, exist_ok=True)
    
    # Step 1: Protect Template (Optional - skip if not needed)
    print("\n📋 STEP 1: PROTECT EXCEL TEMPLATE (SKIPPING - Using unprotected template)")
    duration1 = 0
    success1 = True
    print("⚠️ Note: Template protection step skipped. Using unprotected template for workflow.")
    
    # Step 2: Extract Data
    print("\n📊 STEP 2: EXTRACT DATA FROM EXCEL FILES")
    cmd2 = f"""python3 production_workflow/01_data_extraction/extract_and_combine_data.py \
        --planned input/PLANNED_INPUT_TEMPLATE_*.xlsx \
        --delivered input/DELIVERED_INPUT_TEMPLATE_*.xlsx \
        --output {output_dir}/ \
        --combine"""
    duration2, success2 = run_command(cmd2, "Extract and Combine Data")
    
    if not success2:
        print("❌ Data extraction failed!")
        return
    
    # Step 3: Map to Template
    print("\n🗺️ STEP 3: MAP DATA TO OUTPUT TEMPLATE")
    # Find the combined file
    import glob
    combined_files = glob.glob(f"{output_dir}/COMBINED_*.xlsx")
    if not combined_files:
        print("❌ No COMBINED file found!")
        return
    
    cmd3 = f"""python3 production_workflow/03_template_mapping/map_to_template.py \
        --input {combined_files[0]} \
        --template input/OUTPUT_TEMPLATE_FILE_EMPTY_FILE.xlsx \
        --output {output_dir}/final_mapped_output.xlsx"""
    duration3, success3 = run_command(cmd3, "Map to Template")
    
    if not success3:
        print("❌ Template mapping failed!")
        return
    
    # Total time
    total_duration = time.time() - total_start
    
    print("\n" + "="*60)
    print("WORKFLOW COMPLETE - TIMING SUMMARY")
    print("="*60)
    print(f"Step 1 - Protect Template:    {duration1:6.2f} seconds")
    print(f"Step 2 - Extract Data:        {duration2:6.2f} seconds")
    print(f"Step 3 - Map to Template:     {duration3:6.2f} seconds")
    print("-" * 40)
    print(f"TOTAL WORKFLOW TIME:          {total_duration:6.2f} seconds")
    print("="*60)
    
    # Show output location
    import glob
    output_files = glob.glob(f"{output_dir}/final_mapped_*.xlsx")
    if output_files:
        print(f"\n✅ SUCCESS! Output file created:")
        print(f"   {output_files[0]}")
        
        # Check if we achieved 100% coverage
        report_files = glob.glob(f"{output_dir}/*_COMPREHENSIVE_REPORT.txt")
        if report_files:
            with open(report_files[0], 'r') as f:
                for line in f:
                    if "Coverage:" in line:
                        print(f"\n📈 {line.strip()}")
                        break
    else:
        print("\n❌ No output file was created!")


if __name__ == "__main__":
    main()